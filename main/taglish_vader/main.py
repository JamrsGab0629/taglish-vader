"""
main.py - command line + demo for the Taglish VADER review checker.
(Text only: star ratings are never used.)

Usage:
    python run.py                       # label my_reviews.csv (the easy way)
    python main.py                      # demo + interactive mode
    python main.py "ang ganda ng product, sulit!"
    python main.py "Wow ang galing, sira agad" --no-sarcasm
    python main.py --file reviews.csv   # label any CSV file
"""

import argparse

from analyzer import TaglishSentimentAnalyzer, label_from_compound
from batch import analyze_file
from config import SARCASM_THRESHOLD

DEMO_REVIEWS = [
    "Ang ganda ng product, sulit na sulit! Mabilis pa ang delivery.",
    "Napakapangit ng quality, sira agad after 2 days. Sayang pera.",
    "Okay lang naman, pwede na.",
    "Hindi maganda ang serbisyo, sobrang bagal ng seller.",
    "Maganda sana pero ang tagal dumating at medyo sira yung box.",
    "Hindi ako nadismaya, ang bait ng seller.",
    # texting shortcuts / typos
    "d maganda, pngit ng quality",
    "Sbrang gnda, mbilis pa. Tnx seller!",
    # domain phrases (same word, different meaning)
    "Mabilis maubos ang battery",
    "Mabilis mag-charge, ang tibay ng battery",
    "Ang bilis malowbat",
    "Matagal malowbat, ang ganda ng sound",
    "Hindi siya ma connect sa phone ko",
    "Poor quality, not working",
    "Good quality, sulit",
    # idiom: "walang masabi" = praise
    "Walang masabi sa ganda ng quality",
    # questions
    "Maganda ba talaga to? Worth it ba?",
    "Ano ba yan, bakit ang pangit ng quality?",
    # words that used to be treated as page menus
    "Shipping was fast, ang ganda ng item",
    "Next time bibili ulit ako, solid",
    # politeness after pero is not a verdict
    "Basag yung item pero salamat",
    # sarcasm
    "Wow ang galing, sira agad after 2 days.",
    "Ang bilis naman ng delivery, 3 weeks bago dumating 🙄",
    "Salamat sa wala, basag yung item.",
    "Yeah right, original daw 'to",
    'Yung "maganda" na packaging, basag lahat.',
    "Mabilis ang delivery, 3 days lang dumating.",  # NOT sarcastic
    "Wow, galing naman ng seller!",                 # NOT sarcastic
]


def show(analyzer, review):
    r = analyzer.polarity_scores(review)
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
    print(f"Result   : {label} {icon[label]}   (compound = {r['compound']:+.3f})")
    print(f"Breakdown: pos={r['pos']}  neu={r['neu']}  neg={r['neg']}")
    if r["matched"]:
        words = ", ".join(f"{w} ({sc:+})" for w, sc in r["matched"])
        print(f"Words    : {words}")


def main():
    parser = argparse.ArgumentParser(description="Taglish review sentiment checker")
    parser.add_argument("review", nargs="*", help="the review text")
    parser.add_argument("--no-sarcasm", action="store_true", help="turn sarcasm detection off")
    parser.add_argument("--file", help="CSV file of reviews")
    parser.add_argument("--text-col", help="name of the review column (auto-detected)")
    parser.add_argument("--out", help="where to save the results CSV")
    args = parser.parse_args()

    if args.file:
        analyze_file(args.file, args.text_col, args.out,
                     detect_sarcasm=not args.no_sarcasm)
        return

    analyzer = TaglishSentimentAnalyzer(detect_sarcasm=not args.no_sarcasm)

    if args.review:
        show(analyzer, " ".join(args.review))
        return

    print("=" * 60)
    print(" TAGLISH VADER - Review Sentiment Checker (with sarcasm)")
    print("=" * 60)
    for review in DEMO_REVIEWS:
        show(analyzer, review)

    print("\n" + "-" * 60)
    print("Try your own! (type 'exit' to quit)")
    print("Tip: for the collected reviews just run  python run.py")
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
