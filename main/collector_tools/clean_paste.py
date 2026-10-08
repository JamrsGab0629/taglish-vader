"""
clean_paste.py - keep only the reviews from pages copied with clip_collect.py.

MODE 1 - DATE MODE (default when dates are found, most exact):
  Every Shopee review has a date line ("2024-05-12 14:30 | Variation: Black").
  The review text is whatever comes right after that date line, until a stop line
  ("Helpful", "Report", the seller's reply, page buttons, menus) or the next review.
  Multi-line reviews are joined into one line, and one-word reviews like "Good" are kept.

MODE 2 - FILTER MODE (fallback when no date lines are found):
  Drops menus, dates, prices, labels, short lines, and lines repeated on most pages.

Usage:  python clean_paste.py five_star.txt five_star_clean.txt
        python clean_paste.py five_star.txt five_star_clean.txt --mode filter
Always skim the output: Shopee's layout varies.
"""

import argparse
import math
import re
from collections import Counter

PAGE_MARK = "=====PAGE====="

# ----- the date line that starts every review -----------------------------------
DATE_LINE = re.compile(
    r"^\s*(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}\s+[A-Za-z]{3,9}\.?\s+\d{4})"
    r"(\s+\d{1,2}:\d{2})?"
)

# ----- lines that END a review (buttons, seller reply, pager, menus) ------------
STOP_LINE = re.compile(
    r"^((helpful|report|reply|likes?)\s*(\(\d+\)|\d+)?$|seller'?s? response|response from|"
    r"was this|show more|see more)",
    re.IGNORECASE,
)
PAGER_LINE = re.compile(r"^[\d\s.\u2026<>\u2039\u203a\u00ab\u00bb]+$")  # "1 2 3 ... 10 >"

# ----- menu / page junk (stops a review, and is dropped in filter mode) ---------
MENU_START = re.compile(
    r"^(shop\b|brand:|stock|category|sold\b|ships?\b|shipping|free shipping|voucher|"
    r"add to cart|buy now|chat now|visit|view shop|followers|following|response|joined|"
    r"product ratings|sort|filter|previous|next\b|page\b|related|you may|from the|"
    r"customer|download|copyright|privacy|terms|with (comments|media)|all\b$)",
    re.IGNORECASE,
)
# rating sub-labels that sit between the date and the review text (skipped, not stops)
RATING_LABEL = re.compile(
    r"^(variation|quality:|performance:|true to description:|rating|[a-z][a-z ]{2,25}:\s*\S)",
    re.IGNORECASE,
)
PRICE = re.compile(
    r"^[\u20b1$]\s?[\d,.]+|^\d+(\.\d+)?[kK]?\s*(sold|ratings?|reviews?|followers|%)",
    re.IGNORECASE,
)


def is_label(line):
    return bool(RATING_LABEL.match(line)) and len(line.split()) <= 6


def looks_like_username(s):
    return " " not in s and (any(c in s for c in "*_") or any(c.isdigit() for c in s) or len(s) > 12)


def page_chrome(pages):
    """Lines that appear on (almost) every page: menus, product title, shop info."""
    if len(pages) < 3:
        return set()
    counts = Counter()
    for p in pages:
        for ln in {l.strip().lower() for l in p.splitlines() if l.strip()}:
            counts[ln] += 1
    cut = max(3, math.ceil(len(pages) * 0.8))
    return {ln for ln, n in counts.items() if n >= cut}



# ============================ TIDY (final cleanup) ===============================
INVISIBLE = re.compile("[\u200e\u200f\u200b\u2060\ufeff]")
LEAD_TIME = re.compile(r"^(?:\d{1,2}:\d{2}\s+)+")
TRAIL_JUNK = re.compile(
    r"(?:\s+(?:\d{1,2}:\d{2}|helpful\??|profile|report|reply|translate))+\s*$", re.IGNORECASE
)
# Shopee's review-form labels. They are not the reviewer's words, and "quality" would
# wrongly count as a positive word, so the label is removed and the answer is kept.
ONLY_JUNK = re.compile(
    r"^(?:\d{1,2}:\d{2}|helpful\??|profile|report|reply|translate|\s)*$", re.IGNORECASE
)
FORM_LABELS = re.compile(
    r"\b(sound quality|performance|best feature|true to description|quality|colou?r|"
    r"comfort|fit|durability|material|battery life|value for money|features?)\s*:\s*",
    re.IGNORECASE,
)


