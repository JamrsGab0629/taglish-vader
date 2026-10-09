# Taglish VADER + review collector (one folder)

Everything is in this one folder, so the collector saves straight into it and
`run.py` reads straight from it. **Star ratings are not used anywhere.** Nothing
guesses a label from the stars; labels come from the review text only.

Setup (once):  `pip install pyperclip pyautogui pynput pillow opencv-python`

## 1. Collect  ->  `python start_collecting.py`

1. In your browser, open the reviews. Zoom to about 50% and scroll so the page
   buttons ("Next") are on screen. Do NOT press End (on Shopee it jumps past them).
   You can collect ALL star levels together now: no filter or flag is needed, which
   also gives you the 2-4 star reviews that make up your NEUTRAL cases.
2. Run `python start_collecting.py` (optional: `--interval 10 --max-pages 40`).
3. **Manual step:** hover over the center of "Next" and press **F7**. It saves
   `next_button.png`; open it and check it shows only the button. Redo F7 if the
   zoom or layout changes.
4. **Automatic:** press **F10**. It copies the page and clicks Next every 8 seconds
   (never faster than 5). The reviews are saved to `my_reviews.csv` in this folder
   as it goes. Press F10 or Esc to stop.
   - **Scroll direction:** if the Next button isn't on screen the helper scrolls to find it.
     Default is up. If the page jumps to the TOP after clicking Next, use
     `python start_collecting.py --scroll down` (or `both`). Press **F11** while it runs to
     switch up -> down -> both.
   - F8 = one manual copy + Next, F9 = copy only, Esc = quit.
   - AUTO stops by itself on the last page, if the same page is copied 3 times in a
     row, at `--max-pages`, or if you move the mouse to the top-left screen corner.
   - Stay nearby. Stop it if Shopee shows a captcha, a login wall or an error page.
   - Automated collection may go against Shopee's terms. Use it at your own risk, keep
     the page count modest, and say in your write-up that pages were auto-paged.

## 2. Label  ->  `python run.py`

Labels every review in `my_reviews.csv` GOOD / NEUTRAL / BAD (text only) and writes
`my_reviews_results.csv` (columns: `text_label`, `text_score`, `sarcasm`). It also
lists words the analyzer doesn't know yet.

## 3. Measure it honestly (recommended)

Stars are not the truth, so don't grade against them. Open `my_reviews.csv`, add a
column named `human_label`, and fill in GOOD / NEUTRAL / BAD yourself (a second
person labeling too is even better). Run `python run.py` again: the report now shows
accuracy and a table against YOUR labels. Add new words to `lexicon.py` using only
the first part of your reviews, and test on the rest.

## What gets saved from each review

Only the reviewer's own words. The seller's form labels ("Appearance:", "Colour:", "Material:"),
the date/variation line, usernames, video lengths ("0:12"), and the "Helpful?" row are cut.
To re-clean a `my_reviews.csv` you already made with these rules: `python tidy_csv.py`.

## Files

- `start_collecting.py` runs the clipboard watcher and the hotkeys together
- `clip_collect.py` clipboard watcher (saves reviews to `my_reviews.csv`, raw pages to `raw_pages.txt`)
- `hotkey_helper.py` finds the Next button, copies, clicks
- `clean_paste.py` cleaning rules (re-clean saved pages: `python clean_paste.py raw_pages.txt clean.txt`, then `python collect.py --import clean.txt`)
- `collect.py` adds reviews to `my_reviews.csv` (type them, or `--import file.txt`)
- `tidy_csv.py` re-cleans an old `my_reviews.csv` and removes any rating column
- `run.py`, `batch.py`, `main.py` (demo: `python main.py`), `analyzer.py`, `lexicon.py`, `normalizer.py`, `config.py`, `sarcasm.py` the analyzer