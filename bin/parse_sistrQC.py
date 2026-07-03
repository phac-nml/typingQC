#!/usr/bin/env python3

import json
import csv
import argparse
import re
from pathlib import Path
import gzip

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract and report SISTR subtyping QC information from a mikrokondo-generated JSON output file"
    )
    parser.add_argument(
        "-i", "--input", required=True, type=Path,
        help="Path to the mikrokondo-generated JSON output file (.json or .json.gz)"
    )
    parser.add_argument(
        "-s", "--sample_id", required=True,
        help="Sample ID to use in the output filename"
    )
    parser.add_argument(
        "-n", "--irida_id", required=True,
        help="IRIDA Next sample identifier to populate the CSV output file"
    )
    parser.add_argument(
        "--species", required=True,
        help="Predicted species from mikrokondo"
    )
    parser.add_argument(
        "-r", "--reportables", required=True, type=Path,
        help="Path to the file containing all validated and reportable Salmonella serovars"
    )
    return parser.parse_args()

def load_json(path):
    open_func = gzip.open if path.suffix == ".gz" else open
    with open_func(path, 'rt') as f:
        return json.load(f)

def load_reportable_serovars(reportable_file):
    with reportable_file.open('r', encoding='utf-8') as f:
        serovars = set()
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                serovars.add(line)
        #Ensure at least one valid serovar is included
        if len(serovars) == 0:
            raise ValueError(f"No valid serovars found in {reportable_file}.")
        return serovars

#Constants for SISTR JSON field structure - these define the keys used from the mikrokondo-generate JSON output file
SISTR_PREFIX = "SISTRSubtyping.0."
QC_STATUS_KEY = f"{SISTR_PREFIX}qc_status"
QC_MESSAGES_KEY = f"{SISTR_PREFIX}qc_messages"
SEROVAR_KEY = f"{SISTR_PREFIX}serovar"
SEROVAR_CGMLST = f"{SISTR_PREFIX}serovar_cgmlst"


#QC_MESSAGES Updates
#Matches the non-actionable cgMLST loci found INFO message and strips it from qc_messages
CGMLST_LOCI_INFO_PATTERN = re.compile(r"INFO: Number of cgMLST\d+ loci found \(n=\d+\)")
def filter_qc_messages(qc_messages):
    if not qc_messages:
        return qc_messages
    cleaned = CGMLST_LOCI_INFO_PATTERN.sub("", qc_messages)
    # Collapse leftover separators/whitespace left behind by the removal
    cleaned = re.sub(r"\s*\|\s*", " | ", cleaned)
    cleaned = re.sub(r"^\s*\|\s*|\s*\|\s*$", "", cleaned)
    cleaned = re.sub(r"\n\s*\n", "\n", cleaned)
    return cleaned.strip()

WZX_WZY_PATTERN = "Wzx/Wzy genes missing"
WZX_WZY_WARNING_MESSAGE = "WARNING: Wzx/Wzy genes missing. Cannot determine O-antigen serogroup."

def wzx_wzy_only_failure(qc_messages):
    #Checks if a SISTR FAIL is solely due to missing Wzx/Wzy genes: does not affect serovar prediction and should not result in FAIL for typingQC
    if not qc_messages:
        return False
    return WZX_WZY_PATTERN in qc_messages

def H1_warning(qc_messages):
    # Check if SISTR WARNING contains identification of the inability to identify H1 antigens, and therefore, unable to predict serovar repliably
    if not qc_messages:
        return False
    # Check for the specific H1 antigen missing warnings
    H1_pattern = [
        "H1 antigen gene (fliC) missing",
        "Cannot determine H1 antigen",
        "Cannot accurately predict serovar from antigen genes"
    ]
    return any(pattern in qc_messages for pattern in H1_pattern)

