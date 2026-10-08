"""
run.py - label the reviews the collector saved. Just run:   python run.py

Reads  my_reviews.csv  from THIS folder (where the collector saves it),
labels every review GOOD / NEUTRAL / BAD from the text only, and writes
my_reviews_results.csv next to it. Optional: python run.py other_file.csv
"""

import os
import sys

from batch import analyze_file

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "my_reviews.csv")
    if not os.path.exists(path):
        print(f"No reviews yet: {path} does not exist.")
        print("Run  python start_collecting.py  first to collect some.")
        return
    analyze_file(path)


if __name__ == "__main__":
    main()
