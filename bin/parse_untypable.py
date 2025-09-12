#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate report for samples that could not be typed due to unsupported species or missing mikrokondo-generated output file."
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
        "--has_mikro_file", action="store_true", help="Include this flag if mikrokondo-generated JSON file is present"
    )
    return parser.parse_args()

def determine_failure_reason(species, has_mikro_file):

    # Check if mikrokondo file is missing
    if not has_mikro_file:
        return f"[FAIL] No mikrokondo data file provided."

    # Check for supported species (case-insensitive)
    species_lower = species.lower()
    if "salmonella" not in species_lower and "escherichia" not in species_lower:
        return f"[FAIL] TypingQC unsupported for species: {species}"

    # Catch all for unexpected cases
    else:
        return f"[FAIL] Unknown reason - supported species ({species}) with mikrokondo file present but sample failed TypingQC - further investigation required"

def main():
    args = parse_args()

    # Determine the failure reason
    rds_qc_message = determine_failure_reason(args.species, args.has_mikro_file)

    # Quality analysis provides the QC Status of the sequencing results from mikrokondo
    quality_analysis = f"Overall sequence QC status: {args.qc_status}"

    # Write output CSV
    output_path = Path(f"{args.sample_id}_exclusions.csv")
    with output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["SAMPLE", "RDS_QC_MESSAGE", "QUALITY_METRICS"])
        writer.writerow([args.sample_id, rds_qc_message, quality_analysis])

if __name__ == "__main__":
    main()
