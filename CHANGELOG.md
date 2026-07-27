# phac-nml/typingQC: Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2026/08/??

### `ADDED`

- Added support for the 'wgmlst_loci_count' QA metric.
- Added CDC serovar rename mappings with nomenclature warning.

### `CHANGED`

- Filtered non-actionable cgMLST INFO messages from SISTR QC output.
- Treated wzx/wzy-only SISTR failures as warnings while continuing serovar reportability checks.

### `FIXED`

- Corrected the CheckM field name to match the current mikrokondo JSON schema and use the 'checkm2_contamination' field.

## [1.0.2] - 2026/03/20

### `CHANGED`

- Updated pipeline to include compatibility of nextflow version 25.10.4. [PR 19](https://github.com/phac-nml/typingQC/pull/19)
- Updated the .github/workflows/ci.yml to run specific versions of nextflow (23.04.0, 24.10.3 and 25.10.4) for nf-test. [PR 19](https://github.com/phac-nml/typingQC/pull/19)

## [1.0.1] - 2026/02/13

### `CHANGED`

- Updated the `SEQUENCEQC` logic to align with revised PNC sequencing quality requirements, including new FAIL and WARNING criteria for read quality, coverage, and assembly metrics.
- Updated the README to reflect the revised sequenceQC behavior and module decision rules.
- For more details see [PR 18](https://github.com/phac-nml/typingQC/pull/18)

## [1.0.0] - 2025/12/04

Initial release of phac-nml/typingQC, created with the [iridanextexample](https://github.com/phac-nml/iridanextexample) and [nf-core](https://nf-co.re/) templates.

### `Added`

### `Fixed`

### `Dependencies`

### `Deprecated`

[1.0.2]: https://github.com/phac-nml/typingQC/releases/tag/1.0.2
[1.0.1]: https://github.com/phac-nml/typingQC/releases/tag/1.0.1
[1.0.0]: https://github.com/phac-nml/typingQC/releases/tag/1.0.0
[Overriding container registries with the container directive]: https://github.com/phac-nml/pipeline-standards?tab=readme-ov-file#521-module-software-requirements
[phac-nml pipeline standards software requirements]: https://github.com/phac-nml/pipeline-standards?tab=readme-ov-file#521-module-software-requirements
