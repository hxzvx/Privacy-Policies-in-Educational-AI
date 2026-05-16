# run_compliance_analysis.py
# Place this in your PROJECT CODE folder (same level as extracted_texts folder)

from pathlib import Path
import json
import csv
from datetime import datetime
from typing import Dict, List, Tuple
import re

# ============================================
# CLAUSES DEFINITION (from Table 2 in your report)
# ============================================

CLAUSES = {
    # Personal Information Practices (P1-P7)
    "P1": {
        "name": "Categories of PI Collected",
        "patterns": [
            r"(?i)categories?\s+of\s+personal\s+information",
            r"(?i)types?\s+of\s+data\s+we\s+collect",
            r"(?i)information\s+we\s+collect",
            r"(?i)what\s+information\s+we\s+collect",
        ]
    },
    "P2": {
        "name": "Categories of PI Shared/Sold/Disclosed",
        "patterns": [
            r"(?i)categories?\s+of\s+personal\s+information\s+(?:shared|sold|disclosed)",
            r"(?i)we\s+(?:share|sell|disclose).*?third parties",
            r"(?i)information\s+sharing",
            r"(?i)do\s+not\s+sell",
        ]
    },
    "P3": {
        "name": "Categories of PI Sources",
        "patterns": [
            r"(?i)sources?\s+of\s+information",
            r"(?i)where\s+we\s+collect.*?data",
            r"(?i)information\s+(?:from|collected\s+from)",
            r"(?i)we\s+collect\s+information\s+from",
        ]
    },
    "P4": {
        "name": "Purpose for Collecting PI",
        "patterns": [
            r"(?i)purpose\s+(?:of|for)\s+collecting",
            r"(?i)why\s+we\s+collect",
            r"(?i)how\s+we\s+use\s+(?:your|personal)\s+information",
            r"(?i)to\s+(?:provide|improve|personalize)",
        ]
    },
    "P5": {
        "name": "Purpose for Selling/Sharing/Disclosing",
        "patterns": [
            r"(?i)purpose\s+of\s+(?:sharing|selling|disclosing)",
            r"(?i)why\s+we\s+(?:share|sell)",
            r"(?i)to\s+share.*?with\s+third",
        ]
    },
    "P6": {
        "name": "Categories of Third-Party Recipients",
        "patterns": [
            r"(?i)third[- ]part(y|ies)",
            r"(?i)recipients?\s+of\s+information",
            r"(?i)who\s+we\s+share\s+with",
            r"(?i)service\s+providers",
        ]
    },
    "P7": {
        "name": "PI Retention Period",
        "patterns": [
            r"(?i)retention\s+period",
            r"(?i)how\s+long\s+we\s+(?:keep|retain|store)",
            r"(?i)data\s+retention",
            r"(?i)retain\s+for",
        ]
    },
    
    # Consumer Rights (R1-R10)
    "R1": {
        "name": "Right to Know (Access Confirmation)",
        "patterns": [
            r"(?i)right\s+to\s+know",
            r"(?i)access\s+(?:your|personal)\s+information",
            r"(?i)confirm.*?(?:processing|data)",
            r"(?i)request\s+a\s+copy",
        ]
    },
    "R2": {
        "name": "Right to Data Portability",
        "patterns": [
            r"(?i)data\s+portability",
            r"(?i)right\s+to\s+(?:receive|transfer).*?data",
            r"(?i)portable\s+format",
        ]
    },
    "R3": {
        "name": "Right to Delete (Erase)",
        "patterns": [
            r"(?i)right\s+to\s+(?:delete|erase|remov)",
            r"(?i)request\s+deletion",
            r"(?i)delete\s+your\s+(?:account|data)",
        ]
    },
    "R4": {
        "name": "Right to Correct (Rectify)",
        "patterns": [
            r"(?i)right\s+to\s+(?:correct|rectify|update)",
            r"(?i)correct.*?information",
            r"(?i)update\s+your\s+information",
        ]
    },
    "R5": {
        "name": "Right to Opt-Out",
        "patterns": [
            r"(?i)opt[ -]out",
            r"(?i)do\s+not\s+sell",
            r"(?i)right\s+to\s+object.*?(?:sale|sharing)",
        ]
    },
    "R6": {
        "name": "Right to Object",
        "patterns": [
            r"(?i)right\s+to\s+object",
            r"(?i)object\s+to\s+processing",
        ]
    },
    "R7": {
        "name": "Right to Limit Processing",
        "patterns": [
            r"(?i)restrict\s+processing",
            r"(?i)limit\s+the\s+use",
        ]
    },
    "R8": {
        "name": "Right to Lodge a Complaint",
        "patterns": [
            r"(?i)right\s+to\s+(?:lodge|file)\s+a\s+complaint",
            r"(?i)complaint\s+to\s+(?:authority|regulator)",
            r"(?i)contact\s+your\s+local\s+data\s+protection",
        ]
    },
    "R9": {
        "name": "Right to Withdraw Consent",
        "patterns": [
            r"(?i)withdraw\s+consent",
            r"(?i)revoke\s+consent",
        ]
    },
    "R10": {
        "name": "Right to Non-Discrimination",
        "patterns": [
            r"(?i)non[- ]discriminat",
            r"(?i)no\s+discriminat",
            r"(?i)equal\s+(?:service|price|treatment)",
        ]
    },
    
    # Methods for Exercising Rights (E1-E8)
    "E1": {
        "name": "Methods to Submit a Request",
        "patterns": [
            r"(?i)submit\s+a\s+request",
            r"(?i)how\s+to\s+(?:exercise|request)",
            r"(?i)to\s+exercise\s+your\s+rights?",
        ]
    },
    "E2": {
        "name": "Process for Consumer Appeals",
        "patterns": [
            r"(?i)appeals?",
            r"(?i)appeal\s+process",
        ]
    },
    "E3": {
        "name": "Contact Information",
        "patterns": [
            r"(?i)contact\s+information",
            r"(?i)email:\s*\S+@\S+",
            r"(?i)privacy\s*@",
            r"(?i)contact\s+us\s+at",
        ]
    },
    "E4": {
        "name": "Process for Verifying Requests",
        "patterns": [
            r"(?i)verif(?:y|ication).*?request",
            r"(?i)confirm.*?identity",
            r"(?i)verify\s+your\s+identity",
        ]
    },
    "E5": {
        "name": "Instructions for Authorized Agents",
        "patterns": [
            r"(?i)authorized\s+agent",
            r"(?i)acting\s+on\s+(?:your|their)\s+behalf",
        ]
    },
    "E6": {
        "name": "Opt-In for Under-16s",
        "patterns": [
            r"(?i)under\s+16",
            r"(?i)minor.*?opt[ -]in",
            r"(?i)children.*?consent",
        ]
    },
    "E7": {
        "name": "Opt-Out Preference Signal",
        "patterns": [
            r"(?i)opt[ -]out\s+preference\s+signal",
            r"(?i)global\s+privacy\s+control",
        ]
    },
    "E8": {
        "name": "Frictionless Opt-Out Signal",
        "patterns": [
            r"(?i)frictionless",
            r"(?i)automatic.*?opt[ -]out",
        ]
    },
    
    # Children's Data Protection (C1-C4)
    "C1": {
        "name": "Verifiable Parental Consent",
        "patterns": [
            r"(?i)verifiable\s+parental\s+consent",
            r"(?i)parental\s+consent",
            r"(?i)coppa",
            r"(?i)under\s+13",
        ]
    },
    "C2": {
        "name": "Direct Notice to Parents",
        "patterns": [
            r"(?i)direct\s+notice\s+to\s+parents",
            r"(?i)notify\s+parents",
            r"(?i)notice\s+to\s+parents",
        ]
    },
    "C3": {
        "name": "Prohibition of Conditioning Participation",
        "patterns": [
            r"(?i)conditioning\s+participation",
            r"(?i)require.*?collect.*?to\s+participate",
            r"(?i)condition\s+of\s+service",
        ]
    },
    "C4": {
        "name": "Data Minimization for Children",
        "patterns": [
            r"(?i)data\s+minimization",
            r"(?i)collect.*?only.*?necessary",
            r"(?i)limit\s+collection",
            r"(?i)minimum\s+information",
        ]
    },
}

