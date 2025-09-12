process EXCLUSIONS {
    tag "Identify why sample(s) failed to be typed"
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python%3A3.12' :
        'biocontainers/python:3.12' }"

    input:
    tuple val(meta), path(mikro_file)

    output:
    tuple val(meta), path("${meta.id}_exclusions.csv"),   emit: results
    path "versions.yml",                                  emit: versions

    script:
    def args = task.ext.args ?: ''
    def species = meta.Species ?: "Unknown"
    def qc_status = meta.QCStatus ?: "Unknown"
    def has_file = mikro_file && mikro_file.size() > 0 ? "--has_mikro_file" :  ""
    """
    parse_untypable.py \\
    --sample_id ${meta.id} \\
    --species "${species}" \\
    --qc_status "${qc_status}" \\
    ${has_file} \\
    ${args}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
