import csv
import re
import time
import pyperclip

def clean_review_content(content: str) -> str:
    return " — ".join(
        line.strip()
        for line in content.splitlines()
        if line.strip()
        and not re.match(r"^[A-Za-z0-9\s/&_-]{2,30}\s*:", line.strip())
        and not re.match(r"^\d+$", line.strip())
        and line.strip().lower() not in ["profile", "..."]
    )

def filterClipboard(text=""):
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\b\d{1,2}:\d{2}\b", "", text)

    getReviews = re.search(r"Product Ratings\s+(.*?)\s+From The Same Shop", text, re.DOTALL)
    reviews_text = getReviews.group(1) if getReviews else text

    date_matches = list(re.finditer(r"(\d{4}-\d{2}-\d{2})", reviews_text))

    if not date_matches:
        return "No match found"

    reviews = []

    for i in range(len(date_matches)):
        current_date_match = date_matches[i]
        date_str = current_date_match.group(1)
        content_start = current_date_match.end()

        if i + 1 < len(date_matches):
            next_date_match = date_matches[i + 1]
            next_user_text = reviews_text[content_start : next_date_match.start()]
            lines_between = [l.strip() for l in next_user_text.split("\n") if l.strip()]

            if lines_between:
                last_line = lines_between[-1]
                if last_line.lower() == "profile" and len(lines_between) > 1:
                    last_line = lines_between[-2]

                content_end = current_date_match.end() + next_user_text.rstrip().rfind(last_line)
            else:
                content_end = next_date_match.start()
        else:
            content_end = len(reviews_text)

        raw_content = reviews_text[content_start:content_end]
        clean_content = re.sub(r"^\s*\|\s*Variation:[^\n]*", "", raw_content).strip()
        clean_content = re.sub(r"^\s*\|\s*", "", clean_content).strip()

        if i == 0:
            prior_text = reviews_text[: current_date_match.start()]
        else:
            prev_date_match = date_matches[i - 1]
            prior_text = reviews_text[prev_date_match.end() : current_date_match.start()]

        prior_lines = [l.strip() for l in prior_text.split("\n") if l.strip()]

        username = "Unknown"
        if prior_lines:
            filtered_lines = [
                l for l in prior_lines 
                if l.lower() != "profile" 
                and not re.match(r"^review\s*#\d+", l.lower()) 
                and not l.isdigit()
            ]
            if filtered_lines:
                username = filtered_lines[-1]

        # Put review content into 'review', leave 'rating' empty
        reviews.append([
            clean_review_content(clean_content),
            "none"
        ])

    return reviews

def paperclip(filepath="reviews.csv"):
    i = 0
    last_text = ""

    try:
        # Check if file exists to determine whether to write headers
        try:
            with open(filepath, "r", encoding="utf-8"):
                file_exists = True
        except FileNotFoundError:
            file_exists = False

        review_file = open(filepath, mode="a", newline="", encoding="utf-8")
        writer = csv.writer(review_file)

        # Header with review and rating
        if not file_exists:
            writer.writerow(['review', 'rating'])
            review_file.flush()

        print("Monitoring clipboard... Copy review text (Ctrl+C). Press Ctrl+C in terminal to stop.")

        while True:
            try:
                current_text = pyperclip.paste()
                if current_text != last_text and current_text.strip():
                    last_text = current_text

                    reviews = filterClipboard(current_text)
                    if reviews == "No match found":
                        raise ValueError("No Found Match")

                    for r in reviews:
                        writer.writerow(r)
                        review_file.flush()
                        # print("-" * 20)
                        print(f"review #{i}")
                        i += 1

            except ValueError as e:
                print(f"\n[Error] Processing failed: {e}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[Stopped] Clipboard monitoring ended.")
    finally:
        try:
            review_file.close()
        except UnboundLocalError:
            pass

if __name__ == "__main__":
    paperclip()