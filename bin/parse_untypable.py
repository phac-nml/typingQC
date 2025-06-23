#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate report for samples that could not be typed due to unsupported species or missing mikrokondo file."
    )
    parser.add_argument(
        "-s", "--sample_id", required=True, help="Sample ID"
    )
    parser.add_argument(
        "--species", required=True, help="Species from mikrokondo prediction"
    )
    parser.add_argument(
        "--qc_status", required=True, help="Overall sequencing status from mikrokondo analysis, e.g. PASS or FAIL"
    )
    parser.add_argument(
        "--has_mikro_file", required=True, choices=["true", "false"],
        help="Whether mikrokondo file is present"
    )
    parser.add_argument(
        "-o", "--output_dir", type=Path, default=Path.cwd(),
        help="Directory to write the output CSV file"
    )
    return parser.parse_args()

def determine_failure_reason(species, has_mikro_file, qc_status):

    # Convert string boolean to actual boolean
    has_file = has_mikro_file.lower() == "true"

    # Check if mikrokondo file is missing
    if not has_file:
        return f"[FAILED] No mikrokondo data file provided. Sequencing QC status: {qc_status}"

    # Check for supported species (case-insensitive)
    species_lower = species.lower()
    if "salmonella" not in species_lower and "escherichia" not in species_lower:
        return f"[FAILED] Typing unsupported for species: {species}"

    # Catch all for unexpected cases
    else:
        return f"[FAILED] Unknown reason - supported species ({species}) with mikrokondo file present but sample failed TypingQC - further investigation required"

def main():
    args = parse_args()
    output_path = args.output_dir / f"{args.sample_id}_untypable.csv"

    # Determine the failure reason
    rds_qc_message = determine_failure_reason(args.species, args.has_mikro_file, args.qc_status)

    # Quality analysis is left empty
    quality_analysis = ""

    # Write output CSV
    try:
        with output_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["SAMPLE", "QUALITY_ANALYSIS", "RDS_QC_MESSAGE"])
            writer.writerow([args.sample_id, quality_analysis, rds_qc_message])

    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
