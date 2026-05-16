# Privacy Policies in Educational AI

This project analyzes privacy policies of educational AI applications. The goal is to evaluate policy readability, legal compliance and user perception.
## Project Structure

## Project Structure

```text
Privacy-Policies-in-Educational-AI/
│
├── Extracted_Texts/
│   └── Contains extracted privacy policy text files.
│
├── Results/
│   └── Contains output files generated from the analysis, such as readability scores.
│
├── Scripts/
│   ├── PoliPy_Extraction.py
│   │   └── Extracts privacy policy text using PoliPy.
│   ├── compliance.py
│   │   └── Performs legal compliance-related analysis on the extracted policies.
│   ├── extraction_with_retry.py
│   │   └── Extracts policy text with retry handling for failed extraction attempts.
│   └── readability_evaluation.py
│       └── Calculates readability scores for the extracted privacy policy texts.
│
├── urls/
│   └── Contains text files with privacy policy URLs used in the project.
│
└── req.txt
    └── Contains the Python packages required to run the project.
