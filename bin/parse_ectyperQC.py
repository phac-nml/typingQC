#!/usr/bin/env python3

import json
import csv
import argparse
from pathlib import Path
import gzip
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract and report ECTyper subtyping QC information from a mikrokondo-generated JSON output file"
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
        "-t", "--validated_toxins", required=True, type=Path,
        help="Path to the file containing validated Escherichia toxin genes (one per line)"
    )
    parser.add_argument(
        "-x", "--validated_stx", required=True, type=Path,
        help="Path to the file containing validated Shiga-toxin producing subtyping genes (one per line)"
    )
    return parser.parse_args()

def load_json(path):
    open_func = gzip.open if path.suffix == ".gz" else open
    with open_func(path, 'rt') as f:
        return json.load(f)

def load_validated_list(file_path):
    """Load a list of validated genes from a text file (one per line)"""
    with file_path.open('r', encoding='utf-8') as f:
        validated_genes = set()
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                validated_genes.add(line)
        # Ensure at least one valid gene is included
        if len(validated_genes) == 0:
            raise ValueError(f"No valid genes found in {file_path}.")
        return validated_genes

#Constants for ECTyper JSON field structure
ECTYPER_PREFIX = "ECTyperSubtyping.0."
SPECIES_KEY = f"{ECTYPER_PREFIX}Species"
SEROTYPE_KEY = f"{ECTYPER_PREFIX}Serotype"
QC_KEY = f"{ECTYPER_PREFIX}QC"
TOXIN_GENES_KEY = f"{ECTYPER_PREFIX}PathotypeGenes"
STX_KEY = f"{ECTYPER_PREFIX}StxSubtypes"

def extract_ectyper_serotype_qc(sample_data):
    """Extract serotyping QC information from ECTyper results"""
    qc_status = sample_data.get(QC_KEY, "")
    serotype = sample_data.get(SEROTYPE_KEY, "")
    species = sample_data.get(SPECIES_KEY, "")

    # Define all QC statuses to quality message mappings
    qc_analysis_messages = {
        "FAIL (-:- TYPING)": "Failed to type either of the O and H antigens",
        "WARNING (-:H TYPING)": "Failed to type O antigen.",
        "WARNING (O:- TYPING)": "Failed to type H antigen.",
        "WARNING (O NON-REPORT)": "O-antigen has %identity or %coverage below reportable threshold",
        "WARNING (H NON-REPORT)": "H-antigen has %identity or %coverage below reportable threshold",
        "WARNING (O AND H NON-REPORT)": "Both O- and H-antigens have %identity or %coverage below reportable thresholds",
        "WARNING UNDIFFERENTIATED O-TYPE": "ECTYPER unable to differentiate between a set of O-antigens due to high sequence similarity (above 99%)",
        "WARNING MIXED O-TYPE": f"Mixed O-type: {serotype}",
        "WARNING (WRONG SPECIES)": f"Species identified not as E.coli but as {species} therefore only the toxin typing was performed on sample"
    }

    # Return appropriate message or empty string for PASS
    if not qc_status or qc_status.upper() == "PASS (REPORTABLE)":
        return ""
    elif qc_status in qc_analysis_messages:
        return qc_analysis_messages[qc_status]
    else:
        # For any other QC warnings/failures, record the QC message from the mikrokondo-generated JSON file
        return qc_status

def build_serotype_rds_qc_message(sample_data):
    """Build RDS QC message based on ECTyper serotyping results"""
    qc_status = sample_data.get(QC_KEY, "")
    serotype = sample_data.get(SEROTYPE_KEY, "")
    species = sample_data.get(SPECIES_KEY, "")

    # Check if serotype was determined
    if not serotype:
        return "[ECTYPER_FAIL] No serotype found in ECTyper results."

    # Define all RDS QC message mappings
    rds_qc_messages = {
        "FAIL (-:- TYPING)": "[ECTYPER_FAIL] RESEQUENCING or TRADITIONAL SEROTYPING is advised.",
        "WARNING (-:H TYPING)": "[ECTYPER_FAIL] RESEQUENCING or TRADITIONAL SEROTYPING is advised.",
        "WARNING (O:- TYPING)": "[ECTYPER_FAIL] RESEQUENCING or TRADITIONAL SEROTYPING is advised.",
        "WARNING (O NON-REPORT)": "[ECTYPER_FAIL] THRESHOLD adjustment, RESEQUENCING or TRADITIONAL SEROTYPING is advised.",
        "WARNING (H NON-REPORT)": "[ECTYPER_FAIL] THRESHOLD adjustment, RESEQUENCING or TRADITIONAL SEROTYPING is advised.",
        "WARNING (O AND H NON-REPORT)": "[ECTYPER_FAIL] THRESHOLD adjustment, RESEQUENCING or TRADITIONAL SEROTYPING is advised.",
        "WARNING UNDIFFERENTIATED O-TYPE": "[ECTYPER_WARNING] Ambiguous Escherichia antigen pairs detected. Refer to DED-C-350C.",
        "WARNING MIXED O-TYPE": "[ECTYPER_WARNING] Mixed O type detected.",
        "WARNING (WRONG SPECIES)": f"[ECTYPER_WARNING] Sample identified as {species}. Serotyping not performed; Toxin typing performed."
    }

    # Handle all conditions for the RDS QC message
    if not qc_status or qc_status.upper() == "PASS (REPORTABLE)":
        return f"[ECTYPER_PASS] Serotype '{serotype}' determined successfully."
    elif qc_status in rds_qc_messages:
        return rds_qc_messages[qc_status]
    else:
        return f"[ECTYPER_FAIL] Serotyping issues detected: {qc_status}. RESEQUENCING or TRADITIONAL SEROTYPING is advised."

