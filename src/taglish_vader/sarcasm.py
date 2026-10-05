"""
sarcasm.py - sarcasm detector.
Adds up clues (see config.py). At SARCASM_THRESHOLD the review counts as
sarcastic and the analyzer flips it to negative.

It receives the analyzer in __init__ (to look up word scores), so it never
imports analyzer.py - no circular imports.
"""

import re

from config import (
    BUT_WORDS, SARCASM_MARKERS, SARCASM_EMOJIS, SARCASM_THRESHOLD,
    STRONG_WORD_SCORE, MARKER_CAP, EMOJI_CAP, MIXED_POLARITY_POINTS,
    HEARSAY_POINTS, QUOTED_POINTS, DELAY_POINTS, LONG_WAIT_DAYS,
    SPEED_PATTERN, DURATION_PATTERN, UNIT_DAYS, QUOTE_PATTERN, HEARSAY_PATTERN,
)


class SarcasmDetector:
    def __init__(self, analyzer):
        self.analyzer = analyzer

    def detect(self, text, matched):
        """
        text    : the review
        matched : list of (word, score) from the sentiment analyzer
        returns : dict(score, is_sarcastic, reasons)
        """
        t = text.lower().replace("\u2019", "'")
        t = re.sub(r"(.)\1{2,}", r"\1", t)  # wowwww -> wow

        pos = [s for _, s in matched if s > 0]
        strong_pos = [s for s in pos if s >= STRONG_WORD_SCORE]
        strong_neg = [s for _, s in matched if s <= -STRONG_WORD_SCORE]

        score, reasons, has_strong_marker = 0.0, [], False

        # 1) sarcasm phrases
        marker_pts = 0.0
        for phrase, pts in SARCASM_MARKERS.items():
            if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", t):
                marker_pts += pts
                reasons.append(f"sarcasm phrase '{phrase}' (+{pts})")
                if pts >= 2.0:
                    has_strong_marker = True
        score += min(marker_pts, MARKER_CAP)

        # Sarcasm needs a nice-sounding surface (or a very strong phrase)
        if not pos and not has_strong_marker:
            return {"score": 0.0, "is_sarcastic": False, "reasons": []}

        # 2) positive + negative words, with no "pero" to explain the contrast
        words = re.findall(r"\w+", t)
        has_but = any(w in BUT_WORDS for w in words)
        if strong_pos and strong_neg and not has_but:
            score += MIXED_POLARITY_POINTS
            reasons.append(
                f"positive and negative words together, no 'pero' (+{MIXED_POLARITY_POINTS})"
            )

        # 3) sarcastic emojis
        emoji_pts = 0.0
        for emo, pts in SARCASM_EMOJIS.items():
            if emo in text:
                emoji_pts += pts
                reasons.append(f"sarcastic emoji {emo} (+{pts})")
        score += min(emoji_pts, EMOJI_CAP)

        # 4) "maganda daw" / "original raw"
        for m in HEARSAY_PATTERN.finditer(t):
            if self.analyzer._valence(m.group(1)) > 0:
                score += HEARSAY_POINTS
                reasons.append(f"'{m.group(0)}' sounds doubtful (+{HEARSAY_POINTS})")
                break

        # 5) positive word inside "quotes"
        for q in QUOTE_PATTERN.finditer(text.lower()):
            if any(self.analyzer._valence(w) > 0 for w in re.findall(r"\w+", q.group(1))):
                score += QUOTED_POINTS
                reasons.append(f"positive word in quotes {q.group(0)} (+{QUOTED_POINTS})")
                break

        # 6) "mabilis" + a long wait
        if SPEED_PATTERN.search(t):
            longest = 0
            for num, unit in DURATION_PATTERN.findall(t):
                longest = max(longest, int(num) * UNIT_DAYS[unit])
            if longest >= LONG_WAIT_DAYS:
                score += DELAY_POINTS
                reasons.append(f"says 'fast' but waited ~{longest} days (+{DELAY_POINTS})")

        return {
            "score": round(score, 2),
            "is_sarcastic": score >= SARCASM_THRESHOLD,
            "reasons": reasons,
        }
