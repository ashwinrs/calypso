---
name: calypso-podcast-clips
description: Turn local podcast recordings into reviewable short clips through the terminal. Use for a step-by-step walkthrough, timestamped local transcription, episode analysis, candidate selection, active-speaker framing, Excalidraw explainers, or vertical video export in Calypso.
---

# Calypso podcast clips

Run `./scripts/calypso.py` from the repository root. Use the [README](../../../README.md) for CLI syntax and JSON examples. Preserve the source and keep intermediate files under `work/`.

For a guided run, give one actionable step at a time and explain how to verify the result. Provide commands using the user's actual paths when they want to run the steps themselves. Carry out authorized CLI steps when they ask Codex to run them. Resume from the latest verified artifact for that source.

## Find the recording and transcribe

Use the source path the user supplies, or ask for it when the recording is unclear. Use `doctor` to check dependencies. Probe the source before choosing the dialogue track. Run `transcribe` in a new work directory using the configured model or `--model models/ggml-base.bin` when that file exists. Reuse a transcript from a confirmed earlier run of the same source when available. Confirm the timestamped JSON contains usable dialogue.

If Whisper's Metal backend or Excalidraw's Chrome launch fails in the Codex sandbox, provide the corresponding command for the user's regular terminal. Use a fresh transcription work directory if the failed run already created one.

## Prepare a shortlist

Read the timestamped transcript in order. For long episodes, summarize successive sections and consolidate topics and dependencies before suggesting clips. Check nearby lines and sample frames where a speaker refers to something onscreen.

Choose excerpts with a self-contained question or claim, a useful explanation, and a payoff. Preserve important qualifiers. Align boundaries to complete phrases and check them against the source. Write a `clips.json` with stable IDs, source-relative timestamps in seconds, titles, and reasons. Use `list` to present the options and describe which framing fits each clip. Ask for clip IDs and any missing layout choices. Render the IDs the user selects, including any selection they already supplied.

## Prepare framing and diagrams

- **Full shot** uses `original`.
- **Speaker only** uses `speaker` with `--framing`.
- **Diagram only** uses `diagram` with `--diagram` and keeps the source audio.
- **Both** uses `combined` with `--diagram`. Add `--framing` for speaker crops or omit it to show the full shot above the diagram.

For a fixed two-shot, inspect full-resolution source frames and assign a crop to each seat. Build sorted, nonoverlapping speaker turns in source-relative seconds from isolated mics, manual review, or local [pyannote.audio Community-1](https://github.com/pyannote/pyannote-audio) after model setup. Confirm the seat for each speaker label, hold the crop through brief interjections as appropriate, and leave gaps for uncertain turns or shared reactions. For a moving camera, a detector such as [TalkNet](https://github.com/TaoRuijie/TalkNet-ASD) requires a separate integration and validation on the footage.

For multi-step explanations, derive nodes and arrows from the selected excerpt or use the user's Excalidraw scene. Run `diagram` to produce a PNG and retain the editable scene. Preview labels at phone size.

## Verify exports

Run or provide one `render` command per selected ID and layout, with a distinct output path. Check the output duration, dimensions, codecs, and audio with ffprobe. Preview starts, ends, and crop transitions for sync, intact words, and readable framing. Report the output paths and candidate IDs. In a guided run, show how to retry a clip with adjusted boundaries or a different layout if the user wants changes.
