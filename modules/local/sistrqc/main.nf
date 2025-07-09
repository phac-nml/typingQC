process SISTRQC {
    tag "Verify SISTR Serotyping Results"
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python%3A3.12' :
        'biocontainers/python:3.12' }"

    input:
    tuple val(meta), path(mikro_file)
    path(reportable_serovars)

    output:
    path "${meta.id}_sistrQC.csv",      emit: results
    path "versions.yml",                emit: versions

    script:
    def args = task.ext.args ?: ''
    def species = meta.Species ?: "Unknown"
    def qc_status = meta.QCStatus ?: "Unknown"
    """
    parse_sistrQC.py \\
    --input ${mikro_file} \\
    --sample_id ${meta.id} \\
    --species "${species}" \\
    --reportables ${reportable_serovars} \\
    ${args}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
