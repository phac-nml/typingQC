process EXCLUSIONS {
    tag "Identify why sample(s) failed to be typed"
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python%3A3.12' :
        'biocontainers/python:3.12' }"

    input:
    tuple val(meta), path(mikro_file)

    output:
    path "${meta.id}_untypable.csv",   emit: results
    path "versions.yml",               emit: versions

    script:
    def args = task.ext.args ?: ''
    def species = meta.Species ?: "Unknown"
    def has_file = mikro_file.toString() != "[]" && mikro_file.size() >0 ? "true" : "false"
    """
    parse_untypable.py \\
    --sample_id ${meta.id} \\
    --species "${species}" \\
    --has_mikro_file ${has_file} \\
    --output_dir . \\
    ${args}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
