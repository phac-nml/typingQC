# Example pipeline for IRIDA Next

This is an example pipeline to be used for integration with IRIDA Next.

# Input

The input to the pipeline is a standard sample sheet (passed as `--input samplesheet.csv`) that looks like:

| sample  | fastq_1         | fastq_2         |
| ------- | --------------- | --------------- |
| SampleA | file_1.fastq.gz | file_2.fastq.gz |

The structure of this file is defined in [assets/schema_input.json](assets/schema_input.json).

# Parameters

The main parameter is `--input` as defined above and `--output` for specifying the output results directory.

Other parameters (defaults from nf-core) are defined in [nextflow_schema.json](nextflow_schmea.json).

# Running

To run the pipeline, please do:

```bash
nextflow run phac-nml/iridanext-example-nf -profile docker,test -r dev -latest --input samplesheet.csv --outdir results
```

Where the `samplesheet.csv` is structured as above.

# Output

Output JSON file for loading metadata into IRIDA Next is located in `results/irida/output.json.gz`:

```
{
    "files": {
        "samples": {}
    },
    "metadata": {
        "samples": {
            "SAMPLE1_PE_T1": {
                "reads": [
                    "sample1_R1.fastq.gz",
                    "sample1_R2.fastq.gz"
                ]
            },
            "SAMPLE3_SE_T1": {
                "reads": [
                    "sample1_R1.fastq.gz",
                    "null"
                ]
            },
            "SAMPLE3_SE_T2": {
                "reads": [
                    "sample2_R1.fastq.gz",
                    "null"
                ]
            },
            "SAMPLE2_PE_T1": {
                "reads": [
                    "sample2_R1.fastq.gz",
                    "sample2_R2.fastq.gz"
                ]
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

# Legal

Copyright 2023 Government of Canada

Licensed under the MIT License (the "License"); you may not use
this work except in compliance with the License. You may obtain a copy of the
License at:

https://opensource.org/license/mit/

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
