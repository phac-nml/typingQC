#!/usr/bin/env python3

import json
import csv
import argparse
from pathlib import Path
import gzip

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract sequence QC assessment from a mikrokondo-generated JSON output file"
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
    with open_func(path, "rt") as f:
        return json.load(f)

#Constants for JSON field structure and failed test info
QUALITY_PREFIX = "QualityAnalysis."
QC_STATUS_SUFFIX = ".qc_status"
MESSAGE_SUFFIX = ".message"
QC_MESSAGE_KEY = "QCMessage"

ABSOLUTE_FAIL_TESTS = {
    "raw_average_quality",
    "average_coverage",
}

WARNING_TESTS = {
    "n50_value",
    "nr_contigs",
    "length",
}

CHECKM_TEST = "checkm_contamination"

PNC_FAIL_MESSAGE = (
    "[SEQ_FAIL] Resequencing is recommended. QUALITY_METRICS did not meet PNC requirements."
)

CHECKM_FAIL_MESSAGE = (
    "[SEQ_FAIL] Sample may be contaminated. Re-isolation and resequencing is recommended."
)

WARNING_MESSAGE = (
    "[SEQ_WARNING] Check QUALITY_METRICS messages to determine if resequencing is necessary."
)

# Check is typing is supported for given species.
# Note: Needs to be updated if new species are added to genome typing capabilities
def is_typing_supported(species):
    species_lower = species.lower()
    return (
        "salmonella" in species_lower
        or "escherichia" in species_lower
    )

#Extract failed QC messages and return both messages and failed test info
def extract_failed_messages(sample_data):
    messages = []
    failed_tests = set()

    for key, value in sample_data.items():
        if key.startswith(QUALITY_PREFIX) and key.endswith(QC_STATUS_SUFFIX) and value == "FAILED":
            test_name = key.replace(QUALITY_PREFIX, "").replace(QC_STATUS_SUFFIX, "")
            failed_tests.add(test_name)

            message_key = f"{QUALITY_PREFIX}{test_name}{MESSAGE_SUFFIX}"
            if message_key in sample_data:
                messages.append(sample_data[message_key])

    return messages, failed_tests

# Build RDS QC message depending on test results
# Note: Needs to be updated if new species are added to genome typing capabilities
def build_typingQC_message(sample_data, species, failed_tests):
    if CHECKM_TEST in failed_tests:
        base_message = CHECKM_FAIL_MESSAGE
    elif failed_tests.intersection(ABSOLUTE_FAIL_TESTS):
        base_message = PNC_FAIL_MESSAGE
    elif failed_tests.intersection(WARNING_TESTS):
        base_message = WARNING_MESSAGE
    else:
        qc_msg = sample_data.get(QC_MESSAGE_KEY, "")
        base_message = qc_msg.splitlines()[0] if qc_msg else ""

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
        raise ValueError(
            "Expected mikrokondo-generated JSON input file to contain a single top-level sample key."
        )

    sample_key = next(iter(data))
    sample_data = data[sample_key]

    failed_messages, failed_tests = extract_failed_messages(sample_data)

    typingQC_message = build_typingQC_message(
        sample_data=sample_data,
        species=args.species,
        failed_tests=failed_tests,
    )

    output_path = Path(f"{args.sample_id}_sequenceQC.csv")
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["sample", "sample_name", "typingQC_message", "quality_metrics"]
        )
        writer.writerow(
            [
                args.irida_id,
                args.sample_id,
                typingQC_message,
                "; ".join(failed_messages) if failed_messages else "No QC failures",
            ]
        )

if __name__ == "__main__":
    main()

