"""
hotkey_helper.py - one key press = find the pager, copy the page, click "Next".
It FINDS the Next button on your screen each time, so it does not matter that the
button moves when reviews are longer or shorter.

You press the key yourself at normal speed. A 2-second cooldown stops you from
holding the key down. Do NOT turn this into a loop; that would make it a bot.

Keys:  F7 = learn the Next button (hover exactly over its center first)
       F8 = find Next (scrolls up if needed), copy the page, click Next
       F9 = copy the page only (use this on the LAST page, where Next is greyed out)
       Esc = quit
Needs: pip install pyautogui pynput pillow opencv-python
Mac:   allow your terminal in System Settings > Privacy & Security >
       Accessibility AND Screen Recording.
"""

import os
import sys
import time

import pyautogui
from pynput import keyboard

MOD = "command" if sys.platform == "darwin" else "ctrl"
TEMPLATE = "next_button.png"
BOX_W, BOX_H = 36, 28      # size of the picture taken of the Next button (pixels)
COOLDOWN = 2.0             # seconds between presses (keeps it human-paced)
last_press = 0.0


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


def on_press(key):
    global last_press
    try:
        if key == keyboard.Key.f7:
            save_template()
        elif key in (keyboard.Key.f8, keyboard.Key.f9):
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
        elif key == keyboard.Key.esc:
            return False
    except Exception as e:                # keep the listener alive on errors
        print("Error:", e)


print("F7 = learn Next button, F8 = copy + Next, F9 = copy only, Esc = quit")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
