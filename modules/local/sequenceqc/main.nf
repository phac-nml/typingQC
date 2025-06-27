process SEQUENCEQC {
    tag "Identify Sequencing Error"
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python%3A3.12' :
        'biocontainers/python:3.12' }"

    input:
    tuple val(meta), path(mikro_file)

    output:
    path "${meta.id}_sequenceQC.csv",   emit: results
    path "versions.yml",                emit: versions

    script:
    def args = task.ext.args ?: ''
    def species = meta.Species ?: "Unknown"
    def qc_status = meta.QCStatus ?: "Unknown"
    """
    parse_sequenceQC.py \\
    --input ${mikro_file} \\
    --sample_id ${meta.id} \\
    --species "${species}" \\
    ${args}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
