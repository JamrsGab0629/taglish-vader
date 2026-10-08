# Review collection tools (manual, no bot)

You browse Shopee yourself at normal speed. These scripts only read your clipboard
and clean the text on your computer.

Setup:  pip install pyperclip pyautogui pynput pillow opencv-python

Put all the files in your taglish_vader folder (they import each other).

Per star level (5, 4, 3, 2, 1):
1. In your browser, filter reviews to ONE star level. Set zoom to about 50% and scroll so the
   review page buttons (with "Next") are on screen. Do NOT press End: on Shopee it jumps past them.
2. Terminal 1:  python clip_collect.py --rating 5      (use the star level you filtered)
3. Terminal 2:  python hotkey_helper.py
4. Hover over the center of "Next" and press F7 once (it saves next_button.png: check it shows
   only the button). Then press F8 once per page, and F9 on the LAST page (Next greyed out).
   After each page, terminal 1 prints:  page 3: +9 reviews (0 duplicates skipped) -> my_reviews.csv
5. Esc in terminal 2, Ctrl+C in terminal 1 when done. Change the filter and repeat for the next star.

Then:  python main.py --file my_reviews.csv

The reviews go straight into my_reviews.csv (only the review text + the star rating, duplicates
skipped). Each raw copied page is also saved to raw_pages_5star.txt, so clean_paste.py can
re-process it if you ever change the rules. clean_paste.py, collect.py, and tidy_csv.py still
work on their own for old files.

How it works: every Shopee review has a date line. The review text is what follows it,
until "Helpful" / "Report" / the seller's reply / page buttons / the next review. Multi-line
reviews are joined into one line, and one-word reviews like "Good" are kept. Menus, product
info, and usernames never follow a date line, so they are left out.

Rules: press F8 yourself (it has a 2-second cooldown; never loop it), leave out usernames
and photos, and note in your write-up that the sample was collected manually (date + products).
