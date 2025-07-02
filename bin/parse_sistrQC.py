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
    return parser.parse_args()

def load_json(path):
    open_func = gzip.open if path.suffix == ".gz" else open
    with open_func(path, 'rt') as f:
        return json.load(f)

#Constants for SISTR JSON field structure
SISTR_PREFIX = "SISTRSubtyping.0."
QC_STATUS_KEY = f"{SISTR_PREFIX}qc_status"
QC_MESSAGES_KEY = f"{SISTR_PREFIX}qc_messages"
SEROVAR_KEY = f"{SISTR_PREFIX}serovar"

def extract_sistr_qc(sample_data):
    qc_status = sample_data.get(QC_STATUS_KEY, "Unknown")
    if qc_status.upper() == "PASS":
        return ""
    else:
        # For samples that FAIL or have a WARNING as the SISTR QC_STAUTS: include the qc_messages
        qc_messages = sample_data.get(QC_MESSAGES_KEY, "")
        return qc_messages if qc_messages else "No QC messages in mikrokondo-generated JSON file"

def build_rds_qc_message(sample_data):
    qc_status = sample_data.get(QC_STATUS_KEY, "Unknown")

    if qc_status.upper() == "PASS":
        serovar = sample_data.get(SEROVAR_KEY, "")
        return "[PASS] Use SISTR's predicted_primary_type_name as serovar."
        
    elif qc_status.upper() in ["FAIL", "WARNING"]:
        return f"[FAILED] SISTR Serotyping Failed. RESEQUENCING or TRADITIONAL SEROTYPING RECOMMENDED."
    else:
        return f"[UNKNOWN]: {qc_status}"
    
def main():
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input file {args.input} not found.")

    data = load_json(args.input)
    if not isinstance(data, dict) or len(data) != 1:
        raise ValueError("Expected mikrokondo-generated JSON input file to containa single top-level sample key.")
    
    sample_key = next(iter(data))
    sample_data = data[sample_key]

    #Check if SISTR data exists
    if QC_STATUS_KEY not in sample_data:
        quality_analysis = f"Sample predicted to be {args.species} but no SISTR data found"
        rds_qc_message = "[FAILED] Re-run mikrokondo to generate SISTR data"
    else:
        quality_analysis = extract_sistr_qc(sample_data)
        rds_qc_message = build_rds_qc_message(sample_data)
    
    #Write output file
    output_path = Path(f"{args.sample_id}_sistrQC.csv")
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["SAMPLE", "QUALITY_ANALYSIS", "RDS_QC_MESSAGE"])
        writer.writerow([args.sample_id, quality_analysis, rds_qc_message])

if __name__ == "__main__":
    main()
