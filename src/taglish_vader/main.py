"""
main.py - command line + demo for the Taglish VADER review checker.

Usage:
    python main.py                      # demo + interactive mode
    python main.py "ang ganda ng product, sulit!"
    python main.py "ok lang" --stars 2
    python main.py "Wow ang galing, sira agad" --no-sarcasm
    python main.py --file sample_reviews.csv        # whole file + its ratings
    python main.py --file reviews.csv --text-only   # ignore the ratings
"""

import argparse

from analyzer import TaglishSentimentAnalyzer, label_from_compound
from batch import analyze_file
from config import SARCASM_THRESHOLD

# (review, optional stars)
DEMO_REVIEWS = [
    ("Ang ganda ng product, sulit na sulit! Mabilis pa ang delivery.", None),
    ("Napakapangit ng quality, sira agad after 2 days. Sayang pera.", None),
    ("Okay lang naman, pwede na.", None),
    ("Hindi maganda ang serbisyo, sobrang bagal ng seller.", None),
    ("Maganda sana pero ang tagal dumating at medyo sira yung box.", None),
    ("Hindi ako nadismaya, ang bait ng seller.", None),
    # texting shortcuts / typos
    ("d maganda, pngit ng quality", None),
    ("Sbrang gnda, mbilis pa. Tnx seller!", None),
    # domain phrases (same word, different meaning)
    ("Mabilis maubos ang battery", None),
    ("Mabilis mag-charge, ang tibay ng battery", None),
    # idiom: "walang masabi" = praise
    ("Walang masabi sa ganda ng quality", None),
    # questions
    ("Maganda ba talaga to? Worth it ba?", None),
    ("Ano ba yan, bakit ang pangit ng quality?", None),
    # star ratings
    ("5 stars", None),
    ("Ok lang", 2),
    ("Maganda naman, kaso nasira agad", 2),
    # sarcasm
    ("Wow ang galing, sira agad after 2 days.", None),
    ("Ang bilis naman ng delivery, 3 weeks bago dumating 🙄", None),
    ("Salamat sa wala, basag yung item.", None),
    ("Yeah right, original daw 'to", None),
    ('Yung "maganda" na packaging, basag lahat.', None),
    ("Mabilis ang delivery, 3 days lang dumating.", None),  # NOT sarcastic
    ("Wow, galing naman ng seller!", None),                 # NOT sarcastic
    ("Wow ang galing, sira agad", 1),
]


def show(analyzer, review, stars=None):
    r = analyzer.polarity_scores(review, stars)
    s = r["sarcasm"]
    label = label_from_compound(r["compound"])
    icon = {"GOOD": "😊", "BAD": "😡", "NEUTRAL": "😐"}

    print(f"\nReview   : {review}")
    if analyzer.detect_sarcasm:
        print(
            f"Sarcasm  : {'YES 🙄' if s['is_sarcastic'] else 'no'}   "
            f"(score = {s['score']}, needs {SARCASM_THRESHOLD})"
        )
        for reason in s["reasons"]:
            print(f"           - {reason}")
        if s["is_sarcastic"]:
            before = label_from_compound(r["original_compound"])
            print(
                f"Before   : {before} {icon[before]}  ({r['original_compound']:+.3f})"
                "  <- words only, before the sarcasm flip"
            )
    if r["stars"] is not None:
        print(
            f"Stars    : {r['stars']:g}  (star score {r['star_compound']:+.2f}, "
            f"text score {r['text_compound']:+.2f})"
        )
    print(f"Result   : {label} {icon[label]}   (compound = {r['compound']:+.3f})")
    print(f"Breakdown: pos={r['pos']}  neu={r['neu']}  neg={r['neg']}")
    if r["matched"]:
        words = ", ".join(f"{w} ({sc:+})" for w, sc in r["matched"])
        print(f"Words    : {words}")


def main():
    parser = argparse.ArgumentParser(description="Taglish review sentiment checker")
    parser.add_argument("review", nargs="*", help="the review text")
    parser.add_argument("--stars", type=float, help="star rating for a single review (1-5)")
    parser.add_argument("--no-sarcasm", action="store_true", help="turn sarcasm detection off")
    parser.add_argument("--file", help="CSV file of reviews (ratings are read automatically)")
    parser.add_argument("--text-col", help="name of the review column (auto-detected)")
    parser.add_argument("--stars-col", help="name of the rating column (auto-detected)")
    parser.add_argument("--max-rating", type=float, default=5.0,
                        help="top of the rating scale in the file (default 5, use 10 for 1-10)")
    parser.add_argument("--text-only", action="store_true",
                        help="ignore ratings when labeling (they are still compared in the report)")
    parser.add_argument("--out", help="where to save the results CSV")
    args = parser.parse_args()

    if args.file:
        analyze_file(args.file, args.text_col, args.stars_col, args.out,
                     args.max_rating, use_stars=not args.text_only,
                     detect_sarcasm=not args.no_sarcasm)
        return

    analyzer = TaglishSentimentAnalyzer(detect_sarcasm=not args.no_sarcasm)

    if args.review:
        show(analyzer, " ".join(args.review), args.stars)
        return

    print("=" * 60)
    print(" TAGLISH VADER - Review Sentiment Checker (with sarcasm)")
    print("=" * 60)
    for review, stars in DEMO_REVIEWS:
        show(analyzer, review, stars)

    print("\n" + "-" * 60)
    print("Try your own! (type 'exit' to quit)")
    print("Tip: for a whole file of reviews use  --file reviews.csv")
    while True:
        try:
            text = input("\nIsulat ang review: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() in {"exit", "quit", "q"}:
            break
        if text:
            show(analyzer, text)


if __name__ == "__main__":
    main()
