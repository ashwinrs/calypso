---
name: calypso-podcast-clips
description: Turn local podcast recordings into reviewable short clips through the terminal. Use for a step-by-step walkthrough, timestamped local transcription, episode context, story arcs, candidate selection, active-speaker framing, Excalidraw explainers, or vertical video export in Calypso.
---

# Calypso podcast clips

Run `./scripts/calypso.py` from the repository root. Use the [README](../../../README.md) for CLI syntax and JSON examples. Preserve the source and keep intermediate files under `work/`.

For a guided run, give one actionable step at a time and explain how to verify the result. Provide commands using the user's actual paths when they want to run the steps themselves. Carry out authorized CLI steps when they ask Codex to run them. Resume from the latest verified artifact for that source.

## Confirm choices before implementing

When more than one viable approach exists for a step, ask the user to choose before committing to that approach in an edit plan, script, CLI command, or export. Give the options, recommend one, and explain the practical tradeoff. The recommended default is the first option to present. Use choices the user has already confirmed for the clip, and pause only the work that depends on an open choice. Continue inspecting the source or gathering evidence while waiting. If the source or a tool constraint leaves only one viable path, explain the constraint before proceeding.

Apply this to transcription and context methods, story structure and cuts, audio and transitions, how speaker turns are identified or handled when unclear, diagram placement and timing, and whether to reuse the Calypso CLI or write a custom edit script. Verify cut points and crop bounds from the source. Ask about any missing input or unresolved decision that would otherwise require an assumption.

## Find the recording and transcribe

Use the supplied source path, or ask for it if the recording is unclear. Probe the available audio streams and choose the dialogue track. Recommend the local Whisper large-v3-turbo and Silero workflow in [Yogurt-inspired context](references/yogurt-context.md) when the models are available. The standard `transcribe` command works with a configured Whisper model or `--model models/ggml-base.bin` when that file exists. Reuse a verified transcript for the same source when its quality is sufficient. Confirm the JSON contains usable dialogue and source-relative timestamps.

If Whisper's Metal backend or Excalidraw's Chrome launch fails in the Codex sandbox, retry with appropriate access or provide the command for the user's regular terminal. Use a fresh work directory if the failed transcription already created one.

## Build episode context

Use the local notes pass in [Yogurt-inspired context](references/yogurt-context.md). Map the whole episode before proposing edits. Link topics and callbacks to timestamped transcript rows. Preserve what was proposed, disputed, or hypothetical. Check the notes against the transcript and keep speaker attribution uncertain when the audio is mixed. Check nearby lines and sample frames where meaning depends on something onscreen.

## Propose complete stories

Start with the message a viewer should take away. Find the hook or question, the minimum context to follow it, and the explanation and payoff. Flag promising arcs even when they span several minutes or when the answer comes much later. Keep source order unless the user requests a different structure and the resulting edit preserves meaning.

For a multi-part story, save a separate `story-arcs.json` with a stable ID, title, takeaway, full source span, ordered nonoverlapping keep ranges, cut ranges with reasons, estimated edited duration, and any joins that need a short visual bridge. Use source-relative seconds and record transcript row IDs for each keep range. Cut repetition, tangents, and dead air while retaining caveats and necessary setup. Compare the lines on both sides of each proposed join and mark unclear joins for an audio preview. Present the source span and estimated edited duration so the user can judge the difference.

Include shorter contiguous clips when they deliver a complete point. Save those in `clips.json` and use `list` to present them. The current `render` command accepts one continuous interval per ID. Use a separate rough-cut step for selected multi-part edits and preview joins before treating the edit as final. Ask for clip IDs and any missing layout choices. Render the selections the user approves.

## Request host-recorded narration

Use the original dialogue and host-recorded pickups for spoken audio. Keep synthesized or cloned voices out of rough cuts and final exports unless the user explicitly changes this preference.

When an opening, transition, or factual correction needs new speech, give the host exact copy for each pickup, where it goes, an estimated duration, and a distinct filename or take label. Accept short separate recordings or one recording with clear pauses between takes. Prepare the edit and visuals while the host records. Use silent text cards for any interim preview that needs missing pickups.

When the recordings arrive, match each take to its cue, remove excess silence, level it against the podcast dialogue, and adjust card timing to fit the recorded delivery. Check the joins and confirm that the export contains only original dialogue and the host's recorded pickups.

## Prepare framing and diagrams

For a vertical clip with a diagram, recommend the approved layout first: crop to the active speaker, place that crop in the upper part of the frame, and reserve the lower part for a large diagram. Show the left host while they speak and switch to the right host when they take a turn. Determine left and right from this recording's frames and dialogue. Offer diagram below or above the host when either arrangement is viable and confirm the placement. Ask what should fill the diagram area when the diagram is offscreen if the clip does not use a diagram throughout.

- **Speaker above diagram** uses `render --layout combined --framing <turns.json> --diagram <diagram.png>` when a single interval and a static diagram fit. Check the text at phone size.
- **Timed diagram or multi-part edit** can use a dedicated render script if the CLI cannot express the approved timing or layout. Keep the same speaker-above-diagram framing when approved. Record the chosen crop, layout, and diagram cues in the edit plan. Convert source-relative cue times to the edited timeline after accounting for cuts and cards.
- **Other layouts** use `speaker` with `--framing` for a speaker-only crop, `original` for a full shot, or `diagram` with `--diagram` for diagram-only video with source audio. A full shot above a diagram is available through `combined` without `--framing`.

For a fixed two-shot, inspect full-resolution frames and frame each seat so the crop includes the host's face and shoulders. Build sorted, nonoverlapping speaker turns in source-relative seconds from an approved method, such as manual review, isolated mic tracks, or local [pyannote.audio Community-1](https://github.com/pyannote/pyannote-audio) after model setup. Confirm the seat for each speaker label. Ask how to handle uncertain turns, overlap, and brief interjections when those choices matter. Offer the full shot for uncertain turns when feasible. A moving-camera detector such as [TalkNet](https://github.com/TaoRuijie/TalkNet-ASD) requires separate integration and validation on the footage.

For multi-step explanations, derive nodes and arrows from the selected excerpt or use the user's Excalidraw scene. Run `diagram` to produce a PNG and retain the editable scene. Preview the speaker change and diagram cue together at phone size.

## Verify exports

Run or provide one `render` command per selected ID and layout, with a distinct output path. Check the output duration, dimensions, codecs, and audio with ffprobe. Preview starts, ends, and crop transitions for sync, intact words, and readable framing. Report the output paths and candidate IDs. In a guided run, show how to retry a clip with adjusted boundaries or a different layout if the user wants changes.
