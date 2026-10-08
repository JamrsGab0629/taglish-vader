"""
collect.py - build my_reviews.csv from reviews you collected yourself.

Usage:
    python collect.py --import five_star_clean.txt --rating 5   # whole file = one rating
    python collect.py --import notes.txt                        # lines like:  5 | Ang ganda!
    python collect.py                                           # type them one by one
Duplicates are skipped automatically, so you can keep adding batches.
"""

import argparse
import csv
import os

OUT = "my_reviews.csv"
VALID = {"1", "2", "3", "4", "5"}


def load_existing(path):
    if not os.path.exists(path):
        return set()
    with open(path, newline="", encoding="utf-8-sig") as f:
        return {r["review"].strip().lower() for r in csv.DictReader(f)}


def save(rows, path=OUT):
    seen = load_existing(path)
    fresh = []
    for review, rating in rows:
        key = review.strip().lower()
        if key and key not in seen:
            seen.add(key)
            fresh.append((review.strip(), rating))
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["review", "rating"])
        w.writerows(fresh)
    return len(fresh), len(rows) - len(fresh)


def from_file(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if "|" not in line:
                continue
            rating, review = line.split("|", 1)
            if rating.strip() in VALID:
                rows.append((review.strip(), rating.strip()))
    return rows


def from_bulk(path, rating):
    with open(path, encoding="utf-8") as f:
        return [(line.strip(), rating) for line in f if line.strip()]


def interactive():
    rows = []
    while True:
        review = input("Review (blank to finish): ").strip()
        if not review:
            break
        rating = input("Rating 1-5: ").strip()
        if rating not in VALID:
            print("Rating must be 1-5, try again.")
            continue
        rows.append((review, rating))
    return rows


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--import", dest="src", help="text file of reviews")
    p.add_argument("--rating", choices=sorted(VALID),
                   help="give every line in the --import file this rating")
    args = p.parse_args()
    if args.src and args.rating:
        rows = from_bulk(args.src, args.rating)
    elif args.src:
        rows = from_file(args.src)
    else:
        rows = interactive()
    added, skipped = save(rows)
    print(f"Added {added}, skipped {skipped} duplicates -> {OUT}")