def check_clause(text: str, patterns: List[str]) -> bool:
    """Check if any pattern matches the text."""
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def load_policy_from_txt(file_path: str) -> str:
    """Load privacy policy text from a txt file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"  Error loading {file_path}: {e}")
        return ""

def load_policies_from_extracted_texts():
    """Load all txt files from the extracted_texts folder."""
    policies = {}
    
    # Navigate to extracted_texts folder
    # Assuming this script is in PROJECT CODE folder
    current_dir = Path.cwd()
    extracted_dir = current_dir / "extracted_texts"
    
    if not extracted_dir.exists():
        print(f"Warning: extracted_texts folder not found at {extracted_dir}")
        print("Trying alternative paths...")
        
        # Try relative path
        extracted_dir = Path("extracted_texts")
        if not extracted_dir.exists():
            print("Error: Could not find extracted_texts folder")
            return policies
    
    print(f"Loading policies from: {extracted_dir}")
    
    txt_files = list(extracted_dir.glob("*.txt"))
    print(f"Found {len(txt_files)} text files")
    
    for txt_file in txt_files:
        policy_name = txt_file.stem  # filename without extension
        print(f"  Loading: {policy_name}")
        policies[policy_name] = load_policy_from_txt(txt_file)
    
    return policies

def analyze_policy(policy_text: str) -> Dict[str, bool]:
    """Analyze a single privacy policy for all clauses."""
    results = {}
    
    for clause_id, clause_info in CLAUSES.items():
        results[clause_id] = check_clause(policy_text, clause_info["patterns"])
    
    return results

def analyze_multiple_policies(policies: dict) -> dict:
    """Run compliance analysis on multiple policies."""
    all_results = {}
    total_policies = len(policies)
    
    print(f"\nAnalyzing {total_policies} policies...")
    
    for idx, (policy_name, policy_text) in enumerate(policies.items(), 1):
        print(f"  [{idx}/{total_policies}] Analyzing: {policy_name}")
        
        if not policy_text.strip():
            print(f"    Warning: Empty policy text for {policy_name}")
            all_results[policy_name] = {
                "clause_results": {clause_id: False for clause_id in CLAUSES},
                "raw_score": 0,
                "percentage": 0.0
            }
            continue
        
        results = analyze_policy(policy_text)
        present_count = sum(1 for present in results.values() if present)
        percentage = (present_count / len(CLAUSES)) * 100
        
        all_results[policy_name] = {
            "clause_results": results,
            "raw_score": present_count,
            "percentage": percentage
        }
    
    return all_results

def export_results_to_csv(results: dict, output_file: str):
    """Export compliance results to CSV."""
    clause_ids = list(CLAUSES.keys())
    
    # Create P_downloads/results folder if it doesn't exist
    results_dir = Path("P_downloads") / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = results_dir / output_file
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        header = ["Policy Name", "Raw Score", "Compliance Score (%)"] + \
                 [f"{clause_id}" for clause_id in clause_ids]
        writer.writerow(header)
        
        # Write data for each policy
        for policy_name, data in results.items():
            row = [
                policy_name,
                data["raw_score"],
                f"{data['percentage']:.2f}",
            ]
            for clause_id in clause_ids:
                row.append("YES" if data["clause_results"][clause_id] else "NO")
            writer.writerow(row)
    
    print(f"\nResults exported to: {output_path}")

def export_summary_report(results: dict, output_file: str):
    """Generate a summary report with statistics."""
    results_dir = Path("P_downloads") / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = results_dir / output_file
    
    # Calculate statistics
    scores = [data["percentage"] for data in results.values()]
    
    summary = {
        "analysis_date": datetime.now().isoformat(),
        "total_policies": len(results),
        "total_clauses": len(CLAUSES),
        "statistics": {
            "mean_compliance": sum(scores) / len(scores) if scores else 0,
            "min_compliance": min(scores) if scores else 0,
            "max_compliance": max(scores) if scores else 0,
            "std_dev": (sum((x - sum(scores)/len(scores))**2 for x in scores) / len(scores))**0.5 if scores else 0
        },
        "clause_summary": {},
        "policies": []
    }
    
    # Clause-level summary (how many policies include each clause)
    for clause_id in CLAUSES:
        count = sum(1 for data in results.values() if data["clause_results"][clause_id])
        summary["clause_summary"][clause_id] = {
            "name": CLAUSES[clause_id]["name"],
            "policies_with_clause": count,
            "percentage": (count / len(results)) * 100 if results else 0
        }
    
    # Individual policy results
    for policy_name, data in results.items():
        summary["policies"].append({
            "name": policy_name,
            "compliance_score": data["percentage"],
            "raw_score": data["raw_score"]
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary exported to: {output_path}")

def print_console_summary(results: dict):
    """Print a formatted summary to console."""
    print("\n" + "="*60)
    print("COMPLIANCE ANALYSIS SUMMARY")
    print("="*60)
    
    # Sort policies by compliance score
    sorted_policies = sorted(results.items(), key=lambda x: x[1]["percentage"], reverse=True)
    
    print("\nPolicy Compliance Scores (Highest to Lowest):")
    print("-"*50)
    for policy_name, data in sorted_policies:
        print(f"  {policy_name:<40} {data['percentage']:>5.1f}% ({data['raw_score']}/{len(CLAUSES)})")
    
    # Average compliance
    avg_compliance = sum(data["percentage"] for data in results.values()) / len(results)
    print(f"\nAverage Compliance: {avg_compliance:.1f}%")
    
    # Most common and least common clauses
    clause_counts = {}
    for clause_id in CLAUSES:
        count = sum(1 for data in results.values() if data["clause_results"][clause_id])
        clause_counts[clause_id] = count
    
    # Most common clauses (top 5)
    most_common = sorted(clause_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    print("\nMost Frequently Found Clauses:")
    for clause_id, count in most_common:
        percentage = (count / len(results)) * 100
        print(f"  {clause_id} ({CLAUSES[clause_id]['name']:<35}): {percentage:.0f}%")
    
    # Least common clauses (bottom 5)
    least_common = sorted(clause_counts.items(), key=lambda x: x[1])[:5]
    print("\nLeast Frequently Found Clauses:")
    for clause_id, count in least_common:
        percentage = (count / len(results)) * 100
        print(f"  {clause_id} ({CLAUSES[clause_id]['name']:<35}): {percentage:.0f}%")

def identify_policy_groups(policies: dict) -> dict:
    """
    Try to identify which policies are for children vs adults based on filename.
    You can modify this function based on your actual naming convention.
    """
    group_mapping = {}
    
    # Keywords that might indicate children's apps
    children_keywords = ["child", "kid", "young", "toddler", "preschool", 
                         "abc", "123", "learn", "education", "student"]
    
    # Keywords that might indicate adult apps
    adult_keywords = ["adult", "professional", "business", "corporate", 
                      "work", "office", "linkedin", "facebook", "twitter"]
    
    for policy_name in policies.keys():
        policy_lower = policy_name.lower()
        
        # Check for children indicators
        is_child = any(keyword in policy_lower for keyword in children_keywords)
        is_adult = any(keyword in policy_lower for keyword in adult_keywords)
        
        if is_child and not is_adult:
            group_mapping[policy_name] = "children"
        elif is_adult and not is_child:
            group_mapping[policy_name] = "adults"
        else:
            # Manual mapping - you'll need to update this based on your actual apps
            group_mapping[policy_name] = "unknown"
    
    return group_mapping

def compare_groups(results: dict, group_mapping: dict):
    """Compare compliance between children and adult apps."""
    children_scores = []
    adult_scores = []
    
    for policy_name, data in results.items():
        group = group_mapping.get(policy_name, "unknown")
        if group == "children":
            children_scores.append(data["percentage"])
        elif group == "adults":
            adult_scores.append(data["percentage"])
    
    print("\n" + "="*60)
    print("GROUP COMPARISON (Children vs Adults)")
    print("="*60)
    
    if children_scores:
        print(f"\nChildren's Apps (n={len(children_scores)}):")
        print(f"  Mean compliance: {sum(children_scores)/len(children_scores):.1f}%")
        print(f"  Range: {min(children_scores):.1f}% - {max(children_scores):.1f}%")
    else:
        print("\nNo children's apps identified")
    
    if adult_scores:
        print(f"\nAdult Apps (n={len(adult_scores)}):")
        print(f"  Mean compliance: {sum(adult_scores)/len(adult_scores):.1f}%")
        print(f"  Range: {min(adult_scores):.1f}% - {max(adult_scores):.1f}%")
    else:
        print("\nNo adult apps identified")
    
    # Clause-level comparison for COPPA clauses specifically
    coppa_clauses = ["C1", "C2", "C3", "C4"]
    
    print("\n" + "-"*60)
    print("COPPA-SPECIFIC CLAUSES COMPARISON")
    print("-"*60)
    
    for clause_id in coppa_clauses:
        children_count = sum(1 for name, data in results.items() 
                           if group_mapping.get(name) == "children" 
                           and data["clause_results"][clause_id])
        adult_count = sum(1 for name, data in results.items() 
                         if group_mapping.get(name) == "adults" 
                         and data["clause_results"][clause_id])
        
        children_pct = (children_count / len(children_scores) * 100) if children_scores else 0
        adult_pct = (adult_count / len(adult_scores) * 100) if adult_scores else 0
        
        print(f"\n{clause_id} - {CLAUSES[clause_id]['name']}:")
        print(f"  Children's apps: {children_pct:.0f}% ({children_count}/{len(children_scores)})")
        print(f"  Adult apps:      {adult_pct:.0f}% ({adult_count}/{len(adult_scores)})")

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("="*60)
    print("PRIVACY POLICY COMPLIANCE ANALYZER")
    print("="*60)
    
    # 1. Load policies from extracted_texts folder
    print("\n[1/5] Loading policies...")
    policies = load_policies_from_extracted_texts()
    
    if not policies:
        print("Error: No policies found. Please check the extracted_texts folder.")
        exit(1)
    
    print(f"Successfully loaded {len(policies)} policies")
    
    # 2. Analyze all policies
    print("\n[2/5] Running compliance analysis...")
    results = analyze_multiple_policies(policies)
    
    # 3. Export results
    print("\n[3/5] Exporting results...")
    export_results_to_csv(results, "compliance_results.csv")
    export_summary_report(results, "compliance_summary.json")
    
    # 4. Print console summary
    print("\n[4/5] Generating summary...")
    print_console_summary(results)
    
    # 5. Group comparison (if applicable)
    print("\n[5/5] Comparing groups...")
    group_mapping = identify_policy_groups(policies)
    compare_groups(results, group_mapping)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print(f"Results saved in: P_downloads/results/")
    print("="*60)