"""
tidy_csv.py - clean a my_reviews.csv you already made (video lengths like 0:12,
'helpful? profile', hidden characters, "Sound quality:" style labels, empty rows,
duplicates). A backup is saved first.

Usage:  python tidy_csv.py my_reviews.csv
"""

import csv
import shutil
import sys

from clean_paste import tidy

path = sys.argv[1] if len(sys.argv) > 1 else "my_reviews.csv"
backup = path.rsplit(".", 1)[0] + "_backup.csv"
shutil.copyfile(path, backup)

with open(path, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

seen, out, dropped = set(), [], 0
for r in rows:
    text = tidy(r["review"])
    key = text.lower()
    if len(text) < 2 or key in seen:
        dropped += 1
        continue
    seen.add(key)
    out.append({"review": text, "rating": r["rating"]})

with open(path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["review", "rating"])
    w.writeheader()
    w.writerows(out)

print(f"{len(rows)} rows -> {len(out)} kept, {dropped} removed. Backup: {backup}")
