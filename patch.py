#!/usr/bin/env python3

import os
from pathlib import Path

ROOT = Path.cwd()

KEYWORDS = [
    "vibration",
    "sound_db",
    "device_id",
    "zone",
]

EXTENSIONS = {
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".json",
    ".sql",
    ".prisma",
}

print(f"\nScanning project: {ROOT}\n")

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue

    if path.suffix not in EXTENSIONS:
        continue

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue

    matches = []

    for kw in KEYWORDS:
        if kw in text:
            matches.append(kw)

    if matches:
        print("=" * 80)
        print(path)
        print("Found:", ", ".join(matches))

        lines = text.splitlines()

        for i, line in enumerate(lines, start=1):
            if any(kw in line for kw in matches):
                print(f"{i:4d}: {line}")

print("\nDone.")
