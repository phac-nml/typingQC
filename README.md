# Example pipeline for IRIDA Next

This is an example pipeline to be used for integration with IRIDA Next.

# Input

The input to the pipeline is a standard sample sheet (passed as `--input samplesheet.csv`) that looks like:

| sample  | fastq_1         | fastq_2         |
| ------- | --------------- | --------------- |
| SampleA | file_1.fastq.gz | file_2.fastq.gz |

The structure of this file is defined in [assets/schema_input.json](assets/schema_input.json).

# Parameters

Parameters are defined in [nextflow_schema.json](nextflow_schmea.json).

# Running

To run the pipeline, please do:

```bash
nextflow run phac-nml/iridanext-example-nf -profile docker,test -r dev -latest --input samplesheet.csv --outdir results
```

Where the `samplesheet.csv` is structured as above.

Output JSON file for IRIDA Next is located in `results/irida/output.json`:

```
{
    "files": {
        "summary": {},
        "samples": {}
    },
    "metadata": {
        "samples": {
            "SAMPLE1_PE_T1_info.out": {
                "output_name": "SAMPLE1_PE_T1_info.out"
            },
            "SAMPLE3_SE_T1_info.out": {
                "output_name": "SAMPLE3_SE_T1_info.out"
            },
            "SAMPLE3_SE_T2_info.out": {
                "output_name": "SAMPLE3_SE_T2_info.out"
            },
            "SAMPLE2_PE_T1_info.out": {
                "output_name": "SAMPLE2_PE_T1_info.out"
            }
        }
    }
}
```

## Test profile

To run with the test profile, please do:

```bash
nextflow run phac-nml/iridanext-example-nf -profile docker,test -r dev -latest --outdir results
```

# Output

The output of the pipeline is a file `output.json` that can be used to load data into IRIDA Next.
