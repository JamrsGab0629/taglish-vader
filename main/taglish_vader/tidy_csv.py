"""
tidy_csv.py - clean a my_reviews.csv you already made: removes the star-rating column,
the "Product: Poor quality, ..." form tags, video lengths like 0:12, "helpful? profile",
hidden characters, "Sound quality:" style labels, empty rows and duplicates.
A backup is saved first. Any other column (like human_label) is kept.

Usage:  python tidy_csv.py                 # the my_reviews.csv in this folder
        python tidy_csv.py other.csv
"""

import csv
import os
import shutil
import sys

from clean_paste import tidy

HERE = os.path.dirname(os.path.abspath(__file__))
DROP_COLUMNS = {"rating", "ratings", "stars", "star", "star_rating", "score"}

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "my_reviews.csv")
backup = path.rsplit(".", 1)[0] + "_backup.csv"
shutil.copyfile(path, backup)

with open(path, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fields = [c for c in (reader.fieldnames or []) if c.strip().lower() not in DROP_COLUMNS]

seen, out, dropped = set(), [], 0
for r in rows:
    text = tidy(r["review"])
    key = text.lower()
    if len(text) < 2 or key in seen:
        dropped += 1
        continue
    seen.add(key)
    row = {c: r.get(c, "") for c in fields}
    row["review"] = text
    out.append(row)

with open(path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(out)

print(f"{len(rows)} rows -> {len(out)} kept, {dropped} removed. Backup: {backup}")
