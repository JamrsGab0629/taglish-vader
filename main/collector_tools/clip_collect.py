"""
clip_collect.py - watches your clipboard. Every time you copy a Shopee reviews page,
it pulls out ONLY the reviews and adds them to my_reviews.csv, ready for main.py.
It only reads your own clipboard. It never contacts any website.

Usage:  python clip_collect.py --rating 5
        python clip_collect.py --rating 1 --csv C:\\path\\to\\taglish_vader\\my_reviews.csv

--rating is the star filter you have selected in the browser (1-5).
Keep this file in the same folder as clean_paste.py and collect.py.
Also saves each raw copied page to raw_pages_<rating>star.txt, so you can re-clean
it later with clean_paste.py if you ever change the rules.
Needs:  pip install pyperclip       (Ctrl+C in this terminal to stop)
"""

import argparse
import time

from clean_paste import DATE_LINE, PAGE_MARK, extract_by_date, page_chrome
from collect import save


def process_page(text, rating, csv_path, history, raw_path):
    """Extract the reviews from one copied page and append them to the CSV.
    Returns (status, added, skipped)."""
    if not any(DATE_LINE.match(line.strip()) for line in text.splitlines()):
        return "no review dates found - skipped (is this the reviews page?)", 0, 0
    if history and history[-1] == text:
        return "same page as the last copy - skipped", 0, 0
    history.append(text)
    with open(raw_path, "a", encoding="utf-8") as f:
        f.write(text + "\n" + PAGE_MARK + "\n")
    chrome = page_chrome(history)          # menus/product info (needs 3+ pages to learn)
    reviews, _ = extract_by_date([text], chrome)
    added, skipped = save([(r, str(rating)) for r in reviews], csv_path)
    return "ok", added, skipped


def main():
    ap = argparse.ArgumentParser(description="Copy a reviews page -> reviews land in the CSV")
    ap.add_argument("--rating", type=int, choices=[1, 2, 3, 4, 5], required=True,
                    help="the star filter you are copying from")
    ap.add_argument("--csv", default="my_reviews.csv", help="where the reviews go")
    a = ap.parse_args()

    import pyperclip
    raw_path = f"raw_pages_{a.rating}star.txt"
    last = pyperclip.paste()
    history, pages, total = [], 0, 0
    print(f"Watching clipboard. {a.rating}-star reviews -> {a.csv}")
    print("Copy a reviews page (Ctrl+A, Ctrl+C or F8). Press Ctrl+C here to stop.")
    while True:
        try:
            text = pyperclip.paste()
            if text != last and len(text) > 20:
                last = text
                status, added, skipped = process_page(text, a.rating, a.csv, history, raw_path)
                if status == "ok":
                    pages += 1
                    total += added
                    print(f"page {pages}: +{added} reviews ({skipped} duplicates skipped) -> {a.csv}")
                else:
                    print(status)
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
    print(f"\nDone. {total} new {a.rating}-star reviews added to {a.csv}")


if __name__ == "__main__":
    main()
