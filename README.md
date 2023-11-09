# Example pipeline for IRIDA Next

This is an example pipeline to be used for integration with IRIDA Next.

# Input

The input to the pipeline is a standard sample sheet (passed as `--input samplesheet.csv`) that looks like:

| sample  | fastq_1         | fastq_2         |
| ------- | --------------- | --------------- |
| SampleA | file_1.fastq.gz | file_2.fastq.gz |

The structure of this file is defined in [assets/schema_input.json](assets/schema_input.json). Validation of the sample sheet is performed by [nf-validation](https://nextflow-io.github.io/nf-validation/).

# Parameters

The main parameter is `--input` as defined above and `--output` for specifying the output results directory.

You may wish to provide `-profile singularity` to specify the use of singularity containers and `-r [branch]` to specify which GitHub branch you would like to run.

Other parameters (defaults from nf-core) are defined in [nextflow_schema.json](nextflow_schmea.json).

# Running

To run the pipeline, please do:

```bash
nextflow run phac-nml/iridanext-example-nf -profile singularity -r main -latest --input assets/samplesheet.csv --outdir results
```

Where the `samplesheet.csv` is structured as specified in [Input](#input).

# Output

Output JSON file for loading metadata into IRIDA Next is located in the specified `--outdir` location, as follows: `[outdir]/irida.output.json.gz`:

```
{
    "files": {
        "global": [
            {
                "path": "summary/summary.txt.gz"
            }
        ],
        "samples": {
            "SAMPLE1": [
                {
                    "path": "assembly/SAMPLE1.assembly.fa.gz"
                }
            ],
            "SAMPLE2": [
                {
                    "path": "assembly/SAMPLE2.assembly.fa.gz"
                }
            ],
            "SAMPLE3": [
                {
                    "path": "assembly/SAMPLE3.assembly.fa.gz"
                }
            ]
        }
    },
    "metadata": {
        "samples": {
            "SAMPLE1": {
                "reads.1": "sample1_R1.fastq.gz",
                "reads.2": "sample1_R2.fastq.gz"
            },
            "SAMPLE2": {
                "reads.1": "sample2_R1.fastq.gz",
                "reads.2": "sample2_R2.fastq.gz"
            },
            "SAMPLE3": {
                "reads.1": "sample1_R1.fastq.gz",
                "reads.2": "null"
            }
        }
    }
}
```

There is also some output in the summary file (specified in the above JSON as `"global": [{"path":"summary/summary.txt.gz"})`). However, there is not formatting specification for this file.

## Test profile

To run with the test profile, please do:

```bash
nextflow run phac-nml/iridanext-example-nf -profile docker,test -r main -latest --outdir results
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
