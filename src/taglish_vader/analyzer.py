"""
analyzer.py - the main Taglish VADER sentiment analyzer.

Works like VADER:
  1. Lexicon of words with scores (-4 to +4)
  2. Boosters / dampeners (sobra, grabe, medyo...)
  3. Negators (hindi, wala, di...)
  4. "But" rule (pero, kaso...): the part AFTER "pero" matters more
  5. ALL CAPS and "!" add emphasis
  6. Emojis / emoticons count too
  7. compound = score / sqrt(score^2 + 15)  ->  value from -1 to +1
Extras: spelling normalizer, question rule, domain phrases, star ratings,
sarcasm detector.
"""

import math
import re

from config import (
    BOOSTERS, NEGATORS, BUT_WORDS, BREAKERS,
    NEGATION_FACTOR, CAPS_BOOST, EXCLAIM_BOOST,
    POS_THRESHOLD, NEG_THRESHOLD, NORMALIZE_ALPHA,
    QUESTION_POS_FACTOR, QUESTION_NEG_FACTOR,
    STAR_STRENGTH, STAR_WEIGHT, SARCASM_MIN_NEG,
)
from lexicon import LEXICON, EMOTICONS
from normalizer import NORMALIZE
from ratings import detect_stars
from sarcasm import SarcasmDetector


def label_from_compound(c):
    if c >= POS_THRESHOLD:
        return "GOOD"
    if c <= NEG_THRESHOLD:
        return "BAD"
    return "NEUTRAL"


def _sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0


