#!/usr/bin/env python3

import csv
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="Merge CSV reports from each module into a single TypingQC_report"
    )
    parser.add_argument(
        "-i", "--input", required=True, nargs="+", type=Path,
        help="Paths to CSV files to merge"
    )
    parser.add_argument(
        "-o", "--output", required=True, type=Path,
        help="Path to the merged TypingQC CSV output file"
    )
    return parser.parse_args()

def load_csv(file_path, headers):
    """Load CSV file and return a dict mapping sample -> row dict with all headers filled"""
    data = dict()
    with file_path.open('r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sample_id = row.get("sample") or row.get("sample_name")
            if not sample_id:
                raise ValueError(f"No 'sample' column found in {file_path}")
            # Ensure all expected headers exist, leave blank if missing
            row_data = {h: row.get(h, "") or "" for h in headers}
            if sample_id in data:
                # Merge repeated samples by concatenating unique values with "; "
                for h in headers:
                    if h in ["sample", "sample_name"]:
                        continue
                    existing = data[sample_id][h]
                    new_val = row_data[h]
                    if not existing:
                        data[sample_id][h] = new_val
                    elif new_val:
                        # Merge unique values
                        existing_set = set(existing.split("; "))
                        new_set = set(new_val.split("; "))
                        merged = "; ".join(sorted(existing_set | new_set))
                        data[sample_id][h] = merged
            else:
                data[sample_id] = row_data
    return data

def main():
    args = parse_args()

    headers = [
        "sample",
        "sample_name",
        "rds_qc_message",
        "quality_metrics",
        "Validated_Toxins",
        "Validated_STXSubtypes"
    ]

    merged_data = dict()

    for csv_file in args.input:
        if not csv_file.exists():
            raise FileNotFoundError(f"Input CSV file not found: {csv_file}")
        data = load_csv(csv_file, headers)
        for sample, row in data.items():
            if sample in merged_data:
                # Merge duplicate samples
                for h in headers:
                    if h in ["sample", "sample_name"]:
                        continue
                    existing = merged_data[sample][h]
                    new_val = row[h]
                    if not existing:
                        merged_data[sample][h] = new_val
                    elif new_val:
                        existing_set = set(existing.split("; "))
                        new_set = set(new_val.split("; "))
                        merged = "; ".join(sorted(existing_set | new_set))
                        merged_data[sample][h] = merged
            else:
                merged_data[sample] = row

    # Write merged CSV
    with args.output.open("w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for sample in sorted(merged_data.keys()):
            writer.writerow(merged_data[sample])

if __name__ == "__main__":
    main()
