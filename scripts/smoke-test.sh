#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT

ffmpeg -v error -f lavfi \
  -i 'color=red:size=640x360:rate=30,drawbox=x=320:y=0:w=320:h=360:color=blue:t=fill' \
  -f lavfi -i 'sine=frequency=440' -t 2 -c:v libx264 -c:a aac "$scratch/source.mp4"
ffmpeg -v error -f lavfi -i 'color=white:size=320x180' \
  -frames:v 1 -update 1 "$scratch/diagram.png"
cat > "$scratch/clips.json" <<'JSON'
{"clips":[{"id":"example","start":0.2,"end":1.5,"title":"Example"}]}
JSON
cat > "$scratch/framing.json" <<'JSON'
{"crops":{"left":[0,0,320,360],"right":[320,0,320,360]},
 "turns":[{"speaker":"left","start":0,"end":0.7},
          {"speaker":"right","start":0.8,"end":2}]}
JSON
./scripts/calypso.py list "$scratch/clips.json"
render() {
  layout=$1
  shift
  ./scripts/calypso.py render "$scratch/source.mp4" "$scratch/clips.json" example \
    "$scratch/$layout.mp4" --layout "$layout" "$@"
  ffprobe -v error -show_entries format=duration -of csv=p=0 "$scratch/$layout.mp4" |
    awk '$1 >= 1.26 && $1 <= 1.34 {ok=1} END {exit !ok}'
}

render original
render speaker --framing "$scratch/framing.json"
render diagram --diagram "$scratch/diagram.png"
render combined --diagram "$scratch/diagram.png" --framing "$scratch/framing.json"

# Sample the opposite half of the full shot during each speaker turn.
# The 0.5–0.6s clip-relative gap should show both source colors.
pixel_is() {
  ffmpeg -v error -ss "$2" -i "$scratch/$1.mp4" \
    -vf "format=rgb24,crop=1:1:$3:$4" -frames:v 1 -f rawvideo - |
    python3 -c 'import sys; rgb = sys.stdin.buffer.read(); assert len(rgb) == 3 and rgb[int(sys.argv[1])] > 220 and sum(rgb) - rgb[int(sys.argv[1])] < 50, list(rgb)' "$5"
}
pixel_is speaker 0.20 700 960 0
pixel_is speaker 0.54 380 960 0
pixel_is speaker 0.54 700 960 2
pixel_is speaker 0.90 380 960 2
pixel_is combined 0.20 700 480 0
pixel_is combined 0.90 380 480 2
