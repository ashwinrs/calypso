# Yogurt-inspired context

Use Yogurt's approach of local speech recognition followed by whole-episode notes. Calypso starts with a prerecorded source and keeps source-relative times for editing. This workflow can reuse local model files from an existing Yogurt install or accept equivalent paths on another machine. The desktop app does not need to be running. [Yogurt ASR](https://github.com/FrigadeHQ/yogurt/blob/efdba7c930941fe920da7f3ad33dad5cab991da1/app/src/main/asr/transcribe.ts) · [Yogurt notes pipeline](https://github.com/FrigadeHQ/yogurt/blob/efdba7c930941fe920da7f3ad33dad5cab991da1/app/src/main/notes/enhance.ts)

## Get a timestamped transcript

Prefer Whisper large-v3-turbo with Silero VAD. On macOS, look under `~/Library/Application Support/Yogurt/models/asr/` for the Whisper model and under `/Applications/Yogurt.app/Contents/Resources/vad/` for the VAD model. The tested files were `ggml-large-v3-turbo-q5_0.bin` and `ggml-silero-v6.2.0.bin`. Work with whichever paths actually exist. Use the standard Calypso transcription step to generate `dialogue.wav` with source-aligned timing, or reuse that file from a confirmed run. When the larger models are present, run the following with the existing WAV and a fresh output prefix. Use the known spoken language in place of `auto` if appropriate.

```sh
whisper-cli -m "$whisper_model" -f "$dialogue_wav" -l auto \
  --vad -vm "$vad_model" -oj -osrt -of "$transcript_prefix"
```

If only the larger Whisper model is available, use it without the VAD flags. If it is unavailable, use the configured local Whisper model and check unclear names or candidate boundaries against the audio.

## Map the whole episode

Prefer a local `llama-cli` notes pass with Yogurt's installed notes model when available. The tested machine used `gemma-4-E4B_q4_0-it.gguf` under `~/Library/Application Support/Yogurt/models/llm/`. Other machines can use their configured local GGUF model. Give transcript rows stable sequential IDs and keep the ID-to-timestamp mapping from the original JSON. Put the transcript before the instructions in the prompt. Ask for topic notes that cover the whole episode with row IDs, concrete examples, and open questions or caveats. If it exceeds the model's context window, summarize chronological chunks at row boundaries, then consolidate the notes while retaining citations to the original rows.

```sh
llama-cli -m "$notes_model" -f "$context_prompt" --single-turn \
  --simple-io --no-display-prompt -c "$context_size" -n "$output_tokens" </dev/null
```

Choose context and output budgets for the loaded model. Check for early truncation, unsupported attributions, and claims that the speakers describe as uncertain. Use the notes to find connections and validate them in the original transcript before proposing keep ranges. If the local notes runtime or model is unavailable, identify that when offering in-session transcript analysis. Ask before using in-session analysis if the user has specified that transcript processing must stay local.
