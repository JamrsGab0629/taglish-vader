"""
collect.py - build my_reviews.csv (just the review text, no star ratings).

my_reviews.csv is always saved NEXT TO THIS FILE (the VADER folder), no matter
which folder you run the command from, so run.py finds it automatically.

Usage:
    python collect.py --import clean.txt     # a text file, one review per line
    python collect.py                        # type them one by one
Duplicates are skipped automatically, so you can keep adding batches.
"""

import argparse
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "my_reviews.csv")


def load_existing(path):
    if not os.path.exists(path):
        return set()
    with open(path, newline="", encoding="utf-8-sig") as f:
        return {(r.get("review") or "").strip().lower() for r in csv.DictReader(f)}


def save(reviews, path=OUT):
    """Append new reviews (list of text). Returns (added, skipped_duplicates)."""
    seen = load_existing(path)
    fresh = []
    for review in reviews:
        review = review.strip()
        key = review.lower()
        if key and key not in seen:
            seen.add(key)
            fresh.append(review)

    width = 1
    new_file = not os.path.exists(path) or os.path.getsize(path) == 0
    if not new_file:                      # keep any extra columns (e.g. human_label) aligned
        with open(path, newline="", encoding="utf-8-sig") as f:
            header = next(csv.reader(f), ["review"])
        width = max(len(header), 1)
    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["review"])
        for r in fresh:
            w.writerow([r] + [""] * (width - 1))
    return len(fresh), len(reviews) - len(fresh)


def from_file(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def interactive():
    rows = []
    while True:
        review = input("Review (blank to finish): ").strip()
        if not review:
            break
        rows.append(review)
    return rows


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--import", dest="src", help="text file of reviews, one per line")
    args = p.parse_args()
    rows = from_file(args.src) if args.src else interactive()
    added, skipped = save(rows)
    print(f"Added {added}, skipped {skipped} duplicates -> {OUT}")
