#!/usr/bin/env python3
"""Regenerate nkplay-names.json (playlist id -> {label, tracks}) from the local
m3u files and upload it next to the dashboard on the server.

The dashboard (nkplay-dash.py on the server) reads this JSON to show playlist
names instead of bare numbers. Run this whenever you add or change playlists.
"""
import glob
import json
import os
import re
import subprocess
import sys

MUSIC = "/Users/dmd/Library/CloudStorage/Dropbox-Personal/dashare/musicplayer"
REMOTE = "edges@3e.org:3e.org/private/nkplay-names.json"
OUT = "/tmp/nkplay-names.json"


def clean(s):
    # strip leading track numbers like "09 ", "2-04 ", "1 "
    return re.sub(r'^\d+[-\s]+', '', s).strip()


def label_for(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        tracks = [l.strip() for l in f if l.strip()]
    n = len(tracks)
    if n == 1:  # single track: use the song name (most descriptive)
        return clean(os.path.splitext(os.path.basename(tracks[0]))[0]), 1
    dirs = [d for d in (os.path.dirname(t) for t in tracks) if d and d != "."]
    label = None
    if dirs and len(set(dirs)) == 1:
        label = dirs[0]
    elif dirs:
        try:
            common = os.path.commonpath(dirs)
            label = common if common and common != "." else None
        except ValueError:
            label = None
    if not label and tracks:
        label = "mix: " + clean(os.path.splitext(os.path.basename(tracks[0]))[0])
    return label, n


def main():
    out = {}
    for path in glob.glob(os.path.join(MUSIC, "*.m3u")):
        pid = os.path.splitext(os.path.basename(path))[0]
        try:
            label, n = label_for(path)
        except Exception as e:
            print(f"  skip {pid}: {e}", file=sys.stderr)
            continue
        out[pid] = {"label": label or pid, "tracks": n}
    out.setdefault("999", {"label": "(shuffle all)", "tracks": 0})

    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(f"wrote {len(out)} playlists to {OUT}")

    subprocess.run(["scp", "-q", OUT, REMOTE], check=True)
    print(f"uploaded to {REMOTE}")


if __name__ == "__main__":
    main()
