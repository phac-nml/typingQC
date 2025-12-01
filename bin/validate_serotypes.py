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

def determine_validated_serotype(typingqc_message, sample_serotype, approve_verification=False):
# Determine the validated serotype based on typingQC message and sample serotype.
    typingqc_upper = str(typingqc_message).upper()
    
    if 'FAIL' in typingqc_upper:
        return 'pending'
    elif 'WARNING' in typingqc_upper:
        if approve_verification:
            # If approving verification, treat like PASS
            if not sample_serotype or sample_serotype.strip() == '':
                return ''
            return sample_serotype
        else:
            # Default behavior for warnings
            return 'verification needed'
    elif 'PASS' in typingqc_upper:
        # If no serotype provided, leave blank
        if not sample_serotype or sample_serotype.strip() == '':
            return ''
        return sample_serotype
    else:
        return 'unknown'

def find_column_indices(header):
# Find the indices of important columns in the CSV header.
    indices = {
        'sample': None,
        'sample_name': None,
        'typingqc_message': None,
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
            
            # Get the serotype for this sample
            sample_serotype = serotype_lookup.get(sample_id, '')
            
            # Determine validated serotype
            validated_serotype = determine_validated_serotype(
                typingqc_message, 
                sample_serotype, 
                approve_verification
            )
            
            # Set the validated serotype in the appropriate column
            if col_indices['validated_serotype'] is not None:
                row[col_indices['validated_serotype']] = validated_serotype
            
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
