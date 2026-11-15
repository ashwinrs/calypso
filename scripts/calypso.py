#!/usr/bin/env python3
"""Terminal commands for the Calypso podcast workflow."""
import argparse
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory


LAYOUTS = ("original", "speaker", "diagram", "combined")
ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]*")


def run(*command, capture=False):
    return subprocess.run(command, check=True, text=True, capture_output=capture).stdout


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def probe(path):
    return json.loads(run(
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path), capture=True,
    ))


def doctor(args):
    tools = ["ffmpeg", "ffprobe", "whisper-cli", "excalidraw"]
    missing = False
    for tool in tools:
        location = shutil.which(tool)
        print(f"{tool}: {location or 'missing'}")
        missing |= location is None
    model_ready = args.model is not None and args.model.is_file()
    print(f"Whisper model: {args.model if model_ready else 'set --model or CALYPSO_WHISPER_MODEL'}")
    return int(missing or not model_ready)


def transcribe(args):
    if args.model is None or not args.model.is_file():
        raise ValueError("Provide a local Whisper model with --model or CALYPSO_WHISPER_MODEL.")
    # A new directory prevents overwrites, including concurrent transcription runs.
    args.work.mkdir(parents=True)
    info = probe(args.source)
    audio_streams = [stream for stream in info["streams"] if stream["codec_type"] == "audio"]
    if args.audio_track >= len(audio_streams):
        raise ValueError(f"Audio track {args.audio_track} is unavailable.")
    audio = audio_streams[args.audio_track]
    source_start = float(info["format"].get("start_time", 0))
    audio_start = float(audio.get("start_time", source_start))
    delay_ms = max(0, round((audio_start - source_start) * 1000))
    wav = args.work / "dialogue.wav"
    filters = ["aresample=16000:async=1", f"adelay={delay_ms}:all=1"]
    run("ffmpeg", "-v", "warning", "-n", "-i", str(args.source),
        "-map", f"0:a:{args.audio_track}", "-af", ",".join(filters),
        "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav))
    run("whisper-cli", "-m", str(args.model), "-f", str(wav), "-l", args.language,
        "-oj", "-osrt", "-of", str(args.work / "transcript"))
    print(args.work / "transcript.json")


def seconds(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Timestamps must be numeric seconds.")
    if not math.isfinite(value) or value < 0:
        raise ValueError("Timestamps must be finite and nonnegative.")
    return value


def interval(row):
    start, end = seconds(row["start"]), seconds(row["end"])
    if start >= end:
        raise ValueError("Each interval must have start < end.")
    return start, end


def candidates(path):
    items = read_json(path)["clips"]
    result = {}
    for item in items:
        key = item["id"]
        if not ID.fullmatch(key) or key in result:
            raise ValueError(f"Invalid or duplicate clip ID: {key!r}")
        interval(item)
        result[key] = item
    return result


def list_clips(args):
    for key, clip in candidates(args.plan).items():
        print(f"{key}\t{clip['start']:.3f}–{clip['end']:.3f}s\t{clip['title']}")
        if clip.get("reason"):
            print(f"  {clip['reason']}")


def create_diagram(args):
    if args.output.suffix.lower() != ".png":
        raise ValueError("Diagram output must end in .png.")
    scene = args.output.with_suffix(".excalidraw")
    outputs = [args.output, scene] if args.source.suffix.lower() == ".mmd" else [args.output]
    if any(output.exists() for output in outputs):
        raise ValueError("Choose a new diagram output path.")
    if args.source.suffix.lower() == ".mmd":
        run("excalidraw", "mermaid", str(args.source), "--out", str(scene))
    elif args.source.suffix.lower() == ".excalidraw":
        scene = args.source
    else:
        raise ValueError("Use a .mmd or .excalidraw source.")
    run("excalidraw", "render", str(scene), "--out", str(args.output))
    print(scene)
    print(args.output)


def fit(width, height, background="black"):
    return (f"scale={width}:{height}:force_original_aspect_ratio=decrease:"
            "force_divisible_by=2:reset_sar=1,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color={background},setsar=1")


def speaker_filters(framing, start, end, height, width_limit, height_limit):
    seats = framing["crops"]
    previous_end = 0
    ranges = {}
    for turn in framing["turns"]:
        left, right = interval(turn)
        if left < previous_end:
            raise ValueError("Speaker turns must be sorted and nonoverlapping.")
        previous_end = right
        seat = turn["speaker"]
        if seat not in seats:
            raise ValueError(f"No crop for speaker {seat!r}.")
        if left < end and right > start:
            ranges.setdefault(seat, []).append((max(left, start) - start, min(right, end) - start))
    filters = [f"[0:v:0]{fit(1080, height)}[shot0]"]
    for index, (seat, spans) in enumerate(ranges.items(), 1):
        x, y, width, crop_height = seats[seat]
        values = [x, y, width, crop_height]
        if (any(type(n) is not int or n < 0 or n % 2 for n in values)
                or width == 0 or crop_height == 0
                or x + width > width_limit or y + crop_height > height_limit):
            raise ValueError(f"Invalid crop for {seat!r}. Use even pixel coordinates within the source.")
        filters.append(
            f"[0:v:0]crop={width}:{crop_height}:{x}:{y},{fit(1080, height)}[seat{index}]"
        )
        enable = "+".join(f"gte(t,{left:.6f})*lt(t,{right:.6f})" for left, right in spans)
        filters.append(
            f"[shot{index - 1}][seat{index}]overlay=enable='{enable}'[shot{index}]"
        )
    return filters, f"shot{len(ranges)}"


def render(args):
    clips = candidates(args.plan)
    if args.id not in clips:
        raise ValueError(f"Unknown clip ID: {args.id}")
    clip = clips[args.id]
    start, end = interval(clip)
    info = probe(args.source)
    if end > float(info["format"]["duration"]) + 0.001:
        raise ValueError("Clip extends past the source duration.")
    if args.output.suffix.lower() != ".mp4" or args.output.exists():
        raise ValueError("Choose a new .mp4 output path.")

    uses_diagram = args.layout in ("diagram", "combined")
    if uses_diagram and not (args.diagram and args.diagram.is_file()):
        raise ValueError("Provide an existing diagram PNG with --diagram.")
    if args.layout == "speaker" and args.framing is None:
        raise ValueError("Provide crop and speaker turns with --framing.")
    if args.framing and args.layout not in ("speaker", "combined"):
        raise ValueError("--framing applies to speaker and combined layouts.")

    command = ["ffmpeg", "-v", "warning", "-n", "-ss", str(start), "-i", str(args.source)]
    if uses_diagram:
        command += ["-loop", "1", "-framerate", "30", "-i", str(args.diagram)]

    if args.layout == "diagram":
        filters = [f"[1:v:0]{fit(1080, 1920, 'white')}[video]"]
        video = "video"
    else:
        height = 960 if args.layout == "combined" else 1920
        if args.framing:
            source_video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
            if any(float(side.get("rotation", 0)) % 360
                   for side in source_video.get("side_data_list", [])):
                raise ValueError("Normalize the source rotation before defining speaker crops.")
            filters, video = speaker_filters(
                read_json(args.framing), start, end, height,
                source_video["width"], source_video["height"],
            )
        else:
            video = "shot"
            filters = [f"[0:v:0]{fit(1080, height)}[shot]"]
        if args.layout == "combined":
            filters += [
                f"[1:v:0]{fit(1080, 960, 'white')}[diagram]",
                f"[{video}][diagram]vstack=shortest=1[video]",
            ]
            video = "video"

    # Encode in a temporary directory on the destination filesystem. Linking
    # exposes only a complete result and fails if another run claimed the path.
    with TemporaryDirectory(prefix=".calypso-", dir=args.output.parent) as temp:
        output = Path(temp) / "clip.mp4"
        run(*command, "-t", str(end - start), "-filter_complex", ";".join(filters),
            "-map", f"[{video}]", "-map", f"0:a:{args.audio_track}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
            "-movflags", "+faststart", str(output))
        streams = probe(output)["streams"]
        if not any(s["codec_name"] == "h264" and (s["width"], s["height"]) == (1080, 1920)
                   for s in streams) or not any(s["codec_name"] == "aac" for s in streams):
            raise ValueError("Render did not produce the expected video and audio streams.")
        os.link(output, args.output)
    print(args.output)


def nonnegative_int(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be nonnegative")
    return number


def model_argument(parser):
    parser.add_argument("--model", type=Path, default=os.environ.get("CALYPSO_WHISPER_MODEL"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    command = commands.add_parser("doctor", help="check local runtime dependencies")
    model_argument(command)
    command.set_defaults(action=doctor)

    command = commands.add_parser("transcribe", help="produce a timestamped local transcript")
    command.add_argument("source", type=Path)
    command.add_argument("work", type=Path, help="new directory for transcription artifacts")
    command.add_argument("--audio-track", type=nonnegative_int, default=0)
    command.add_argument("--language", default="auto")
    model_argument(command)
    command.set_defaults(action=transcribe)

    command = commands.add_parser("list", help="show clip IDs and source time ranges")
    command.add_argument("plan", type=Path)
    command.set_defaults(action=list_clips)

    command = commands.add_parser("diagram", help="render Mermaid or Excalidraw to PNG")
    command.add_argument("source", type=Path)
    command.add_argument("output", type=Path)
    command.set_defaults(action=create_diagram)

    command = commands.add_parser("render", help="export a selected clip ID to vertical MP4")
    command.add_argument("source", type=Path)
    command.add_argument("plan", type=Path)
    command.add_argument("id")
    command.add_argument("output", type=Path)
    command.add_argument("--layout", choices=LAYOUTS, default="original")
    command.add_argument("--diagram", type=Path)
    command.add_argument("--framing", type=Path)
    command.add_argument("--audio-track", type=nonnegative_int, default=0)
    command.set_defaults(action=render)

    args = parser.parse_args()
    try:
        return args.action(args) or 0
    except (OSError, ValueError, KeyError, TypeError, StopIteration, subprocess.CalledProcessError) as exc:
        print(f"calypso: {getattr(exc, 'stderr', None) or str(exc) or type(exc).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
