brew install whisper.cpp
npm install -g @excalidraw/cli

mkdir -p models
curl -fL https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin \
  -o models/ggml-base.bin
export CALYPSO_WHISPER_MODEL="$PWD/models/ggml-base.bin"

./scripts/calypso.py doctor