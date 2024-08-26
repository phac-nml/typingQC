# phac-nml/iridanextexample: Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4]- 2024/08/27

- Fixed nf-core tools linting failures introduced in version 2.14.1.
- Added phac-nml prefix to nf-core config
- Updated container directives to meet requirements of [phac-nml pipeline standards software requirements]
  - Added ternary conditional operator in container section of process directive for singularity containers
  - Replaced docker.io as default docker container registry for quay.io/biocontainers
  - Implemented an example of [overriding container registries with the container directive]

## [1.0.3]- 2024/02/23

- Pinned nf-validation@1.1.3 plugin

## [1.0.2] - 2023/12/18

- Removed GitHub workflows that weren't needed.
- Adding additional parameters for testing purposes.

## [1.0.1] - 2023/12/06

Allowing non-gzipped FASTQ files as input. Default branch is now main.

## [1.0.0] - 2023/11/30

Initial release of phac-nml/iridanextexample, created with the [nf-core](https://nf-co.re/) template.

### `Added`

### `Fixed`

### `Dependencies`

### `Deprecated`

[Overriding container registries with the container directive]: https://github.com/phac-nml/pipeline-standards?tab=readme-ov-file#521-module-software-requirements
[phac-nml pipeline standards software requirements]: https://github.com/phac-nml/pipeline-standards?tab=readme-ov-file#521-module-software-requirements
[1.0.4]: https://github.com/phac-nml/iridanextexample/releases/tag/1.0.4
[1.0.3]: https://github.com/phac-nml/iridanextexample/releases/tag/1.0.3
[1.0.2]: https://github.com/phac-nml/iridanextexample/releases/tag/1.0.2
[1.0.1]: https://github.com/phac-nml/iridanextexample/releases/tag/1.0.1
[1.0.0]: https://github.com/phac-nml/iridanextexample/releases/tag/1.0.0