def tidy(text):
    """Remove video lengths (0:12), 'helpful? profile', hidden characters, and form labels."""
    t = INVISIBLE.sub("", text)
    t = LEAD_TIME.sub("", t.strip())
    t = TRAIL_JUNK.sub("", t)
    t = FORM_LABELS.sub("", t)
    t = re.sub(r"\s+", " ", t).strip()
    if ONLY_JUNK.match(t):          # nothing left but video lengths / buttons
        return ""
    return t

# =============================== DATE MODE ======================================
def extract_by_date(pages, chrome=None):
    if chrome is None:
        chrome = page_chrome(pages)
    reviews, seen = [], set()
    stats = Counter()
    for p in pages:
        lines = [l.strip() for l in p.splitlines() if l.strip()]
        dates = [i for i, l in enumerate(lines) if DATE_LINE.match(l)]
        for n, i in enumerate(dates):
            stats["dates"] += 1
            has_next = n + 1 < len(dates)
            end = dates[n + 1] if has_next else len(lines)
            block, stopped = [], False
            for l in lines[i + 1:end]:
                if (STOP_LINE.match(l) or MENU_START.match(l) or PAGER_LINE.match(l)
                        or l.lower() in chrome):
                    stopped = True
                    break
                if not block and (is_label(l) or PRICE.match(l)):
                    continue
                block.append(l)
            if not stopped and has_next and block:
                last = block[-1]       # the next reviewer's username sits right before their date
                if " " not in last and (len(block) >= 2 or looks_like_username(last)):
                    block.pop()
            text = tidy(" ".join(block))
            if len(text) < 2:
                stats["empty (rating only)"] += 1
            elif text.lower() in seen:
                stats["duplicate"] += 1
            else:
                seen.add(text.lower())
                reviews.append(text)
    return reviews, stats


# ============================== FILTER MODE =====================================
def why_drop(line, min_words):
    s = line.strip()
    if not s:
        return "empty"
    if MENU_START.search(s) or STOP_LINE.search(s) or RATING_LABEL.match(s):
        return "label / menu"
    if DATE_LINE.match(s):
        return "date"
    if PRICE.search(s):
        return "price / count"
    non_space = [c for c in s if not c.isspace()]
    letters = sum(c.isalpha() for c in non_space)
    if letters < 3 or letters / len(non_space) < 0.4:
        return "mostly numbers / symbols"
    if len(s.split()) < min_words:
        return "too short (username?)"
    return None


def extract_by_filter(pages, min_words):
    chrome = page_chrome(pages)
    kept, dropped, seen, reasons = [], [], set(), Counter()
    for p in pages:
        for line in p.splitlines():
            s = line.strip()
            if not s:
                continue
            reason = why_drop(s, min_words)
            if not reason and s.lower() in chrome:
                reason = "repeats on every page (menu / product info)"
            if not reason and s.lower() in seen:
                reason = "duplicate"
            if reason:
                reasons[reason] += 1
                dropped.append(f"[{reason}] {s}")
            else:
                seen.add(s.lower())
                kept.append(s)
    return kept, dropped, reasons


# ================================== MAIN ========================================
def clean(path, out, mode="auto", min_words=2):
    text = open(path, encoding="utf-8").read()
    pages = [p for p in text.split(PAGE_MARK) if p.strip()]
    if not pages:
        print("The file is empty.")
        return
    n_dates = sum(1 for p in pages for l in p.splitlines() if DATE_LINE.match(l.strip()))
    if mode == "auto":
        mode = "date" if n_dates >= 3 else "filter"
    print(f"pages: {len(pages)}   date lines found: {n_dates}   mode: {mode}")

    if mode == "date":
        reviews, stats = extract_by_date(pages)
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(reviews))
        print(f"kept {len(reviews)} reviews -> {out}")
        for k in ("empty (rating only)", "duplicate"):
            if stats[k]:
                print(f"  skipped {stats[k]:3}  {k}")
        for r in reviews[:5]:
            print("  e.g.", r[:90])
    else:
        if len(pages) < 3:
            print("Note: fewer than 3 pages, so the repeated-line filter is off.")
        kept, dropped, reasons = extract_by_filter(pages, min_words)
        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(kept))
        drop_path = out.rsplit(".", 1)[0] + "_dropped.txt"
        with open(drop_path, "w", encoding="utf-8") as f:
            f.write("\n".join(dropped))
        print(f"kept: {len(kept)}   dropped: {len(dropped)}")
        for r, n in reasons.most_common():
            print(f"  dropped {n:4}  {r}")
        print(f"saved -> {out}\nremoved lines (check these) -> {drop_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--mode", choices=["auto", "date", "filter"], default="auto")
    ap.add_argument("--min-words", type=int, default=2, help="filter mode only")
    a = ap.parse_args()
    clean(a.input, a.output, a.mode, a.min_words)
