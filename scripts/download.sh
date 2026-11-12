#!/usr/bin/env bash
# Download SEN12MS-CR into data/raw/.
# Per archive: download -> verify sha512 -> extract -> delete archive.
# Re-running is safe: extracted archives are skipped, partial downloads resume.
#
# Usage: scripts/download.sh                    # all four seasons (~292 GB download, ~480 GB extracted)
#        scripts/download.sh ROIs2017_winter    # one or more seasons
#        DEST=/mnt/vol/raw scripts/download.sh  # other destination
set -euo pipefail

DEST="${DEST:-data/raw}"
SERVER="rsync://m1554803@dataserv.ub.tum.de/m1554803"
export RSYNC_PASSWORD=m1554803

if [ $# -gt 0 ]; then
  SEASONS=("$@")
else
  SEASONS=(ROIs1158_spring ROIs1868_summer ROIs1970_fall ROIs2017_winter)
fi

mkdir -p "$DEST"
cd "$DEST"
echo "destination: $(pwd)  free: $(df -h . | awk 'NR==2 {print $4}')"
rsync -q "$SERVER/checksums.sha512" .

for s in "${SEASONS[@]}"; do
  for t in s1 s2 s2_cloudy; do
    name="${s}_${t}"
    if [ -f "$name/.done" ]; then
      echo "skip $name (already extracted)"
      continue
    fi
    echo "== $name"
    rsync -P --partial "$SERVER/$name.tar.gz" .
    grep " ./$name.tar.gz\$" checksums.sha512 | sed 's# \./# #' | sha512sum -c -
    tar xzf "$name.tar.gz"
    touch "$name/.done"
    rm "$name.tar.gz"
  done
done
echo "done"