def extract_validated_toxins(sample_data, validated_genes, validated_stx):
    """Extract and validate toxin genes and STX subtypes"""
    pathotype_genes = sample_data.get(TOXIN_GENES_KEY, "")
    stx_subtypes = sample_data.get(STX_KEY, "")

    # Process pathotype genes
    validated_toxins_found = []
    if pathotype_genes:
        genes = [gene.strip() for gene in pathotype_genes.split(",")]
        validated_toxins_found = [gene for gene in genes if gene in validated_genes]

    # Process STX subtypes
    validated_stx_found = []
    if stx_subtypes:
        stx_types = [stx.strip() for stx in stx_subtypes.split(";")]
        validated_stx_found = [stx for stx in stx_types if stx in validated_stx]

    return validated_toxins_found, validated_stx_found

def main():
    args = parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input file {args.input} not found.")

    if not args.validated_toxins.exists():
        raise FileNotFoundError(f"Validated genes file {args.validated_toxins} not found.")

    if not args.validated_stx.exists():
        raise FileNotFoundError(f"Validated STX subtypes file {args.validated_stx} not found.")

    # Load and validate JSON structure
    data = load_json(args.input)
    if not isinstance(data, dict) or len(data) != 1:
        raise ValueError("Expected mikrokondo-generated JSON input file to contain a single top-level sample key.")

    # Load validated toxin genes and STX subtypes from separate files
    validated_genes = load_validated_list(args.validated_toxins)
    validated_stx = load_validated_list(args.validated_stx)

    if len(validated_genes) == 0:
        raise ValueError(f"No valid toxin genes found in {args.validated_genes}.")

    if len(validated_stx) == 0:
        raise ValueError(f"No valid STX subtypes found in {args.validated_stx}.")

    # Extract sample data from JSON
    sample_key = next(iter(data))

    # Check if sample_key matches expected sample_id to ensure correct JSON file
    if sample_key != args.sample_id:
        raise ValueError(f"Sample ID mismatch: JSON contains '{sample_key}' but expected '{args.sample_id}'.")

    sample_data = data[sample_key]

    # Check if ECTyper data exists in the JSON file
    if SEROTYPE_KEY not in sample_data and TOXIN_GENES_KEY not in sample_data:
        # No ECTyper data found
        quality_analysis = f"Sample predicted to be {args.species} but no ECTyper data found."
        rds_qc_message = "[FAIL] Re-run mikrokondo to generate ECTyper data."
        validated_toxins_found = []
        validated_stx_found = []
    else:
        # Process serotyping data
        quality_analysis = extract_ectyper_serotype_qc(sample_data)
        rds_qc_message = build_serotype_rds_qc_message(sample_data)

        # Process toxin data
        validated_toxins_found, validated_stx_found = extract_validated_toxins(sample_data, validated_genes, validated_stx)

    # Write serotyping output CSV file
    serotype_output_path = Path(f"{args.sample_id}_ectyperQC.csv")
    with serotype_output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["SAMPLE", "QUALITY_METRICS", "RDS_QC_MESSAGE"])
        writer.writerow([args.sample_id, quality_analysis, rds_qc_message])

    # Write toxin typing output CSV file
    toxin_output_path = Path(f"{args.sample_id}_toxinQC.csv")
    with toxin_output_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Validated_Toxins", "Validated_STXSubtypes"])
        writer.writerow([
            ",".join(validated_toxins_found) if validated_toxins_found else "n/a",
            ",".join(validated_stx_found) if validated_stx_found else "n/a"
        ])

if __name__ == "__main__":
    main()
