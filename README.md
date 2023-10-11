# Example pipeline for IRIDA Next

This is an example pipeline to be used for integration with IRIDA Next.

# Input

The input to the pipeline is a standard sample sheet (passed as `--input samplesheet.csv`) that looks like:

| sample  | fastq_1         | fastq_2         |
| ------- | --------------- | --------------- |
| SampleA | file_1.fastq.gz | file_2.fastq.gz |

The structure of this file is defined in [assets/schema_input.json][].

# Parameters

Parameters are defined in [nextflow_schema.json][].

# Output

The output of the pipeline is a file `output.json` that can be used to load data into IRIDA Next.
