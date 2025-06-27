#!/usr/bin/env python3

import json
import csv
import argparse
from pathlib import Path
import gzip

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract FAILED QC messages from a mikrokondo-generated JSON output file"
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

#Constants for JSON field structure
Quality_Analysis_prefix = "QualityAnalysis."
QC_Status_suffix = ".qc_status"
Message_suffix = ".message"
QC_Message_key = "QCMessage"

def extract_failed_messages(sample_data):
    messages = []
    for key, value in sample_data.items():
        if key.startswith(Quality_Analysis_prefix) and key.endswith(QC_Status_suffix) and value == "FAILED":
            prefix = key.rsplit(QC_Status_suffix, 1)[0]
            message_key = f"{prefix}{Message_suffix}"
            if message_key in sample_data:
                messages.append(sample_data[message_key])
    return messages

#Needs to be updated if new species are added to genome typing capabilities
def build_rds_qc_message(sample_data, species):
    qc_msg = sample_data.get(QC_Message_key, "")
    base_msg = qc_msg.splitlines()[0] if qc_msg else ""
    species_lower = species.lower()
    if "salmonella" not in species_lower and "escherichia" not in species_lower:
        return f"{base_msg}; [WARNING] Typing unsupported for {species}."
    return base_msg

def main():
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input file {args.input} not found.")

    data = load_json(args.input)
    if not isinstance(data, dict) or len(data) != 1:
        raise ValueError("Expected mikrokondo-generated JSON input file to contain a single top-level sample key.")

    sample_key = next(iter(data))
    sample_data = data[sample_key]

    failed_messages = extract_failed_messages(sample_data)
    rds_qc_message = build_rds_qc_message(sample_data, args.species)

    output_path = Path(f"{args.sample_id}_sequenceQC.csv")
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["SAMPLE", "QUALITY_ANALYSIS", "RDS_QC_MESSAGE"])
        writer.writerow([args.sample_id, "; ".join(failed_messages) if failed_messages else "No QC failures", rds_qc_message])

if __name__ == "__main__":
    main()
