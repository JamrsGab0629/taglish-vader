"""
batch.py - read a CSV of reviews (and their star ratings) and label them all.
Ratings are read from the file itself, so nobody has to type them.
"""

import csv
import os
import re
from collections import Counter, defaultdict

from analyzer import TaglishSentimentAnalyzer, label_from_compound
from config import BOOSTERS, NEGATORS, BUT_WORDS
from ratings import parse_rating

TEXT_COLUMN_NAMES = [
    "review", "reviews", "review_text", "reviewtext", "text", "comment",
    "comments", "content", "feedback", "body", "message",
]
STAR_COLUMN_NAMES = [
    "rating", "ratings", "stars", "star", "star_rating", "review_rating",
    "score", "rate",
]
# common filler words (ignored when hunting for unknown slang)
STOPWORDS = set(
    "ang ng sa na ay at ko mo yung yong ito to ba naman lang po pa din rin si ni "
    "kay mga ako ikaw siya kami kayo sila kasi para kaya ung nung dun doon dito "
    "may mayroon yun iyon ka ako akin ating namin nila niya nyo nyong ang the "
    "and for with this that was are you but have has had his her its our they "
    "them their there from then than also been will would could should about "
    "when what which while where who how all any can one out too get got just "
    "item order seller product".split()
)


def _read_csv(path):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, newline="", encoding=enc) as f:
                sample = f.read(4096)
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
                except csv.Error:
                    dialect = csv.excel
                reader = csv.DictReader(f, dialect=dialect)
                rows = list(reader)
                fields = list(reader.fieldnames or [])
            if not fields:
                raise ValueError("The file looks empty (no header row).")
            return rows, fields
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not read the file as text.")


def _pick_column(fields, wanted, candidates):
    lowered = {f.strip().lower(): f for f in fields}
    if wanted:
        key = wanted.strip().lower()
        if key in lowered:
            return lowered[key]
        raise ValueError(f"Column '{wanted}' not found. Columns: {', '.join(fields)}")
    for name in candidates:
        if name in lowered:
            return lowered[name]
    return None


def find_unknown_words(analyzer, texts, ratings=None, top=25, min_count=2):
    """
    Words the analyzer doesn't know yet (possible new slang), most common first.
    If ratings are given, shows the average rating of the reviews using each word:
    a word that shows up mostly in 5-star reviews is probably positive.
    Returns a list of (word, number_of_reviews, average_stars_or_None).

    Tip: run this on your TRAIN split only, never on dev/test.
    """
    seen = defaultdict(set)
    for idx, text in enumerate(texts):
        for _, w in analyzer._tokenize(text):
            if not w.isalpha() or len(w) < 3 or w in STOPWORDS:
                continue
            if w in BOOSTERS or w in NEGATORS or w in BUT_WORDS:
                continue
            if w in analyzer.lexicon or analyzer._valence(w) != 0:
                continue
            seen[w].add(idx)
    rows = []
    for w, idxs in seen.items():
        if len(idxs) < min_count:
            continue
        vals = [ratings[i] for i in idxs if ratings and ratings[i] is not None]
        rows.append((w, len(idxs), sum(vals) / len(vals) if vals else None))
    rows.sort(key=lambda r: (-r[1], r[0]))
    return rows[:top]


