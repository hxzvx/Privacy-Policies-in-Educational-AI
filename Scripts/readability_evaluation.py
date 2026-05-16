import os
from datetime import datetime
import csv
import textstat

# =========================
# PATH SETUP
# =========================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

EXTRACTED_FOLDER = os.path.join(BASE_DIR, "extracted_texts")
RESULTS_FOLDER = os.path.join(BASE_DIR, "results")

os.makedirs(RESULTS_FOLDER, exist_ok=True)


# =========================
# HELPERS
# =========================

def analyze_text(text: str, name: str) -> dict:
    """
    Compute readability scores for one already-extracted privacy policy.
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
        "coleman_liau_index": round(textstat.coleman_liau_index(text), 2),
        "smog_index": round(textstat.smog_index(text), 2),
        "automated_readability_index": round(textstat.automated_readability_index(text), 2),
        "dale_chall_readability_score": round(textstat.dale_chall_readability_score(text), 2),
        "difficult_words": textstat.difficult_words(text),
    }


def load_text_file(file_path: str) -> str:
    """
    Read a text file safely.
    """

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


# =========================
# MAIN PIPELINE
# =========================

def main():
    print("=" * 70)
    print("Privacy Policy Readability Scoring Only")
    print("=" * 70)
    print(f"Extracted texts folder: {EXTRACTED_FOLDER}")
    print(f"Results folder        : {RESULTS_FOLDER}")
    print("=" * 70)

    if not os.path.exists(EXTRACTED_FOLDER):
        print(f"Error: extracted_texts folder not found: {EXTRACTED_FOLDER}")
        return

    txt_files = [
        file for file in os.listdir(EXTRACTED_FOLDER)
        if file.lower().endswith(".txt")
    ]

    if not txt_files:
        print("No .txt files found in extracted_texts folder.")
        return

    print(f"Found {len(txt_files)} extracted policy file(s).\n")

    all_results = []

    for i, filename in enumerate(txt_files, start=1):
        file_path = os.path.join(EXTRACTED_FOLDER, filename)
        policy_name = os.path.splitext(filename)[0]

        print(f"[{i}/{len(txt_files)}] Scoring: {filename}")

        try:
            text = load_text_file(file_path)

            if not text:
                print("  Empty file. Skipping.\n")
                continue

            result = analyze_text(text, policy_name)
            result["text_file"] = filename

            all_results.append(result)

            print(f"  Word Count                 : {result['word_count']}")
            print(f"  Sentence Count             : {result['sentence_count']}")
            print(f"  Avg Sentence Length        : {result['avg_sentence_length']}")
            print(f"  Flesch-Kincaid Grade       : {result['flesch_kincaid_grade']}")
            print(f"  Flesch Reading Ease        : {result['flesch_reading_ease']}")
            print(f"  Gunning Fog Index          : {result['gunning_fog']}")
            print(f"  Coleman-Liau Index         : {result['coleman_liau_index']}")
            print(f"  SMOG Index                 : {result['smog_index']}")
            print(f"  ARI                        : {result['automated_readability_index']}")
            print(f"  Dale-Chall Score           : {result['dale_chall_readability_score']}")
            print(f"  Difficult Words            : {result['difficult_words']}")
            print()

        except Exception as e:
            print(f"  Error scoring {filename}: {e}\n")

    if not all_results:
        print("No policies were successfully scored.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    txt_results_file = os.path.join(
        RESULTS_FOLDER,
        f"readability_scores_{timestamp}.txt"
    )

    csv_results_file = os.path.join(
        RESULTS_FOLDER,
        f"readability_scores_{timestamp}.csv"
    )

    # =========================
    # SAVE TXT RESULTS
    # =========================

    with open(txt_results_file, "w", encoding="utf-8") as f:
        f.write("Privacy Policy Readability Scores\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Policies analyzed: {len(all_results)}\n\n")

        for r in all_results:
            f.write(f"Name: {r['name']}\n")
            f.write(f"Text file: {r['text_file']}\n")
            f.write(f"Word count: {r['word_count']}\n")
            f.write(f"Sentence count: {r['sentence_count']}\n")
            f.write(f"Average sentence length: {r['avg_sentence_length']}\n")
            f.write(f"Flesch-Kincaid Grade: {r['flesch_kincaid_grade']}\n")
            f.write(f"Flesch Reading Ease: {r['flesch_reading_ease']}\n")
            f.write(f"Gunning Fog Index: {r['gunning_fog']}\n")
            f.write(f"Coleman-Liau Index: {r['coleman_liau_index']}\n")
            f.write(f"SMOG Index: {r['smog_index']}\n")
            f.write(f"Automated Readability Index: {r['automated_readability_index']}\n")
            f.write(f"Dale-Chall Readability Score: {r['dale_chall_readability_score']}\n")
            f.write(f"Difficult Words: {r['difficult_words']}\n")
            f.write("-" * 70 + "\n")

        f.write("\nOVERALL AVERAGES\n")
        f.write("=" * 70 + "\n")

        numeric_metrics = [
            "word_count",
            "sentence_count",
            "avg_sentence_length",
            "flesch_kincaid_grade",
            "flesch_reading_ease",
            "gunning_fog",
            "coleman_liau_index",
            "smog_index",
            "automated_readability_index",
            "dale_chall_readability_score",
            "difficult_words",
        ]

        for metric in numeric_metrics:
            avg_value = round(sum(r[metric] for r in all_results) / len(all_results), 2)
            f.write(f"Average {metric}: {avg_value}\n")

    # =========================
    # SAVE CSV RESULTS
    # =========================

    fieldnames = [
        "name",
        "text_file",
        "word_count",
        "sentence_count",
        "avg_sentence_length",
        "flesch_kincaid_grade",
        "flesch_reading_ease",
        "gunning_fog",
        "coleman_liau_index",
        "smog_index",
        "automated_readability_index",
        "dale_chall_readability_score",
        "difficult_words",
    ]

    with open(csv_results_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for r in all_results:
            writer.writerow(r)

    print("=" * 70)
    print("Done. Scores saved to:")
    print(f"TXT: {txt_results_file}")
    print(f"CSV: {csv_results_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
