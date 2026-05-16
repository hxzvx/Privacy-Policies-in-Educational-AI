import os
from datetime import datetime
import polipy
import textstat
import time
import random
import requests

# =========================
# PATH SETUP
# =========================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

URLS_FILE = os.path.join(BASE_DIR, "urls", "privacy_urls.txt")
EXTRACTED_FOLDER = os.path.join(BASE_DIR, "extracted_texts")
RESULTS_FOLDER = os.path.join(BASE_DIR, "results")
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "P_downloads")  # optional backup storage

os.makedirs(EXTRACTED_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# =========================
# HELPERS
# =========================
def safe_name_from_url(url: str) -> str:
    """
    Convert a URL into a short safe filename.
    Example:
    https://buddy.ai/en/privacy -> buddy
    """
    try:
        domain = url.split("//")[-1].split("/")[0].replace("www.", "")
        name = domain.split(".")[0]
        return name if name else "policy"
    except Exception:
        return "policy"


def get_policy_text(policy):
    """
    PoliPy content may be stored in slightly different structures.
    This tries to safely extract the main text.
    """
    content = policy.content

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, dict):
        # most likely keys
        preferred_keys = ["text", "content", "clean_text", "body"]
        for key in preferred_keys:
            if key in content and isinstance(content[key], str):
                return content[key].strip()

        # fallback: first string value found
        for value in content.values():
            if isinstance(value, str) and value.strip():
                return value.strip()

    return ""


def analyze_text(text: str, name: str) -> dict:
    """
    Compute readability metrics for one text.
    """
    word_count = textstat.lexicon_count(text, removepunct=True)
    sentence_count = textstat.sentence_count(text)
    avg_sentence_length = round(word_count / sentence_count, 2) if sentence_count > 0 else 0

    return {
        "name": name,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sentence_length,
        "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(text), 2),
        "flesch_reading_ease": round(textstat.flesch_reading_ease(text), 2),
        "gunning_fog": round(textstat.gunning_fog(text), 2),
    }


def save_text_file(path: str, text: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def load_urls(file_path: str) -> list[str]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"URLs file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    return urls


# =========================
# MAIN PIPELINE
# =========================
def fetch_with_retries(url, retries=5, delay=1):
    """
    Retry logic with exponential backoff to handle connection issues
    """
    for attempt in range(retries):
        try:
            # Attempt to fetch the policy
            policy = polipy.get_policy(url)
            return policy  # Successfully fetched
        except (requests.exceptions.RequestException, ConnectionResetError) as e:
            print(f"Attempt {attempt + 1} failed: {e}")

        # Wait before retrying with increasing delay
        time.sleep(delay * (2 ** attempt) + random.uniform(0, 1))  # Exponential backoff with jitter

    print(f"Failed to retrieve policy after {retries} retries.")
    return None


def main():
    print("=" * 70)
    print("Privacy Policy Extraction + Readability Analysis")
    print("=" * 70)
    print(f"Base directory      : {BASE_DIR}")
    print(f"URLs file           : {URLS_FILE}")
    print(f"Extracted texts dir : {EXTRACTED_FOLDER}")
    print(f"Results dir         : {RESULTS_FOLDER}")
    print(f"Downloads dir       : {DOWNLOAD_FOLDER}")
    print("=" * 70)

    try:
        urls = load_urls(URLS_FILE)
    except Exception as e:
        print(f"Error loading URLs: {e}")
        return

    if not urls:
        print("No URLs found in privacy_urls.txt")
        return

    print(f"Found {len(urls)} URL(s).\n")

    all_results = []

    for i, url in enumerate(urls, start=1):
        print(f"[{i}/{len(urls)}] Processing: {url}")

        site_name = safe_name_from_url(url)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        extracted_txt_path = os.path.join(EXTRACTED_FOLDER, f"{site_name}_{timestamp}.txt")
        raw_backup_path = os.path.join(DOWNLOAD_FOLDER, f"{site_name}_{timestamp}_raw.txt")

        # Fetch the policy with retries
        policy = fetch_with_retries(url)

        if not policy:
            print(f"Skipping {url} due to failed retrieval.")
            continue

        try:
            # Optional: save PoliPy output folder if supported
            try:
                policy_output_dir = os.path.join(DOWNLOAD_FOLDER, f"{site_name}_{timestamp}")
                policy.save(policy_output_dir)
                print(f"  Saved PoliPy output to: {policy_output_dir}")
            except Exception as save_err:
                print(f"  PoliPy save skipped: {save_err}")

            text = get_policy_text(policy)

            if not text:
                print("  No text extracted. Skipping.")
                continue

            if len(text.split()) < 100:
                print(f"  Warning: extracted text is short ({len(text.split())} words).")

            # Save extracted text
            save_text_file(extracted_txt_path, text)
            save_text_file(raw_backup_path, text)

            print(f"  Extracted text saved to: {extracted_txt_path}")

            # Analyze
            result = analyze_text(text, site_name)
            result["url"] = url
            result["text_file"] = os.path.basename(extracted_txt_path)

            all_results.append(result)

            print(f"  FK Grade      : {result['flesch_kincaid_grade']}")
            print(f"  Reading Ease  : {result['flesch_reading_ease']}")
            print(f"  Gunning Fog   : {result['gunning_fog']}")
            print()

        except Exception as e:
            print(f"  Error processing {url}: {e}\n")

    if not all_results:
        print("No policies were successfully processed.")
        return

    # Save final results
    results_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(RESULTS_FOLDER, f"analysis_results_{results_timestamp}.txt")

    with open(results_file, "w", encoding="utf-8") as f:
        f.write("Privacy Policy Readability Analysis\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Policies analyzed: {len(all_results)}\n\n")

        for r in all_results:
            f.write(f"Name: {r['name']}\n")
            f.write(f"URL: {r['url']}\n")
            f.write(f"Extracted text file: {r['text_file']}\n")
            f.write(f"Word count: {r['word_count']}\n")
            f.write(f"Sentence count: {r['sentence_count']}\n")
            f.write(f"Average sentence length: {r['avg_sentence_length']}\n")
            f.write(f"Flesch-Kincaid Grade: {r['flesch_kincaid_grade']}\n")
            f.write(f"Flesch Reading Ease: {r['flesch_reading_ease']}\n")
            f.write(f"Gunning Fog Index: {r['gunning_fog']}\n")
            f.write("-" * 70 + "\n")

        avg_fk = round(sum(r["flesch_kincaid_grade"] for r in all_results) / len(all_results), 2)
        avg_fe = round(sum(r["flesch_reading_ease"] for r in all_results) / len(all_results), 2)
        avg_fog = round(sum(r["gunning_fog"] for r in all_results) / len(all_results), 2)

        f.write("\nOVERALL SUMMARY\n")
        f.write("=" * 70 + "\n")
        f.write(f"Average Flesch-Kincaid Grade: {avg_fk}\n")
        f.write(f"Average Flesch Reading Ease: {avg_fe}\n")
        f.write(f"Average Gunning Fog Index: {avg_fog}\n")

    print("=" * 70)
    print(f"Done. Results saved to: {results_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
