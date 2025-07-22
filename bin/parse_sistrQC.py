#!/usr/bin/env python3

import json
import csv
import argparse
from pathlib import Path
import gzip
import sys

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
    qc_messages = sample_data.get(QC_MESSAGES_KEY, "")

    if qc_status.upper() == "PASS":
        # For PASS samples, leave QUALITY_ANALYSIS column blank
        return ""

    elif qc_status.upper() == "WARNING":
        # If sample raises a WARNING in qc_status record the QC_message
        return qc_messages if qc_messages else "SISTR analysis completed with warnings. Please review results manually."

    else:
        # For samples that FAIL SISTR QC_STATUS: include the qc_messages in report file
        return qc_messages if qc_messages else "No QC messages in mikrokondo-generated JSON file. Please check for failures manually."

def build_rds_qc_message(sample_data, reportable_serovars):
    qc_status = sample_data.get(QC_STATUS_KEY, "Unknown")
    qc_messages = sample_data.get(QC_MESSAGES_KEY, "")

    # Check for H1 antigen warning from SISTR and treat it as an RDS [FAIL]
    if qc_status.upper() == "WARNING" and H1_warning(qc_messages):
        return "[FAILED] SISTR serotyping unsuccessful. RESEQUENCING or TRADITIONAL SEROTYPING is advised."

    if qc_status.upper() in ["PASS", "WARNING"]:
        # Extract serovar predictions
        serovar = sample_data.get(SEROVAR_KEY, "")
        serovar_cgmlst = sample_data.get(SEROVAR_CGMLST, "")

        # Check is any serovar was found by SISTR
        if not serovar:
            return "[FAILED] No serovar found in SISTR results."

        # Check if SISTR predicted serovar is reportable
        if serovar in reportable_serovars:
            return "[PASS] Use SISTR's PREDICTED_PRIMARY_TYPE_NAME as serovar."
        else:
            # Predicted overall serovar is not reportable, but check cgMLST serovar as alternative
            if serovar_cgmlst != serovar and serovar_cgmlst in reportable_serovars:
                return f"[FAILED] Serovar '{serovar}' is not reportable. cgMLST '{serovar_cgmlst}' result is reportable — seek guidance on traditional serotyping."
            else:
                # Serovar not reportable
                return f"[FAILED] Serovar '{serovar}' is NOT REPORTABLE. Perform TRADITIONAL SEROTYPING."

    elif qc_status.upper() == "FAIL":
        # SISTR analysis failed or has warnings
        return "[FAILED] SISTR serotyping unsuccessful. RESEQUENCING or TRADITIONAL SEROTYPING is advised."
    else:
        return f"[UNKNOWN] SISTR QC status: {qc_status}. Please check for failures manually."

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
    sample_data = data[sample_key]

    #Check if SISTR data exists in the JSON file and process accordingly
    if QC_STATUS_KEY not in sample_data:
        quality_analysis = f"Sample predicted to be {args.species} but no SISTR data found."
        rds_qc_message = "[FAILED] Re-run mikrokondo to generate SISTR data."
    else:
        quality_analysis = extract_sistr_qc(sample_data)
        rds_qc_message = build_rds_qc_message(sample_data, reportable_serovars)

    #Write output CSV file with results
    output_path = Path(f"{args.sample_id}_sistrQC.csv")
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["SAMPLE", "QUALITY_ANALYSIS", "RDS_QC_MESSAGE"])
        writer.writerow([args.sample_id, quality_analysis, rds_qc_message])

if __name__ == "__main__":
    main()
