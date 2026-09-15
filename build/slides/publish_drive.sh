#!/usr/bin/env bash
# Drive half of deck publishing. Run on the owner's Mac (rclone remote iisd-drive).
#   bash build/slides/publish_drive.sh 1sw-wk3 "SW1 · Wk3 Computer Science IT"
# Google Masters/ gets each deck converted to Google Slides; Download Releases/ keeps the .pptx.
# Writes gslides_url and pptx_drive_url into build/slides/slides_registry.json (merged per day).
set -euo pipefail
export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH
WEEK="$1"; UNIT="$2"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BASEDIR="iisd-drive:VILS27/Units_CCR/$UNIT"
SRC="$ROOT/docs/resources/slides"
REG="$ROOT/build/slides/slides_registry.json"
[ -f "$REG" ] || echo '{"days":{}}' > "$REG"
for f in "$SRC"/${WEEK}-day*.pptx; do
  name="$(basename "$f")"; n="${name: -6:1}"
  sw="${WEEK:0:1}"; wk="${WEEK#*-wk}"; key="${sw}SW-Wk${wk}-Day${n}"
  rclone copyto "$f" "$BASEDIR/Download Releases/$name"
  rclone copyto --drive-import-formats pptx "$f" "$BASEDIR/Google Masters/${name%.pptx}"
  gid="$(rclone lsjson "$BASEDIR/Google Masters" | python3 -c "import json,sys;print(next(x['ID'] for x in json.load(sys.stdin) if x['Name']=='${name%.pptx}'))")"
  pid="$(rclone lsjson "$BASEDIR/Download Releases" | python3 -c "import json,sys;print(next(x['ID'] for x in json.load(sys.stdin) if x['Name']=='$name'))")"
  python3 - "$REG" "$key" "$gid" "$pid" <<'EOF'
import json,sys
reg,key,gid,pid=sys.argv[1:]
d=json.load(open(reg)); e=d["days"].setdefault(key,{})
e["gslides_url"]=f"https://docs.google.com/presentation/d/{gid}/edit"
e["pptx_drive_url"]=f"https://drive.google.com/file/d/{pid}/view"
json.dump(d,open(reg,"w"),indent=1)
print(key,e["gslides_url"])
EOF
done
