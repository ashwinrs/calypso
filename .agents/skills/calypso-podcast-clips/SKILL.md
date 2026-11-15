---
name: calypso-podcast-clips
description: Turn local podcast recordings into reviewable short clips through the terminal. Use for a step-by-step walkthrough, timestamped local transcription, episode context, story arcs, candidate selection, active-speaker framing, Excalidraw explainers, or vertical video export in Calypso.
---

# Calypso podcast clips

Run `./scripts/calypso.py` from the repository root. Use the [README](../../../README.md) for CLI syntax and JSON examples. Preserve the source and keep intermediate files under `work/`.

For a guided run, give one actionable step at a time and explain how to verify the result. Provide commands using the user's actual paths when they want to run the steps themselves. Carry out authorized CLI steps when they ask Codex to run them. Resume from the latest verified artifact for that source.

## Find the recording and transcribe

Use the supplied source path, or ask for it if the recording is unclear. Probe the available audio streams and choose the dialogue track. Prefer the local Whisper large-v3-turbo and Silero workflow in [Yogurt-inspired context](references/yogurt-context.md) when the models are available. The standard `transcribe` command works with a configured Whisper model or `--model models/ggml-base.bin` when that file exists. Reuse a verified transcript for the same source when its quality is sufficient. Confirm the JSON contains usable dialogue and source-relative timestamps.

If Whisper's Metal backend or Excalidraw's Chrome launch fails in the Codex sandbox, retry with appropriate access or provide the command for the user's regular terminal. Use a fresh work directory if the failed transcription already created one.

## Build episode context

Use the local notes pass in [Yogurt-inspired context](references/yogurt-context.md). Map the whole episode before proposing edits. Link topics and callbacks to timestamped transcript rows. Preserve what was proposed, disputed, or hypothetical. Check the notes against the transcript and keep speaker attribution uncertain when the audio is mixed. Check nearby lines and sample frames where meaning depends on something onscreen.

## Propose complete stories

Start with the message a viewer should take away. Find the hook or question, the minimum context to follow it, and the explanation and payoff. Flag promising arcs even when they span several minutes or when the answer comes much later. Keep source order unless the user requests a different structure and the resulting edit preserves meaning.

For a multi-part story, save a separate `story-arcs.json` with a stable ID, title, takeaway, full source span, ordered nonoverlapping keep ranges, cut ranges with reasons, estimated edited duration, and any joins that need a short visual bridge. Use source-relative seconds and record transcript row IDs for each keep range. Cut repetition, tangents, and dead air while retaining caveats and necessary setup. Compare the lines on both sides of each proposed join and mark unclear joins for an audio preview. Present the source span and estimated edited duration so the user can judge the difference.

Include shorter contiguous clips when they deliver a complete point. Save those in `clips.json` and use `list` to present them. The current `render` command accepts one continuous interval per ID. Use a separate rough-cut step for selected multi-part edits and preview joins before treating the edit as final. Ask for clip IDs and any missing layout choices. Render the selections the user approves.

## Prepare framing and diagrams

- **Full shot** uses `original`.
- **Speaker only** uses `speaker` with `--framing`.
- **Diagram only** uses `diagram` with `--diagram` and keeps the source audio.
- **Both** uses `combined` with `--diagram`. Add `--framing` for speaker crops or omit it to show the full shot above the diagram.

For a fixed two-shot, inspect full-resolution source frames and assign a crop to each seat. Build sorted, nonoverlapping speaker turns in source-relative seconds from isolated mics, manual review, or local [pyannote.audio Community-1](https://github.com/pyannote/pyannote-audio) after model setup. Confirm the seat for each speaker label, hold the crop through brief interjections as appropriate, and leave gaps for uncertain turns or shared reactions. For a moving camera, a detector such as [TalkNet](https://github.com/TaoRuijie/TalkNet-ASD) requires a separate integration and validation on the footage.

For multi-step explanations, derive nodes and arrows from the selected excerpt or use the user's Excalidraw scene. Run `diagram` to produce a PNG and retain the editable scene. Preview labels at phone size.

## Verify exports

Run or provide one `render` command per selected ID and layout, with a distinct output path. Check the output duration, dimensions, codecs, and audio with ffprobe. Preview starts, ends, and crop transitions for sync, intact words, and readable framing. Report the output paths and candidate IDs. In a guided run, show how to retry a clip with adjusted boundaries or a different layout if the user wants changes.
