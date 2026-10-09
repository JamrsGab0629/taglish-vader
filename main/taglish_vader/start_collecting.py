"""
start_collecting.py - ONE command for the whole collector:

    python start_collecting.py                      # 8 s per page, max 100 pages
    python start_collecting.py --interval 10 --max-pages 40
    python start_collecting.py --scroll down        # page jumps to the top after Next
    python start_collecting.py --max-pages 5        # auto stops every 5 pages (press F10 again)

It watches your clipboard (saving the reviews into my_reviews.csv in THIS folder)
and listens for the hotkeys at the same time:
    F7  learn the Next button (manual step: hover over it first)
    F10 AUTO start/stop (copy + click Next every 8 seconds)
    F11 change which way it scrolls to find Next: up -> down -> both
    F8  manual copy + Next, F9 copy only, Esc quit
When you are done, run:   python run.py
"""

import argparse
import threading

import clip_collect
import hotkey_helper
from collect import OUT


def main():
    ap = argparse.ArgumentParser(description="Collector: clipboard watcher + Next-button helper")
    ap.add_argument("--interval", type=float, default=8.0,
                    help="AUTO mode: seconds per page (default 8, minimum 5)")
    ap.add_argument("--max-pages", type=int, default=100,
                    help="AUTO mode: stop after this many pages (default 100)")
    ap.add_argument("--scroll", choices=hotkey_helper.SCROLL_MODES, default="up",
                    help="scroll direction to find Next: up (default), down, or both. "
                         "Use down if the page jumps to the top after clicking Next. "
                         "F11 changes it while running.")
    ap.add_argument("--csv", default=OUT, help="where the reviews go (default: this folder)")
    a = ap.parse_args()

    stop = threading.Event()
    watcher = threading.Thread(target=clip_collect.watch, args=(a.csv, stop), daemon=True)
    watcher.start()
    try:
        hotkey_helper.run(a.interval, a.max_pages, a.scroll)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        watcher.join(timeout=3)
    print("\nFinished. Now run:  python run.py")


if __name__ == "__main__":
    main()