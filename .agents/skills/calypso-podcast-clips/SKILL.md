---
name: calypso-podcast-clips
description: Turn local podcast recordings into reviewable short clips through the terminal. Use for timestamped local transcription, episode analysis, candidate selection, active-speaker framing, Excalidraw explainers, or vertical video export in Calypso.
---

# Calypso podcast clips

Run `./scripts/calypso.py` from the repository root. Read the relevant section of `README.md` for commands and JSON formats. Use `doctor` to check dependencies and `transcribe` for on-device speech recognition. Probe the media before choosing the dialogue track. Keep source files intact and save intermediate media under `work/`.

## Prepare a shortlist

Read the timestamped transcript in order. For long episodes, summarize successive sections and consolidate topics and dependencies before suggesting clips. Check nearby lines and sample frames where a speaker refers to something onscreen.

Choose excerpts with a self-contained question or claim, a useful explanation, and a payoff. Preserve important qualifiers. Align boundaries to complete phrases and check them against the source. Write a `clips.json` with stable IDs, source-relative timestamps in seconds, titles, and reasons. Use `list` to present the options and describe which framing fits each clip. Render only the IDs the user selects.

## Prepare framing and diagrams

For a fixed two-shot, inspect full-resolution source frames and assign a crop to each seat. Build sorted, nonoverlapping speaker turns in source-relative seconds from isolated mics, manual review, or local [pyannote.audio Community-1](https://github.com/pyannote/pyannote-audio) after model setup. Confirm the seat for each speaker label, hold the crop through brief interjections as appropriate, and leave gaps for uncertain turns or shared reactions. For a moving camera, a detector such as [TalkNet](https://github.com/TaoRuijie/TalkNet-ASD) requires a separate integration and validation on the footage.

For multi-step explanations, derive nodes and arrows from the selected excerpt or use the user's Excalidraw scene. Run `diagram` to produce a PNG and retain the editable scene. Preview labels at phone size. Use `combined` with framing to place the active speaker above the diagram. Use `diagram` to show the diagram alone with source audio.

## Verify exports

Run `render` with the selected ID and layout. Check the output duration, dimensions, codecs, and audio with ffprobe. Preview starts, ends, and crop transitions for sync, intact words, and readable framing. Report the output paths and candidate IDs.