def analyze_file(path, text_col=None, stars_col=None, out_path=None,
                 max_rating=5.0, use_stars=True, detect_sarcasm=True):
    """
    Label every review in a CSV file. Writes <file>_results.csv and prints a summary.
    Report text_label (not final_label) as your accuracy: final_label blends in
    the star rating, so scoring it against the same rating is circular.
    """
    rows, fields = _read_csv(path)
    text_key = _pick_column(fields, text_col, TEXT_COLUMN_NAMES) or fields[0]
    star_key = _pick_column(fields, stars_col, STAR_COLUMN_NAMES)

    text_an = TaglishSentimentAnalyzer(detect_sarcasm=detect_sarcasm, use_stars=False)
    final_an = (
        TaglishSentimentAnalyzer(detect_sarcasm=detect_sarcasm, use_stars=True)
        if use_stars and star_key else text_an
    )

    out_rows, texts, ratings = [], [], []
    for row in rows:
        review = (row.get(text_key) or "").strip()
        stars = parse_rating(row.get(star_key), max_rating) if star_key else None
        t = text_an.polarity_scores(review)
        f = final_an.polarity_scores(review, stars) if final_an is not text_an else t
        rating_label = None
        if stars is not None:
            rating_label = "GOOD" if stars >= 4 else "BAD" if stars <= 2 else "NEUTRAL"
        text_label = label_from_compound(t["compound"])
        out = dict(row)
        out.update({
            "text_label": text_label,
            "text_score": t["compound"],
            "sarcasm": "yes" if t["sarcasm"]["is_sarcastic"] else "",
            "final_label": label_from_compound(f["compound"]),
            "final_score": f["compound"],
            "rating_label": rating_label or "",
            "agrees": "" if rating_label is None else ("yes" if rating_label == text_label else "NO"),
        })
        out_rows.append(out)
        texts.append(review)
        ratings.append(stars)

    if out_path is None:
        base, _ = os.path.splitext(path)
        out_path = base + "_results.csv"
    extra = ["text_label", "text_score", "sarcasm", "final_label", "final_score",
             "rating_label", "agrees"]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields + extra, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)

    # ----- summary -----
    n = len(out_rows)
    print(f"\nFile      : {path}   ({n} reviews)")
    print(f"Columns   : review = '{text_key}',  rating = '{star_key or 'none found'}'")
    mode = "text + star ratings" if final_an is not text_an else "text only"
    print(f"Mode      : {mode}")
    counts = Counter(r["final_label"] for r in out_rows)
    print("Final     : " + "   ".join(
        f"{k} {counts.get(k, 0)} ({counts.get(k, 0) / max(n, 1):.0%})"
        for k in ("GOOD", "NEUTRAL", "BAD")))
    sarcastic = sum(1 for r in out_rows if r["sarcasm"])
    print(f"Sarcastic : {sarcastic}")

    rated = [r for r in out_rows if r["rating_label"]]
    if rated:
        agree = sum(1 for r in rated if r["agrees"] == "yes")
        print(f"\nText vs star rating: they agree on {agree}/{len(rated)} ({agree / len(rated):.0%})")

        labels = ("GOOD", "NEUTRAL", "BAD")
        print("\nRows = star rating, columns = text prediction:")
        print(f"{'':10}" + "".join(f"{l:>9}" for l in labels))
        for t in labels:
            row = [sum(1 for r in rated
                       if r["rating_label"] == t and r["text_label"] == p)
                   for p in labels]
            print(f"{t:10}" + "".join(f"{c:>9}" for c in row))

        conflicts = [r for r in rated
                     if {r["rating_label"], r["text_label"]} == {"GOOD", "BAD"}]
        if conflicts:
            print("\nDirect conflicts (rating says one thing, the text says the opposite):")
            for r in conflicts[:8]:
                print(f"  rating={r['rating_label']:4} text={r['text_label']:4} | {(r.get(text_key) or '')[:70]}")

    unknown = find_unknown_words(text_an, texts, ratings)
    if unknown:
        print("\nWords the analyzer doesn't know (in 2+ reviews) - possible new slang:")
        print(f"  {'word':14}{'reviews':>8}{'avg stars':>11}   guess")
        for word, cnt, avg in unknown:
            guess = ""
            if avg is not None:
                guess = "+ likely positive" if avg >= 4.2 else "- likely negative" if avg <= 2.3 else ""
            avg_s = f"{avg:.1f}" if avg is not None else "-"
            print(f"  {word:14}{cnt:>8}{avg_s:>11}   {guess}")
        print("  -> add real slang to lexicon.py (misspellings go in normalizer.py).")
    print(f"\nSaved     : {out_path}")
    return out_rows
