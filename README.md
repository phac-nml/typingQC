[![Nextflow](https://img.shields.io/badge/nextflow-%E2%89%A523.04.3-brightgreen.svg)](https://www.nextflow.io/)

# Example Pipeline for IRIDA Next

This is an example pipeline to be used for integration with IRIDA Next.

# Input

The input to the pipeline is a standard sample sheet (passed as `--input samplesheet.csv`) that looks like:

| sample  | fastq_1         | fastq_2         |
| ------- | --------------- | --------------- |
| SampleA | file_1.fastq.gz | file_2.fastq.gz |

The structure of this file is defined in [assets/schema_input.json](assets/schema_input.json). Validation of the sample sheet is performed by [nf-validation](https://nextflow-io.github.io/nf-validation/).

# Parameters

The main parameters are `--input` as defined above and `--output` for specifying the output results directory. You may wish to provide `-profile singularity` to specify the use of singularity containers and `-r [branch]` to specify which GitHub branch you would like to run.

Other parameters (defaults from nf-core) are defined in [nextflow_schema.json](nextflow_schema.json).

# Running

To run the pipeline, please do:

```bash
nextflow run phac-nml/typingQC -profile singularity -r main -latest --input assets/samplesheet.csv --outdir results
```

Where the `samplesheet.csv` is structured as specified in the [Input](#input) section.
For more information see [usage doc](docs/usage.md)

# Output

A JSON file for loading metadata into IRIDA Next is output by this pipeline. The format of this JSON file is specified in our [Pipeline Standards for the IRIDA Next JSON](https://github.com/phac-nml/pipeline-standards#32-irida-next-json). This JSON file is written directly within the `--outdir` provided to the pipeline with the name `iridanext.output.json.gz` (ex: `[outdir]/iridanext.output.json.gz`).

An example of the what the contents of the IRIDA Next JSON file looks like for this particular pipeline is as follows:

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

Within the `files` section of this JSON file, all of the output paths are relative to the `outdir`. Therefore, `"path": "assembly/SAMPLE1.assembly.fa.gz"` refers to a file located within `outdir/assembly/SAMPLE1.assembly.fa.gz`.

There is also a pipeline execution summary output file provided (specified in the above JSON as `"global": [{"path":"summary/summary.txt.gz"}]`). However, there is no formatting specification for this file.

For more information see [output doc](docs/output.md)

## Test profile

To run with the test profile, please do:

```bash
nextflow run phac-nml/typingQC -profile docker,test -r main -latest --outdir results
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
