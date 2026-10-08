"""
clean_paste.py - keep only the reviews from pages copied with clip_collect.py.

MODE 1 - DATE MODE (default when dates are found, most exact):
  Every Shopee review has a date line ("2024-05-12 14:30 | Variation: Black").
  The review text is whatever comes right after that date line, until a stop line
  ("Helpful", "Report", the seller's reply, page buttons, menus) or the next review.
  Multi-line reviews are joined into one line, and one-word reviews like "Good" are kept.

MODE 2 - FILTER MODE (fallback when no date lines are found):
  Drops menus, dates, prices, labels, short lines, and lines repeated on most pages.

Usage:  python clean_paste.py raw_pages.txt clean.txt
        python clean_paste.py raw_pages.txt clean.txt --mode filter
Then:   python collect.py --import clean.txt
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

# ----- lines that END a review (buttons, seller reply, pager) -------------------
STOP_LINE = re.compile(
    r"^((helpful\??|report|reply|likes?)\s*(\(\d+\)|\d+)?$|seller'?s? response|response from|"
    r"was this|show more|see more)",
    re.IGNORECASE,
)
PAGER_LINE = re.compile(r"^[\d\s.…<>‹›«»]+$")  # "1 2 3 ... 10 >"

# ----- menu / page junk --------------------------------------------------------
# Menu words are only menus when they are the WHOLE line. A review such as
# "Shipping was fast" or "Next time bibili ulit ako" must never be thrown away.
MENU_EXACT = re.compile(
    r"^(shop|shop vouchers?|shipping|free shipping|vouchers?|stock|category|sold|"
    r"product ratings?|ratings?|sort( by)?|filter|previous|prev|next|page( \d+)?|all|"
    r"with comments|with media|with photos?|with videos?|related( products?)?|"
    r"you may also like|from the same shop|customer service|download( the app)?|"
    r"followers|following|joined|visit|view shop|chat now|chat|add to cart|buy now|"
    r"response rate|response time|ships from)\s*:?\s*$",
    re.IGNORECASE,
)
# These only ever appear in page chrome, so a line that STARTS with them is junk.
MENU_PREFIX = re.compile(
    r"^(add to cart|buy now|chat now|view shop|brand:|category:|©|copyright|"
    r"privacy policy|terms (of|&|and) |you may also like|from the same shop|"
    r"related products|product ratings)",
    re.IGNORECASE,
)

# the known rating sub-labels that sit between the date and the review text
LABEL_NAMES = (
    r"variation|quality|performance|true to description|rating|sound quality|battery life|"
    r"best feature|comfort|fit|durability|material|value for money|features?|colou?r|size|"
    r"seller service|delivery service|packaging|product"
)
RATING_LABEL = re.compile(rf"^(?:{LABEL_NAMES})\s*:\s*\S", re.IGNORECASE)
PRICE = re.compile(
    r"^[₱$]\s?[\d,.]+|^\d+(\.\d+)?[kK]?\s*(sold|ratings?|reviews?|followers|%)",
    re.IGNORECASE,
)


# "Colour: the color is true", "Appearance: good": the label word is the seller's form
# (grey on the page), the words after it are the reviewer's own (black). Plain-text copy
# has no colors, but the label always looks like "Word:" at the start of the line,
# so the label is cut and the reviewer's words are kept.
LABEL_PREFIX = re.compile(r"^([A-Za-z][A-Za-z ]{1,24}):\s*")
DURATION_LINE = re.compile(r"^(?:\d{1,2}:\d{2}\s*)+$")      # video length "0:12"


def strip_label(line):
    """One-word labels (Appearance:, Colour:, Material:) and the known multi-word ones
    (Sound quality:). "Great product: works well" is the reviewer's own text and stays."""
    m = LABEL_PREFIX.match(line)
    if not m:
        return line
    label = m.group(1).strip()
    if " " not in label or re.fullmatch(LABEL_NAMES, label, re.IGNORECASE):
        return line[m.end():].strip()
    return line


def is_menu(line):
    s = line.strip()
    return bool(MENU_EXACT.match(s) or MENU_PREFIX.match(s))


def is_label(line):
    return bool(RATING_LABEL.match(line)) and len(line.split()) <= 6


def looks_like_username(s):
    """Shopee masks usernames like  j***n  . A normal last word ("salamat") is kept."""
    if " " in s:
        return False
    if "*" in s or "_" in s:
        return True
    has_digit = any(c.isdigit() for c in s)
    has_alpha = any(c.isalpha() for c in s)
    return (has_digit and has_alpha and len(s) >= 5) or len(s) > 16


