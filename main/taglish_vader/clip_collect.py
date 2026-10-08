"""
clip_collect.py - watches your clipboard. Every time you copy a Shopee reviews page,
it pulls out ONLY the review text and adds it to my_reviews.csv in the VADER folder.
It only reads your own clipboard. It never contacts any website.
No star ratings are saved: sentiment is decided later, from the text only.

Usage:  python clip_collect.py
        (or just run start_collecting.py, which does this AND the Next-button part)

Each raw copied page is also saved to raw_pages.txt (same folder), so you can
re-clean it later with clean_paste.py if you ever change the rules.
Needs:  pip install pyperclip       (Ctrl+C in this terminal to stop)
"""

import argparse
import os
import threading
import time

from clean_paste import DATE_LINE, PAGE_MARK, extract_by_date, page_chrome
from collect import OUT, save

HISTORY_PAGES = 30


def process_page(text, csv_path, history, raw_path):
    """Extract the reviews from one copied page and append them to the CSV.
    Returns (status, added, skipped)."""
    if not any(DATE_LINE.match(line.strip()) for line in text.splitlines()):
        return "no review dates found - skipped (is this the reviews page?)", 0, 0
    if history and history[-1] == text:
        return "same page as the last copy - skipped", 0, 0
    history.append(text)
    del history[:-HISTORY_PAGES]
    with open(raw_path, "a", encoding="utf-8") as f:
        f.write(text + "\n" + PAGE_MARK + "\n")
    chrome = page_chrome(history)          # menus/product info (needs 8+ pages to learn)
    reviews, _ = extract_by_date([text], chrome)
    added, skipped = save(reviews, csv_path)
    return "ok", added, skipped


def watch(csv_path=OUT, stop=None):
    """Watch the clipboard until `stop` is set (or Ctrl+C)."""
    import pyperclip

    stop = stop or threading.Event()
    raw_path = os.path.join(os.path.dirname(os.path.abspath(csv_path)), "raw_pages.txt")
    last = pyperclip.paste()
    history, pages, total = [], 0, 0
    print(f"Watching clipboard. Reviews -> {csv_path}")
    print("Copy a reviews page (Ctrl+A, Ctrl+C or F8/F10). Ctrl+C here to stop.")
    while not stop.is_set():
        try:
            text = pyperclip.paste()
            if text != last and len(text) > 20:
                last = text
                status, added, skipped = process_page(text, csv_path, history, raw_path)
                if status == "ok":
                    pages += 1
                    total += added
                    print(f"page {pages}: +{added} reviews ({skipped} duplicates skipped)")
                else:
                    print(status)
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
    print(f"\nDone. {total} new reviews added to {csv_path}")


def main():
    ap = argparse.ArgumentParser(description="Copy a reviews page -> reviews land in the CSV")
    ap.add_argument("--csv", default=OUT, help="where the reviews go (default: VADER folder)")
    a = ap.parse_args()
    watch(a.csv)


if __name__ == "__main__":
    main()