def extract_sistr_qc(sample_data):
    qc_status = sample_data.get(QC_STATUS_KEY, "Unknown")
    qc_messages = filter_qc_messages(sample_data.get(QC_MESSAGES_KEY, ""))

    if qc_status.upper() == "PASS":
        # For PASS samples, leave QUALITY_ANALYSIS column blank
        return ""

    if qc_status.upper() == "FAIL" and wzx_wzy_only_failure(qc_messages):
        # O-antigen serogroup couldn't be determined, but this doesn't block typingQC and reports it as a warning rather than the raw FAIL message.
        return WZX_WZY_WARNING_MESSAGE

    elif qc_status.upper() == "WARNING":
        # If sample raises a WARNING in qc_status record the QC_message
        return qc_messages if qc_messages else "SISTR analysis completed with warnings. Please review results manually."

    else:
        # For samples that FAIL SISTR QC_STATUS: include the qc_messages in report file
        return qc_messages if qc_messages else "No QC messages in mikrokondo-generated JSON file. Please check for failures manually."

def build_typingQC_message(sample_data, reportable_serovars):
    qc_status = sample_data.get(QC_STATUS_KEY, "Unknown")
    qc_messages = filter_qc_messages(sample_data.get(QC_MESSAGES_KEY, ""))

    # Check for H1 antigen warning from SISTR and treat it as an RDS [FAIL]
    if qc_status.upper() == "WARNING" and H1_warning(qc_messages):
        return "[SISTR_FAIL] Serotyping unsuccessful. RESEQUENCING or TRADITIONAL SEROTYPING is advised."

    # A FAIL solely due to missing Wzx/Wzy genes: fall through to the serovar reportability check below and prepend a warning instead of SISTR_FAIL
    is_wzx_wzy_fail = qc_status.upper() == "FAIL" and wzx_wzy_only_failure(qc_messages)

    if qc_status.upper() in ["PASS", "WARNING"] or is_wzx_wzy_fail:
        # Extract serovar predictions
        serovar = sample_data.get(SEROVAR_KEY, "")
        serovar_cgmlst = sample_data.get(SEROVAR_CGMLST, "")

        # Check is any serovar was found by SISTR
        if not serovar:
            return "[SISTR_FAIL] No serovar found in SISTR results."

        # Check if SISTR predicted serovar is reportable
        if serovar in reportable_serovars:
            return "[SISTR_PASS]"
        else:
            return f"[TYPE_FAIL] Serovar '{serovar}' is NOT REPORTABLE. Perform TRADITIONAL SEROTYPING."

    elif qc_status.upper() == "FAIL":
        # SISTR analysis failed or has warnings
        return "[SISTR_FAIL] Serotyping unsuccessful. RESEQUENCING or TRADITIONAL SEROTYPING is advised."
    else:
        return f"[FAIL] SISTR QC status: {qc_status}. Please check for failures manually."

def main():
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input file {args.input} not found.")

    #Load and validate JSON structure
    data = load_json(args.input)
    if not isinstance(data, dict) or len(data) != 1:
        raise ValueError("Expected mikrokondo-generated JSON input file to contain a single top-level sample key.")

    #Load reportable serovar list
    reportable_serovars = load_reportable_serovars(args.reportables)

    # Extract sample data from JSON
    sample_key = next(iter(data))

    # Check if sample_key matches expected sample_id to ensure correct JSON file
    if sample_key != args.sample_id:
        raise ValueError(f"Sample ID mismatch: JSON contains '{sample_key}' but expected '{args.sample_id}'.")

    sample_data = data[sample_key]

    #Check if SISTR data exists in the JSON file and process accordingly
    if QC_STATUS_KEY not in sample_data:
        quality_analysis = f"Sample predicted to be {args.species} but no SISTR data found."
        typingQC_message = "[FAIL] Re-run mikrokondo to generate SISTR data."
    else:
        quality_analysis = extract_sistr_qc(sample_data)
        typingQC_message = build_typingQC_message(sample_data, reportable_serovars)

    #Write output CSV file with results
    output_path = Path(f"{args.sample_id}_sistrQC.csv")
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sample", "sample_name", "typingQC_message", "quality_metrics"])
        writer.writerow([args.irida_id, args.sample_id, typingQC_message, quality_analysis])

if __name__ == "__main__":
    main()