class TaglishSentimentAnalyzer:
    def __init__(self, lexicon=None, detect_sarcasm=True, use_stars=True):
        self.lexicon = dict(LEXICON if lexicon is None else lexicon)
        # longest multi-word phrase length (so "sulit na sulit" is matched first)
        self.max_phrase = max(len(k.split()) for k in self.lexicon)
        self.detect_sarcasm = detect_sarcasm
        self.use_stars = use_stars
        self.detector = SarcasmDetector(self)

    # ------------------------------------------------------------------
    def _tokenize(self, text):
        """Return list of (original_word, normalized_word)."""
        text = text.replace("\u2019", "'")
        raw = re.findall(r"\w+(?:['-]\w+)*|[^\w\s]", text, flags=re.UNICODE)
        tokens = []
        for w in raw:
            norm = w.lower()
            norm = re.sub(r"(.)\1{2,}", r"\1", norm)  # gandaaaa -> ganda
            norm = NORMALIZE.get(norm, norm)          # pngit -> pangit, d -> hindi
            tokens.append((w, norm))
        return self._merge_phrases(tokens)

    def _merge_phrases(self, tokens):
        merged, i = [], 0
        while i < len(tokens):
            for n in range(min(self.max_phrase, len(tokens) - i), 1, -1):
                phrase = " ".join(t[1] for t in tokens[i:i + n])
                if phrase in self.lexicon:
                    orig = " ".join(t[0] for t in tokens[i:i + n])
                    merged.append((orig, phrase))
                    i += n
                    break
            else:
                w = tokens[i][1]
                if (i + 2 < len(tokens) and tokens[i + 1][1] == "na"
                        and tokens[i + 2][1] == w and self._valence(w) != 0):
                    # "sarap na sarap": the same word twice is stronger
                    orig = " ".join(t[0] for t in tokens[i:i + 3])
                    merged.append((orig, f"{w} na {w}"))
                    i += 3
                else:
                    merged.append(tokens[i])
                    i += 1
        return merged

    def _valence(self, word):
        """Look up a word, also handles napakaganda / pinakamaganda."""
        if word in self.lexicon:
            return self.lexicon[word]
        m = re.fullmatch(r"(\w+) na \1", word)  # "sarap na sarap"
        if m:
            v = self._valence(m.group(1))
            if v:
                return v + 0.5 * _sign(v)
        w = word.replace("-", "")
        for prefix in ("napaka", "pinaka"):
            if w.startswith(prefix) and len(w) > len(prefix) + 2:
                rest = w[len(prefix):]
                v = self.lexicon.get(rest, self.lexicon.get("ma" + rest))
                if v is not None:
                    return v + BOOSTERS[prefix] * _sign(v)
        # same word twice = stronger:  "ganda-ganda"
        m = re.fullmatch(r"(\w+)-\1", word)
        if m:
            v = self._valence(m.group(1))
            if v:
                return v + 0.5 * _sign(v)
        # fused "ang":  "angganda", "ampangit", "ansulit"
        for prefix in ("ang", "am", "an"):
            rest = w[len(prefix):]
            if w.startswith(prefix) and len(rest) >= 4:
                v = self.lexicon.get(rest, self.lexicon.get("ma" + rest))
                if v is not None:
                    return v
        return 0.0

    # ------------------------------------------------------------------
    @staticmethod
    def _is_question(words, end):
        joined = " ".join(words)
        # tag questions like "diba?" ask for agreement, they are not real doubts
        if "diba" in words or "di ba" in joined or "hindi ba" in joined:
            return False
        return end == "?" or ("ba" in words and end != "!")

    def _apply_question_rule(self, tokens, scores):
        """Praise inside a question is ignored; complaints are kept but weaker."""
        start = 0
        for i, (_, w) in enumerate(tokens):
            last = i == len(tokens) - 1
            if w in (".", "!", "?") or last:
                end = w if w in (".", "!", "?") else ""
                words = [tokens[j][1] for j in range(start, i + 1)]
                if self._is_question(words, end):
                    for j in range(start, i + 1):
                        if scores[j] > 0:
                            scores[j] *= QUESTION_POS_FACTOR
                        elif scores[j] < 0:
                            scores[j] *= QUESTION_NEG_FACTOR
                start = i + 1

    def _check_sarcasm(self, text, result):
        """Flip sarcastic reviews to negative. Runs on the text score, before stars."""
        if self.detect_sarcasm:
            sarcasm = self.detector.detect(text, result["matched"])
        else:
            sarcasm = {"score": 0.0, "is_sarcastic": False, "reasons": []}
        result["original_compound"] = result["compound"]
        result["sarcasm"] = sarcasm
        if sarcasm["is_sarcastic"]:
            result["compound"] = round(-max(abs(result["compound"]), SARCASM_MIN_NEG), 4)
            result["pos"], result["neg"] = result["neg"], result["pos"]
        return result

    def _apply_stars(self, text, result, stars):
        if not self.use_stars:
            return result
        if stars is None:
            stars = detect_stars(text)
        if stars is None:
            return result
        stars = min(max(float(stars), 1.0), 5.0)
        star_value = round((stars - 3) / 2 * STAR_STRENGTH, 4)
        result["stars"] = stars
        result["text_compound"] = result["compound"]
        result["star_compound"] = star_value
        if result["matched"]:
            blended = (1 - STAR_WEIGHT) * result["compound"] + STAR_WEIGHT * star_value
        else:  # no sentiment words in the text -> the stars decide
            blended = star_value
        result["compound"] = round(blended, 4)
        return result

    # ------------------------------------------------------------------
    def polarity_scores(self, text, stars=None):
        """
        text  : the review
        stars : optional rating from 1 to 5 (if None, tries to find "5 stars" in the text)
        """
        tokens = self._tokenize(text)
        letters = [t[0] for t in tokens if t[0].isalpha()]
        has_mixed_case = any(w.isupper() for w in letters) and not all(
            w.isupper() for w in letters
        )

        scores = []
        but_index = None

        for i, (orig, word) in enumerate(tokens):
            if word in BUT_WORDS:
                but_index = i
            v = self._valence(word)
            if v == 0:
                scores.append(0.0)
                continue

            # ALL CAPS emphasis
            if has_mixed_case and orig.isupper() and len(orig) > 1:
                v += CAPS_BOOST * _sign(v)

            # boosters / dampeners in the previous 3 words
            for dist, scalar in zip((1, 2, 3), (1.0, 0.95, 0.9)):
                j = i - dist
                if j < 0 or tokens[j][1] in BREAKERS or tokens[j][1] in BUT_WORDS:
                    break
                b = BOOSTERS.get(tokens[j][1], 0.0)
                if b:
                    v += b * _sign(v) * scalar

            # negators in the previous 3 words
            for dist in (1, 2, 3):
                j = i - dist
                if j < 0 or tokens[j][1] in BREAKERS or tokens[j][1] in BUT_WORDS:
                    break
                if tokens[j][1] in NEGATORS:
                    v *= NEGATION_FACTOR
                    break

            scores.append(v)

        # "pero" / "but" rule
        if but_index is not None:
            for idx, s in enumerate(scores):
                if idx < but_index:
                    scores[idx] = s * 0.5
                elif idx > but_index:
                    scores[idx] = s * 1.5

        # question rule
        self._apply_question_rule(tokens, scores)

        matched = [
            (tokens[i][0], round(s, 2)) for i, s in enumerate(scores) if s != 0
        ]

        # text emoticons like :) :(
        for emo, val in EMOTICONS.items():
            c = text.count(emo)
            if c:
                scores.extend([val] * c)
                matched.append((emo, val))

        total = sum(scores)

        # "!" emphasis (max 4)
        ex = min(text.count("!"), 4) * EXCLAIM_BOOST
        if total > 0:
            total += ex
        elif total < 0:
            total -= ex

        compound = total / math.sqrt(total * total + NORMALIZE_ALPHA)
        compound = round(max(-1.0, min(1.0, compound)), 4)

        # pos / neg / neu proportions (same idea as VADER)
        pos = sum(s + 1 for s in scores if s > 0)
        neg = sum(s - 1 for s in scores if s < 0)
        neu = sum(1 for s in scores if s == 0)
        if total > 0:
            pos += ex
        elif total < 0:
            neg -= ex
        denom = pos + abs(neg) + neu
        if denom == 0:
            pos_r = neg_r = 0.0
            neu_r = 1.0
        else:
            pos_r, neg_r, neu_r = pos / denom, abs(neg) / denom, neu / denom

        result = {
            "neg": round(neg_r, 3),
            "neu": round(neu_r, 3),
            "pos": round(pos_r, 3),
            "compound": compound,
            "matched": matched,
            "stars": None,
        }
        result = self._check_sarcasm(text, result)
        return self._apply_stars(text, result, stars)

    def classify(self, text, stars=None):
        return label_from_compound(self.polarity_scores(text, stars)["compound"])
