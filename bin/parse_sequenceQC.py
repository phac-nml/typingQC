#!/usr/bin/env python3

import json
import csv
import argparse
from pathlib import Path
import gzip

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract FAILED QC messages from mikro JSON file"
    )
    parser.add_argument(
        "-i", "--input", required=True, type=Path,
        help="Path to the mikro QC JSON file (.json or .json.gz)"
    )
    parser.add_argument(
        "-s", "--sample_id", required=True,
        help="Sample ID to use in the output filename"
    )
    parser.add_argument(
        "-o", "--output_dir", type=Path, default=Path.cwd(),
        help="Directory to write the output CSV file"
    )
    return parser.parse_args()

def load_json(path):
    open_func = gzip.open if path.suffix == ".gz" else open
    with open_func(path, 'rt') as f:
        return json.load(f)

def extract_failed_messages(sample_data):
    messages = []
    for key, value in sample_data.items():
        if key.startswith("QualityAnalysis.") and key.endswith(".qc_status") and value == "FAILED":
            prefix = key.rsplit(".qc_status", 1)[0]
            message_key = f"{prefix}.message"
            if message_key in sample_data:
                messages.append(sample_data[message_key])
    return messages

def extract_qc_message_first_line(sample_data):
    qc_msg = sample_data.get("QCMessage", "")
    return qc_msg.splitlines()[0] if qc_msg else ""

def main():
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input file {args.input} not found.")

    data = load_json(args.input)
    if not isinstance(data, dict) or len(data) != 1:
        raise ValueError("Expected JSON to contain a single top-level sample key.")

    sample_key = next(iter(data))
    sample_data = data[sample_key]

    failed_messages = extract_failed_messages(sample_data)
    rds_qc_message = extract_qc_message_first_line(sample_data)

    output_path = args.output_dir / f"{args.sample_id}_sequenceQC.csv"
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["SAMPLE", "QUALITY_ANALYSIS", "RDS_QC_MESSAGE"])
        writer.writerow([args.sample_id, "; ".join(failed_messages) if failed_messages else "No QC failures", rds_qc_message])

if __name__ == "__main__":
    main()