def page_chrome(pages, min_pages=8):
    """
    Lines that appear on (almost) every page: menus, product title, shop info.
    Needs 8+ pages to be sure, and a line that sits right after a date line
    (a real review like "Good") is never called chrome.
    """
    if len(pages) < min_pages:
        return set()
    counts = Counter()
    review_like = set()
    for p in pages:
        lines = [l.strip() for l in p.splitlines() if l.strip()]
        for i, l in enumerate(lines):
            if DATE_LINE.match(l) and i + 1 < len(lines):
                nxt = lines[i + 1]
                if not (PRICE.match(nxt) or STOP_LINE.match(nxt) or DURATION_LINE.match(nxt)):
                    review_like.add(nxt.lower())
        for ln in {l.lower() for l in lines}:
            counts[ln] += 1
    cut = max(min_pages, math.ceil(len(pages) * 0.8))
    return {ln for ln, n in counts.items() if n >= cut and ln not in review_like}


# ============================ TIDY (final cleanup) ===============================
INVISIBLE = re.compile("[‎‏​⁠﻿]")
LEAD_TIME = re.compile(r"^(?:\d{1,2}:\d{2}\s+)+")
TIME_TAIL = re.compile(r"(?:\s+\d{1,2}:\d{2})+\s*$")
# only the real button row ("Helpful? Profile", "Helpful Report"); a review that ends
# with the word "reply", "profile" or "helpful" on its own keeps it
BUTTON_TAIL = re.compile(
    r"\s+helpful\?(?:\s+\S+){0,3}\s*$"                       # "helpful? profile username"
    r"|\s+helpful\s+(?:profile|report|reply|translate)(?:\s+\S+){0,2}\s*$",
    re.IGNORECASE,
)
ONLY_JUNK = re.compile(
    r"^(?:\d{1,2}:\d{2}|helpful\??|profile|report|reply|translate|\s)*$", re.IGNORECASE
)
# Shopee's review-form labels. They are not the reviewer's words, and "quality" would
# wrongly count as a positive word, so the label is removed and the answer is kept.
FORM_LABELS = re.compile(
    r"\b(appearance|sound quality|performance|best feature|true to description|quality|colou?r|"
    r"comfort|fit|durability|material|battery life|value for money|features?)\s*:\s*",
    re.IGNORECASE,
)
# "Product: Poor quality, Counterfeit product, Item Not as Described" is a dropdown the
# buyer ticked on the form. It leaks the star level, so it is cut. Only cut when EVERY
# part looks like a form choice ("Great product: works well" is kept).
PRODUCT_TAG = re.compile(r"(?:^|\s)Product\s*:\s*(.+)$", re.IGNORECASE)
TAG_WORDS = (
    "quality", "counterfeit", "described", "defective", "damaged", "wrong", "fake",
    "missing", "expired", "poor", "item", "product", "broken", "packaging", "size",
    "color", "colour",
)


def strip_product_tag(text):
    m = PRODUCT_TAG.search(text)
    if not m:
        return text
    parts = [p.strip().lower() for p in re.split(r"[,/]", m.group(1)) if p.strip()]
    if parts and all(any(k in p for k in TAG_WORDS) for p in parts):
        return text[:m.start()]
    return text


def tidy(text):
    """Remove form tags, video lengths (0:12), the 'helpful? profile' row, hidden characters."""
    t = INVISIBLE.sub("", text)
    t = strip_product_tag(t.strip())
    t = LEAD_TIME.sub("", t.strip())
    t = TIME_TAIL.sub("", t)
    t = BUTTON_TAIL.sub("", t)
    t = TIME_TAIL.sub("", t)
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
                if (STOP_LINE.match(l) or is_menu(l) or PAGER_LINE.match(l)
                        or l.lower() in chrome):
                    stopped = True
                    break
                if DURATION_LINE.match(l) or (not block and PRICE.match(l)):
                    continue
                if not strip_product_tag(l).strip():
                    continue                # "Product: Poor quality, Counterfeit product, ..."
                l = strip_label(l)          # "Appearance: good" -> "good"
                if l:
                    block.append(l)
            if not stopped and has_next and block:
                if looks_like_username(block[-1]):   # the NEXT reviewer's masked name
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
    if is_menu(s) or STOP_LINE.search(s) or is_label(s):
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
                kept.append(tidy(s))
    return [k for k in kept if k], dropped, reasons


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
        if len(pages) < 8:
            print("Note: fewer than 8 pages, so the repeated-line filter is off.")
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
