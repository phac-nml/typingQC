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
        "-n", "--irida_id", required=True,
        help="IRIDA Next sample identifier to populate the CSV output file"
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

#Extract failed QC messages and return both messages and failed test info
def extract_failed_messages(sample_data):
    messages = []
    failed_tests = []
    checkm_failed = False

    for key, value in sample_data.items():
        if key.startswith(Quality_Analysis_prefix) and key.endswith(QC_Status_suffix) and value == "FAILED":
            prefix = key.rsplit(QC_Status_suffix, 1)[0]
            message_key = f"{prefix}{Message_suffix}"

            # Extract the test name from the key
            test_name = prefix.replace(Quality_Analysis_prefix, "")
            failed_tests.append(test_name)

            # Check if checkM contamination failed
            if test_name == "checkm_contamination":
                checkm_failed = True

            if message_key in sample_data:
                messages.append(sample_data[message_key])

    return messages, failed_tests, checkm_failed

# Check is typing is supported for given species
def is_typing_supported(species):
    species_lower = species.lower()
    return "salmonella" in species_lower or "escherichia" in species_lower

# Build RDS QC message depending on test results
# Note: Needs to be updated if new species are added to genome typing capabilities
def build_rds_qc_message(sample_data, species, failed_tests, checkm_failed):
    num_failed = len(failed_tests)

    # Check for checkM contamination failure first
    if checkm_failed:
        base_message = "[SEQ_FAIL] Sample may be contaminated. Re-isolation and resequencing is recommended."
    elif num_failed == 0:
        qc_msg = sample_data.get(QC_Message_key, "")
        base_message = qc_msg.splitlines()[0] if qc_msg else ""
    elif 1 <= num_failed <= 2:
        base_message = "[SEQ_WARNING] Check QUALITY_METRICS messages to determine if resequencing is necessary."
    elif 3 <= num_failed <= 5:
        base_message = "[SEQ_FAIL] Resequencing is recommended due to multiple FAILED sequence QUALITY_METRICS."
    else:
        # This shouldn't happen with 6 total tests, but handle edge case
        base_message = "[SEQ_FAIL] Resequencing is recommended. QUALITY_METRICS did not meet the required values."

    # Add species typing warning if not supported
    if not is_typing_supported(species):
        return f"{base_message}; [FAIL] Typing unsupported for {species}."

    return base_message

def main():
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input file {args.input} not found.")

    data = load_json(args.input)
    if not isinstance(data, dict) or len(data) != 1:
        raise ValueError("Expected mikrokondo-generated JSON input file to contain a single top-level sample key.")

    sample_key = next(iter(data))
    sample_data = data[sample_key]

    failed_messages, failed_tests, checkm_failed = extract_failed_messages(sample_data)
    rds_qc_message = build_rds_qc_message(sample_data, args.species, failed_tests, checkm_failed)

    output_path = Path(f"{args.sample_id}_sequenceQC.csv")
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sample", "sample_name", "rds_qc_message", "quality_metrics"])
        writer.writerow([args.irida_id, args.sample_id, rds_qc_message, "; ".join(failed_messages) if failed_messages else "No QC failures"])

if __name__ == "__main__":
    main()
