"""
analyzer.py - the main Taglish VADER sentiment analyzer.

Works like VADER, from the TEXT ONLY (star ratings are never used):
  1. Lexicon of words with scores (-4 to +4)
  2. Boosters / dampeners (sobra, grabe, medyo...)
  3. Negators (hindi, wala, di...)
  4. "But" rule (pero, kaso...): the part AFTER "pero" matters more
  5. ALL CAPS and "!" add emphasis
  6. Emojis / emoticons count too
  7. compound = score / sqrt(score^2 + 15)  ->  value from -1 to +1
Extras: spelling normalizer, question rule, domain phrases, "fast + bad thing",
"hindi ma connect" rule, sarcasm detector.
"""

import math
import re

from config import (
    BOOSTERS, NEGATORS, BUT_WORDS, BREAKERS,
    NEGATION_FACTOR, CAPS_BOOST, EXCLAIM_BOOST,
    POS_THRESHOLD, NEG_THRESHOLD, NORMALIZE_ALPHA,
    QUESTION_POS_FACTOR, QUESTION_NEG_FACTOR, SARCASM_MIN_NEG,
    POLITE_WORDS, POLITE_AFTER_BUT,
    NEEDS_TO_WORK, FAIL_SCORE, NEGATION_WINDOW,
    SPEED_WORD, NEGATIVE_EVENTS,
    WISH_WORDS, WISH_SKIP, WISH_SCORE, WISH_MIN, RATING_IN_TEXT, RATING_SCORE,
    NEGATION_WINDOW_NEG,
)
from lexicon import LEXICON, EMOTICONS
from normalizer import NORMALIZE
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
    def __init__(self, lexicon=None, detect_sarcasm=True):
        self.lexicon = dict(LEXICON if lexicon is None else lexicon)
        # longest multi-word phrase length (so "sulit na sulit" is matched first)
        self.max_phrase = max(len(k.split()) for k in self.lexicon)
        self.detect_sarcasm = detect_sarcasm
        self.detector = SarcasmDetector(self)

    # ------------------------------------------------------------------
    def _tokenize(self, text):
        """Return list of (original_word, normalized_word)."""
        text = text.replace("’", "'")
        raw = re.findall(r"\w+(?:['-]\w+)*|[^\w\s]", text, flags=re.UNICODE)
        tokens = []
        for w in raw:
            norm = w.lower()
            norm = re.sub(r"(.)\1{2,}", r"\1", norm)  # gandaaaa -> ganda
            norm = NORMALIZE.get(norm, norm)          # pngit -> pangit, d -> hindi
            tokens.append((w, norm))
        return self._merge_phrases(self._join_prefixes(tokens))

    def _join_prefixes(self, tokens):
        """'nakaka dismaya' -> 'nakakadismaya', 'napaka ganda' -> 'napakaganda'."""
        out, i = [], 0
        while i < len(tokens):
            w = tokens[i][1]
            if (w in ("nakaka", "napaka", "pinaka") and i + 1 < len(tokens)
                    and tokens[i + 1][1].isalpha()):
                joined = w + tokens[i + 1][1]
                if self._valence(joined) != 0:
                    out.append((tokens[i][0] + " " + tokens[i + 1][0], joined))
                    i += 2
                    continue
            out.append(tokens[i])
            i += 1
        return out

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
        for prefix in ("napaka", "pinaka", "apaka"):
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
    def _negated(tokens, i, window):
        """Is there a negator in the `window` words before token i (same clause)?"""
        for dist in range(1, window + 1):
            j = i - dist
            if j < 0 or tokens[j][1] in BREAKERS or tokens[j][1] in BUT_WORDS:
                return False
            if tokens[j][1] in NEGATORS:
                return True
        return False

    @staticmethod
    def _bad_event_follows(tokens, i):
        """'ang bilis malowbat': a bad event within the next 2 words (same clause)."""
        for dist in (1, 2):
            j = i + dist
            if j >= len(tokens) or tokens[j][1] in BREAKERS or tokens[j][1] in BUT_WORDS:
                return False
            if tokens[j][1] in NEGATIVE_EVENTS:
                return True
        return False

    @staticmethod
    def _wish_follows(tokens, i):
        """'maganda sana', 'maganda naman sana': a wish, not praise."""
        for dist in (1, 2, 3):
            j = i + dist
            if j >= len(tokens):
                return False
            w = tokens[j][1]
            if w in WISH_WORDS:
                return True
            if w not in WISH_SKIP:
                return False
        return False

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
        """Flip sarcastic reviews to negative."""
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

    # ------------------------------------------------------------------
    def polarity_scores(self, text):
        """text: the review. Returns neg/neu/pos, compound (-1..+1), matched words, sarcasm."""
        tokens = self._tokenize(text)
        letters = [t[0] for t in tokens if t[0].isalpha()]
        has_mixed_case = any(w.isupper() for w in letters) and not all(
            w.isupper() for w in letters
        )

        scores = []
        but_positions = []

        for i, (orig, word) in enumerate(tokens):
            if word in BUT_WORDS:
                but_positions.append(i)

            # "hindi ma connect", "not working": something that must work, but doesn't
            if word in NEEDS_TO_WORK and self._negated(tokens, i, NEGATION_WINDOW):
                scores.append(FAIL_SCORE)
                continue

            v = self._valence(word)
            if v == 0:
                scores.append(0.0)
                continue

            # "ang bilis malowbat": fast + a bad event is not praise
            if v > 0 and SPEED_WORD.match(word) and self._bad_event_follows(tokens, i):
                scores.append(0.0)
                continue

            # "maganda sana ...": it would have been nice = it was NOT nice
            if v >= WISH_MIN and word not in POLITE_WORDS and self._wish_follows(tokens, i):
                scores.append(WISH_SCORE)
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

            # negators in the previous 3 words (2 for a complaint word). A negator belongs
            # to the nearest sentiment word: "not worth waste of money" negates "worth" only.
            # Politeness ("thanks") is never negated.
            if word not in POLITE_WORDS:
                for dist in range(1, (3 if v > 0 else NEGATION_WINDOW_NEG) + 1):
                    j = i - dist
                    if j < 0 or tokens[j][1] in BREAKERS or tokens[j][1] in BUT_WORDS:
                        break
                    if tokens[j][1] in NEGATORS:
                        v *= NEGATION_FACTOR
                        break
                    if self._valence(tokens[j][1]) != 0:
                        break

            scores.append(v)

        # "pero" / "but" rule. A "but" only counts when a real opinion follows it:
        # "...doesn't fit, i dunno why but ty seller" -> the verdict is the first "but".
        but_index = None
        for b in but_positions:
            if any(scores[k] != 0 and tokens[k][1] not in POLITE_WORDS
                   for k in range(b + 1, len(scores))):
                but_index = b
        if but_index is not None:
            for idx, s in enumerate(scores):
                if idx < but_index:
                    scores[idx] = s * 0.5
                elif idx > but_index:
                    polite = tokens[idx][1] in POLITE_WORDS
                    scores[idx] = s * (POLITE_AFTER_BUT if polite else 1.5)

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

        # a score the reviewer wrote: "10/10", "9/9", "2/10"
        for m in RATING_IN_TEXT.finditer(text):
            num, den = float(m.group(1)), float(m.group(2))
            if den <= 0 or num > den or not (den in (5, 10) or num == den):
                continue
            ratio = num / den
            val = RATING_SCORE if ratio >= 0.8 else -RATING_SCORE if ratio <= 0.4 else 0
            if val:
                scores.append(val)
                matched.append((m.group(0), val))

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
        }
        return self._check_sarcasm(text, result)

    def classify(self, text):
        return label_from_compound(self.polarity_scores(text)["compound"])
