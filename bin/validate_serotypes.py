#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate serotypes based on typing QC results and sample metadata."
    )
    parser.add_argument(
        "--input", required=True, help="Input merged CSV file"
    )
    parser.add_argument(
        "--sample_data", action='append', required=True,
        help="Sample data in format 'sample_id:serotype' (can be used multiple times)"
    )
    parser.add_argument(
        "--output", required=True, help="Output CSV file with validated serotypes"
    )
    parser.add_argument(
        "--approve_verification", action='store_true',
        help="Approve samples with WARNING messages and use predicted serotype instead of 'verification needed'"
    )
    return parser.parse_args()

def create_serotype_lookup(sample_data_list):
# Create a lookup dictionary for serotypes by sample ID.
    serotype_lookup = {}

    for sample_data in sample_data_list:
        try:
            sample_id, serotype = sample_data.split(':', 1)
            serotype_lookup[sample_id] = serotype
        except ValueError:
            print(f"Warning: Invalid sample data format: {sample_data}", file=sys.stderr)
            continue

    return serotype_lookup

# Serovar rename mappings: predicted serovar -> validated reportable name (CDC)
# Add new entried here as nomenclature changes are required
SEROVAR_RENAME_MAP = {
    "Panama": "Panama/Houston",
    "Sendai": "Miami"
}

# Quality metrics warnings to append when a rename is applied
SEROVAR_RENAME_WARNINGS = {
    "Sendai": "WARNING: Predicted serovar Sendai has been reported as Miami to conform with current CDC serovar nomenclature."
}

def apply_serovar_rename(serotype, quality_metrics):
# If serotype matched a knoen rename mappung, return the renamed validated serotype and updated quality_metrics string. Otherwsie return the inputs unchanged.
    if serotype not in SEROVAR_RENAME_MAP:
        return serotype, quality_metrics

    renamed = SEROVAR_RENAME_MAP[serotype]
    warning = SEROVAR_RENAME_WARNINGS.get(serotype)

    if warning:
        #Append warning to existing quality_metics content if present
        updated_metrics = f"{quality_metrics}; {warning}" if quality_metrics.strip() else warning
    else:
        updated_metrics = quality_metrics

    return renamed, updated_metrics

def determine_validated_serotype(typingqc_message, sample_serotype, quality_metrics, approve_verification=False):
# Determine the validated serotype based on typingQC message and sample serotype. Returns validated_serotype, updated_quality_metrics
    typingqc_upper = str(typingqc_message).upper()

    if 'FAIL' in typingqc_upper:
        return 'pending', quality_metrics
    
    elif 'WARNING' in typingqc_upper:
        if approve_verification:
            # If approving verification, treat like PASS
            if not sample_serotype or sample_serotype.strip() == '':
                return '', quality_metrics
            return apply_serovar_rename(sample_serotype, quality_metrics)
        else:
            # Default behavior for warnings
            return 'verification needed', quality_metrics
    
    elif 'PASS' in typingqc_upper:
        # If no serotype provided, leave blank
        if not sample_serotype or sample_serotype.strip() == '':
            return '', quality_metrics
        return apply_serovar_rename(sample_serotype, quality_metrics)
    else:
        return 'unknown', quality_metrics

def find_column_indices(header):
# Find the indices of important columns in the CSV header.
    indices = {
        'sample': None,
        'sample_name': None,
        'typingqc_message': None,
        'quality_metrics': None,
        'validated_serotype': None
    }

    for i, col in enumerate(header):
        col_lower = col.lower()
        if col_lower == 'sample':
            indices['sample'] = i
        elif col_lower == 'sample_name':
            indices['sample_name'] = i
        elif col_lower == 'typingqc_message':
            indices['typingqc_message'] = i        
        elif col_lower == 'quality_metrics':
            indices['quality_metrics'] = i
        elif col_lower == 'validated_serotype':
            indices['validated_serotype'] = i

    return indices

def process_csv_file(input_path, serotype_lookup, output_path, approve_verification=False):
    # Process the CSV file and add validated serotype column.
    rows = []
 
    with input_path.open('r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
 
        # Read header
        header = next(reader, None)
        if header is None:
            print(f"Error: Input file '{input_path}' is empty", file=sys.stderr)
            sys.exit(1)
 
        # Add the new column to header if it doesn't exist
        if 'Validated_Serotype' not in header:
            header.append('Validated_Serotype')
 
        # Find column indices
        col_indices = find_column_indices(header)
 
        # Process each row
        for row in reader:
            if len(row) == 0:  # Skip empty rows
                continue
 
            # Ensure row has enough columns
            while len(row) < len(header):
                row.append('')
 
            # Get sample identifier - use 'sample' column (matches meta.irida_id)
            sample_id = ''
            if col_indices['sample'] is not None and len(row) > col_indices['sample']:
                sample_id = row[col_indices['sample']]
 
            # Get typingQC message
            typingqc_message = ''
            if col_indices['typingqc_message'] is not None and len(row) > col_indices['typingqc_message']:
                typingqc_message = row[col_indices['typingqc_message']]
 
            # Get existing quality_metrics value
            quality_metrics = ''
            if col_indices['quality_metrics'] is not None and len(row) > col_indices['quality_metrics']:
                quality_metrics = row[col_indices['quality_metrics']]
 
            # Get the serotype for this sample
            sample_serotype = serotype_lookup.get(sample_id, '')
 
            # Determine validated serotype and updated quality_metrics
            validated_serotype, updated_quality_metrics = determine_validated_serotype(
                typingqc_message,
                sample_serotype,
                quality_metrics,
                approve_verification,
            )
 
            # Write validated serotype and (possibly updated) quality_metrics back to row
            if col_indices['validated_serotype'] is not None:
                row[col_indices['validated_serotype']] = validated_serotype
            if col_indices['quality_metrics'] is not None:
                row[col_indices['quality_metrics']] = updated_quality_metrics
 
            rows.append(row)

    # Write the output CSV file
    with output_path.open('w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)

    return len(rows)

def main():
    args = parse_args()

    # Check if input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    # Create serotype lookup from sample data
    serotype_lookup = create_serotype_lookup(args.sample_data)

    # Process the CSV file
    output_path = Path(args.output)
    try:
        num_samples = process_csv_file(
            input_path,
            serotype_lookup,
            output_path,
            args.approve_verification
        )
        print(f"Successfully processed {num_samples} samples")
        if args.approve_verification:
            print("WARNING samples were approved - using predicted serotypes")
        print(f"Output written to: {args.output}")
    except Exception as e:
        print(f"Error processing file: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
