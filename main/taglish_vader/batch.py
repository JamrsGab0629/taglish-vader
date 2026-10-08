"""
batch.py - read a CSV of reviews and label them all, from the TEXT ONLY.

No star ratings are used anywhere: stars are a guess about what the review says,
so they are not allowed to influence (or grade) the labels.

To measure accuracy honestly, add a column called  human_label  to the CSV and
fill it in yourself with GOOD / NEUTRAL / BAD for each review (a second person
labeling too is even better). Then run again: the report compares the analyzer
against YOUR labels.
"""

import csv
import os
from collections import Counter, defaultdict

from analyzer import TaglishSentimentAnalyzer, label_from_compound
from config import BOOSTERS, NEGATORS, BUT_WORDS

TEXT_COLUMN_NAMES = [
    "review", "reviews", "review_text", "reviewtext", "text", "comment",
    "comments", "content", "feedback", "body", "message",
]
HUMAN_COLUMN_NAMES = ["human_label", "label", "my_label", "gold", "gold_label"]
LABELS = ("GOOD", "NEUTRAL", "BAD")
LABEL_ALIASES = {
    "good": "GOOD", "positive": "GOOD", "pos": "GOOD", "g": "GOOD", "p": "GOOD",
    "neutral": "NEUTRAL", "neu": "NEUTRAL", "n": "NEUTRAL", "mixed": "NEUTRAL",
    "bad": "BAD", "negative": "BAD", "neg": "BAD", "b": "BAD",
}
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


def find_unknown_words(analyzer, texts, top=25, min_count=2):
    """
    Words the analyzer doesn't know yet (possible new slang), most common first.
    Returns a list of (word, number_of_reviews).
    Look at them yourself and decide: positive, negative, or neutral. Do this on your
    TRAIN reviews only, never on the reviews you test on.
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
    rows = [(w, len(idxs)) for w, idxs in seen.items() if len(idxs) >= min_count]
    rows.sort(key=lambda r: (-r[1], r[0]))
    return rows[:top]


def _clean_label(value):
    return LABEL_ALIASES.get((value or "").strip().lower())


def analyze_file(path, text_col=None, out_path=None, detect_sarcasm=True):
    """Label every review in a CSV file. Writes <file>_results.csv and prints a summary."""
    rows, fields = _read_csv(path)
    text_key = _pick_column(fields, text_col, TEXT_COLUMN_NAMES) or fields[0]
    human_key = _pick_column(fields, None, HUMAN_COLUMN_NAMES)

    analyzer = TaglishSentimentAnalyzer(detect_sarcasm=detect_sarcasm)

    out_rows, texts = [], []
    for row in rows:
        review = (row.get(text_key) or "").strip()
        r = analyzer.polarity_scores(review)
        out = dict(row)
        out.update({
            "text_label": label_from_compound(r["compound"]),
            "text_score": r["compound"],
            "sarcasm": "yes" if r["sarcasm"]["is_sarcastic"] else "",
        })
        out_rows.append(out)
        texts.append(review)

    if out_path is None:
        base, _ = os.path.splitext(path)
        out_path = base + "_results.csv"
    extra = ["text_label", "text_score", "sarcasm"]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields + extra, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)

    # ----- summary -----
    n = len(out_rows)
    print(f"\nFile      : {path}   ({n} reviews)")
    print(f"Column    : review = '{text_key}'   (text only, no star ratings used)")
    counts = Counter(r["text_label"] for r in out_rows)
    print("Labels    : " + "   ".join(
        f"{k} {counts.get(k, 0)} ({counts.get(k, 0) / max(n, 1):.0%})" for k in LABELS))
    print(f"Sarcastic : {sum(1 for r in out_rows if r['sarcasm'])}")

    # ----- accuracy against YOUR labels (only if you filled human_label) -----
    if human_key:
        graded = [(r, _clean_label(r.get(human_key))) for r in out_rows]
        graded = [(r, h) for r, h in graded if h]
        if graded:
            agree = sum(1 for r, h in graded if r["text_label"] == h)
            print(f"\nvs your labels ('{human_key}'): {agree}/{len(graded)} correct "
                  f"({agree / len(graded):.0%})")
            print("\nRows = your label, columns = analyzer:")
            print(f"{'':10}" + "".join(f"{l:>9}" for l in LABELS))
            for h_lab in LABELS:
                cells = [sum(1 for r, h in graded if h == h_lab and r["text_label"] == p)
                         for p in LABELS]
                print(f"{h_lab:10}" + "".join(f"{c:>9}" for c in cells))
            wrong = [(r, h) for r, h in graded if r["text_label"] != h]
            if wrong:
                print("\nSome mistakes (look at these to improve lexicon.py):")
                for r, h in wrong[:10]:
                    print(f"  you={h:7} analyzer={r['text_label']:7} | {(r.get(text_key) or '')[:70]}")
        else:
            print(f"\nColumn '{human_key}' is empty - fill it with GOOD / NEUTRAL / BAD to get accuracy.")
    else:
        print("\nTo measure accuracy: add a column  human_label  and label the reviews yourself.")

    unknown = find_unknown_words(analyzer, texts)
    if unknown:
        print("\nWords the analyzer doesn't know (in 2+ reviews) - possible new slang:")
        print("  " + ", ".join(f"{w} ({c})" for w, c in unknown))
        print("  -> add real slang to lexicon.py (misspellings go in normalizer.py).")
    print(f"\nSaved     : {out_path}")
    return out_rows
