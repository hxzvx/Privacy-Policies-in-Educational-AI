# Privacy Policies in Educational AI

This project analyzes privacy policies of educational AI applications. The goal is to evaluate policy readability, legal compliance and user perception.
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
'''
## Description

The project focuses on collecting and analyzing privacy policies from educational AI applications. The analysis includes reading privacy policy URLs, extracting policy text, evaluating readability, and performing compliance-related analysis.

## Requirements

The required Python packages are listed in:

```text
req.txt
```

To install them, run:

```bash
pip install -r req.txt
```

## Instructions

Follow these steps to run the project:

1. Download or clone the repository.

2. Install the required Python packages:

```bash
pip install -r req.txt
```

3. Add the privacy policy URLs inside the `urls/` folder.

4. Run the extraction script to collect the privacy policy text:

```bash
python Scripts/PoliPy_Extraction.py
```

5. If some policies fail to extract, run the retry script:

```bash
python Scripts/extraction_with_retry.py
```

6. Run the readability evaluation script:

```bash
python Scripts/readability_evaluation.py
```

7. Run the compliance analysis script:

```bash
python Scripts/compliance.py
```

8. The extracted policy texts will be saved in the `Extracted_Texts/` folder.

9. The generated analysis outputs will be saved in the `Results/` folder.
