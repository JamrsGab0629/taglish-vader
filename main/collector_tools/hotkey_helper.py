"""
hotkey_helper.py - find the "Next" button, copy the page, click "Next".
Two ways to use it:

  MANUAL  (F8)   one key press = copy this page + click Next. 2-second cooldown.
  AUTO    (F10)  press F10 once to START, press F10 again (or Esc) to STOP.
                 It repeats copy + click Next, with a fixed pause between pages
                 (default 8 seconds).

Keys:  F7  = learn the Next button (hover exactly over its center first)
       F8  = manual: find Next (scrolls up if needed), copy the page, click Next
       F9  = copy the page only (use on the LAST page when doing it manually)
       F10 = start / stop AUTO mode
       Esc = stop auto mode and quit

AUTO mode stops by itself when:
  - the Next button can't be found  (last page: it copies that page first)
  - the copied page is the same twice in a row (the click didn't work / stuck)
  - it reaches --max-pages
  - you move the mouse to the top-left corner of the screen (pyautogui fail-safe)
  - a keyboard / mouse error happens

Usage:  python hotkey_helper.py                          # 8 s per page, max 100 pages
        python hotkey_helper.py --interval 10 --max-pages 40
Run clip_collect.py in another terminal first (it saves what gets copied).
Keep the browser window in front and DON'T touch the mouse while AUTO is running.

Needs: pip install pyautogui pynput pillow opencv-python pyperclip
Mac:   allow your terminal in System Settings > Privacy & Security >
       Accessibility AND Screen Recording.
"""

import argparse
import os
import sys
import threading
import time

import pyautogui
import pyperclip
from pynput import keyboard

MOD = "command" if sys.platform == "darwin" else "ctrl"
TEMPLATE = "next_button.png"
BOX_W, BOX_H = 36, 28      # size of the picture taken of the Next button (pixels)
COOLDOWN = 2.0             # seconds between MANUAL presses
MIN_INTERVAL = 5.0         # AUTO will never go faster than this
last_press = 0.0

auto_thread = None
auto_stop = threading.Event()
settings = {"interval": 8.0, "max_pages": 100}


def grab():
    """Screenshot + scale (screen pixels per mouse unit; 2 on Retina displays)."""
    img = pyautogui.screenshot()
    return img, img.width / pyautogui.size().width


def save_template():
    pos = pyautogui.position()
    pyautogui.moveTo(pos.x, max(pos.y - 200, 0))  # move away so hover color doesn't matter
    time.sleep(0.4)
    img, scale = grab()
    box = (
        int((pos.x - BOX_W / 2) * scale), int((pos.y - BOX_H / 2) * scale),
        int((pos.x + BOX_W / 2) * scale), int((pos.y + BOX_H / 2) * scale),
    )
    img.crop(box).save(TEMPLATE)
    print(f"Saved a picture of the Next button -> {TEMPLATE}")
    print("Open it to check it shows only the button (not page numbers). Redo F7 if not.")


def find_next():
    """Return (x, y) of the Next button on screen, or None."""
    if not os.path.exists(TEMPLATE):
        return None
    img, scale = grab()
    try:
        boxes = list(pyautogui.locateAll(TEMPLATE, img, confidence=0.85))
    except NotImplementedError:          # OpenCV not installed -> exact match only
        try:
            boxes = list(pyautogui.locateAll(TEMPLATE, img))
        except Exception:
            boxes = []
    except Exception:
        boxes = []
    if not boxes:
        return None
    b = max(boxes, key=lambda b: (b.top, b.left))   # pager is at the bottom
    return (b.left + b.width / 2) / scale, (b.top + b.height / 2) / scale


def find_next_scrolling(max_steps=10):
    """Look on screen; if the pager isn't visible, scroll UP in small steps and look again."""
    for _ in range(max_steps):
        pos = find_next()
        if pos:
            return pos
        pyautogui.scroll(360)    # positive = scroll up (about 3 mouse-wheel notches)
        time.sleep(0.5)
    return None


