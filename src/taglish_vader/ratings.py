"""
ratings.py - read star ratings, either written in the review text
("5 stars", "4/5", "10/10", star emojis) or from a CSV cell.
"""

import re

# "5 stars", "4/5", "3 star"
STAR_TEXT_PATTERN = re.compile(
    r"(?<![\w.])([1-5](?:\.\d)?)\s*(?:/\s*5|stars?|bituin)\b", re.IGNORECASE
)
TEN_POINT_PATTERN = re.compile(r"(?<![\w./])(\d{1,2}(?:\.\d)?)\s*/\s*10(?![\w/])")


def detect_stars(text):
    """Find a rating written inside the review text. Returns 1-5 or None."""
    m = STAR_TEXT_PATTERN.search(text)
    if m:
        return float(m.group(1))
    m = TEN_POINT_PATTERN.search(text)  # "10/10", "8/10"
    if m and float(m.group(1)) <= 10:
        return max(float(m.group(1)) / 2, 1.0)
    n = text.count("\u2b50")  # the star emoji
    if 1 <= n <= 5:
        return float(n)
    return None


def parse_rating(value, max_rating=5.0):
    """Turn '4', '4.5', '4 stars', '4/5', '⭐⭐⭐' into a 1-5 number (or None)."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    n = s.count("\u2b50") or s.count("\u2605")
    if n:
        x = float(n)
    else:
        m = re.search(r"\d+(?:\.\d+)?", s)
        if not m:
            return None
        x = float(m.group())
        slash = re.search(r"/\s*(\d+(?:\.\d+)?)", s)  # "4/5" style
        if slash and float(slash.group(1)) > 0:
            max_rating = float(slash.group(1))
    if x <= 0 or max_rating <= 0:
        return None
    return min(max(x / max_rating * 5.0, 1.0), 5.0)
