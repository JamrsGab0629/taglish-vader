"""
config.py - all the settings and word lists you can tune.
Nothing in here imports other project files.
"""

import re

# ---------------------------------------------------------------------------
# Boosters (+) make the next feeling stronger, dampeners (-) make it weaker
# ---------------------------------------------------------------------------
BOOSTERS = {
    "sobra": 0.35, "sobrang": 0.35, "grabe": 0.40, "grabeng": 0.40,
    "super": 0.35, "very": 0.29, "napaka": 0.40, "pinaka": 0.40,
    "talaga": 0.20, "talagang": 0.25, "masyado": 0.25, "masyadong": 0.25,
    "ubod": 0.35, "lubos": 0.30, "extremely": 0.40, "really": 0.25,
    "so": 0.20, "totally": 0.30, "sobra-sobra": 0.40, "ang": 0.0,
    # dampeners
    "medyo": -0.25, "konti": -0.20, "konting": -0.20, "slightly": -0.25,
    "somewhat": -0.25, "kinda": -0.25, "parang": -0.20, "slight": -0.25,
}

# Words that FLIP the meaning of the next feeling
NEGATORS = {
    "hindi", "hindi'", "di", "hnd", "hndi", "wala", "walang", "ayaw",
    "not", "no", "never", "dont", "don't", "didn't", "isn't", "wasn't",
    "cant", "can't", "won't", "doesn't", "aint", "ain't",
}

# "But" words: what comes AFTER matters more
BUT_WORDS = {"pero", "kaso", "ngunit", "subalit", "but", "however", "datapero"}

# Punctuation that stops a negation / booster from reaching further
BREAKERS = {".", "!", "?", ";", ","}

# ---------------------------------------------------------------------------
# Scoring numbers
# ---------------------------------------------------------------------------
NEGATION_FACTOR = -0.74
CAPS_BOOST = 0.733
EXCLAIM_BOOST = 0.292
POS_THRESHOLD = 0.05
NEG_THRESHOLD = -0.05
NORMALIZE_ALPHA = 15

# Question rule: "Maganda ba?" is a question, not praise
QUESTION_POS_FACTOR = 0.0   # praise inside a question is ignored
QUESTION_NEG_FACTOR = 0.7   # complaints stay (often rhetorical: "Bakit ang tagal?")

# Star ratings
STAR_STRENGTH = 0.8         # 5 stars = +0.8, 1 star = -0.8 (on the -1..+1 scale)
STAR_WEIGHT = 0.4           # if the text has sentiment: 60% text + 40% stars

# ---------------------------------------------------------------------------
# SARCASM DETECTOR settings
#
# Sarcasm says positive words but means something negative, so we add up clues:
#   Positive AND negative words, no "pero"            2.0
#   Sarcasm phrases (yeah right, salamat sa wala...)  0.5 - 3.0 each (max 3.0)
#   Sarcastic emojis                                  1.0 - 2.0 each (max 3.0)
#   "daw / raw" after a positive word (maganda daw)   1.5
#   Positive word in "quotes"                         2.0
#   "Mabilis" + a long wait (e.g. 3 weeks)            3.0
# At SARCASM_THRESHOLD the review is sarcastic and flipped to negative.
# ---------------------------------------------------------------------------
SARCASM_THRESHOLD = 2.5   # score needed to call a review sarcastic
SARCASM_MIN_NEG = 0.5     # a sarcastic review is at least this negative

# phrase -> points   (weights >= 2.0 are "strong" and can trigger on their own)
SARCASM_MARKERS = {
    "/s": 3.0,
    "salamat sa wala": 3.0,
    "thanks for nothing": 3.0,
    "yeah right": 2.0,
    "oh sure": 1.5,
    "as if": 1.5,
    "thanks a lot": 1.5,
    "galing naman": 1.5,
    "napakagaling naman": 1.5,
    "bilis naman": 1.5,
    "congrats": 1.0,
    "congratulations": 1.0,
    "buti na lang": 1.0,
    "wow": 0.5,
    "great job": 1.0,
    "good job": 1.0,
}

SARCASM_EMOJIS = {"🙄": 2.0, "🙃": 2.0, "🤡": 2.0, "😒": 1.5, "👏": 1.0}

MARKER_CAP = 3.0
EMOJI_CAP = 3.0
MIXED_POLARITY_POINTS = 2.0
HEARSAY_POINTS = 1.5      # "maganda daw", "original raw"
QUOTED_POINTS = 2.0       # "maganda" in quotes
DELAY_POINTS = 3.0        # "ang bilis, 3 weeks bago dumating"

STRONG_WORD_SCORE = 1.5   # how strong a word must be to count for mixed polarity
LONG_WAIT_DAYS = 7        # wait this long or more = "slow"

SPEED_PATTERN = re.compile(
    r"\b(?:napaka|pinaka)?(?:ma|ka)?bilis\b|\b(?:fast|quick|quickly|express|speedy)\b"
)
DURATION_PATTERN = re.compile(
    r"(\d+)\s*(?:-\s*\d+\s*)?(days?|araw|weeks?|wks?|linggo|months?|buwan|years?|taon)\b"
)
UNIT_DAYS = {
    "day": 1, "days": 1, "araw": 1,
    "week": 7, "weeks": 7, "wk": 7, "wks": 7, "linggo": 7,
    "month": 30, "months": 30, "buwan": 30,
    "year": 365, "years": 365, "taon": 365,
}
QUOTE_PATTERN = re.compile(r"[\"\u201c\u201d]([^\"\u201c\u201d]+)[\"\u201c\u201d]")
HEARSAY_PATTERN = re.compile(r"\b([\w'-]+)\s+(?:daw|raw)\b")