def do_copy():
    pyautogui.hotkey(MOD, "a")
    pyautogui.hotkey(MOD, "c")
    time.sleep(0.4)  # let clip_collect.py catch the copy


# ------------------------------- AUTO MODE -------------------------------------
def auto_loop(interval, max_pages):
    pages, repeats, prev = 0, 0, None
    print(f"AUTO started: {interval:g} s per page, up to {max_pages} pages. "
          "F10 or Esc stops it. Don't touch the mouse.")
    try:
        while not auto_stop.is_set() and pages < max_pages:
            started = time.time()
            pos = find_next_scrolling()
            if pos is None:
                do_copy()
                pages += 1
                print(f"AUTO: Next not found, so copied page {pages} as the LAST page. Stopped.")
                return
            do_copy()
            text = pyperclip.paste()
            repeats = repeats + 1 if text == prev else 0
            prev = text
            if repeats >= 2:
                print("AUTO: the same page was copied 3 times in a row (stuck). Stopped.")
                return
            pyautogui.click(*pos)
            pages += 1
            print(f"AUTO: page {pages} copied, clicked Next.")
            # fixed pause so the next page can load; measured from the start of this page
            auto_stop.wait(max(0.0, interval - (time.time() - started)))
        if pages >= max_pages:
            print(f"AUTO: reached --max-pages ({max_pages}). Stopped.")
        else:
            print(f"AUTO: stopped by you after {pages} pages.")
    except pyautogui.FailSafeException:
        print("AUTO: mouse hit the screen corner (fail-safe). Stopped.")
    except Exception as e:
        print("AUTO: error, stopped:", e)
    finally:
        auto_stop.set()


def auto_running():
    return auto_thread is not None and auto_thread.is_alive()


def toggle_auto():
    global auto_thread
    if auto_running():
        auto_stop.set()
        print("Stopping AUTO after the current step...")
        return
    if not os.path.exists(TEMPLATE):
        print("Press F7 first (hover over Next) so I know what the button looks like.")
        return
    auto_stop.clear()
    auto_thread = threading.Thread(
        target=auto_loop, args=(settings["interval"], settings["max_pages"]), daemon=True
    )
    auto_thread.start()


# ------------------------------- KEYS ------------------------------------------
def on_press(key):
    global last_press
    try:
        if key == keyboard.Key.esc:
            auto_stop.set()
            return False
        if key == keyboard.Key.f10:
            toggle_auto()
        elif key == keyboard.Key.f7:
            if auto_running():
                print("AUTO is running. Press F10 to stop it first.")
            else:
                save_template()
        elif key in (keyboard.Key.f8, keyboard.Key.f9):
            if auto_running():
                print("AUTO is running. Press F10 to stop it first.")
                return
            now = time.time()
            if now - last_press < COOLDOWN:
                print("Slow down: wait for the page to load, then press again.")
                return
            last_press = now
            if key == keyboard.Key.f9:
                do_copy()
                print("Copied this page (no click).")
                return
            pos = find_next_scrolling()  # looks here first, then scrolls up
            if pos is None:
                print("Can't see the Next button. Last page? Press F9 to copy it. "
                      "Otherwise scroll so the pager is visible and press F8 again.")
                return
            do_copy()
            pyautogui.click(*pos)
            print("Copied and clicked Next. Wait for the new page to load.")
    except Exception as e:                # keep the listener alive on errors
        print("Error:", e)


def main():
    ap = argparse.ArgumentParser(description="Copy + Next helper (manual F8 / auto F10)")
    ap.add_argument("--interval", type=float, default=8.0,
                    help="AUTO mode: seconds per page (default 8, minimum 5)")
    ap.add_argument("--max-pages", type=int, default=100,
                    help="AUTO mode: stop after this many pages (default 100)")
    a = ap.parse_args()
    settings["interval"] = max(a.interval, MIN_INTERVAL)
    settings["max_pages"] = max(a.max_pages, 1)
    print("F7 = learn Next button, F8 = copy + Next (manual), F9 = copy only,")
    print(f"F10 = AUTO start/stop ({settings['interval']:g} s per page, max {settings['max_pages']} pages), Esc = quit")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    main()