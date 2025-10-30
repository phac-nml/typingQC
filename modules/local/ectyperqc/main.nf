process ECTYPERQC {
    tag "Verify ECTyper Sero and Virulence Typing Results"
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python%3A3.12' :
        'biocontainers/python:3.12' }"

    input:
    tuple val(meta), path(mikro_file)
    path(validated_toxins)
    path(validated_stx)

    output:
    tuple val(meta), path("${meta.id}_ectyperQC.csv"),     emit: results
    path "versions.yml",                                   emit: versions

    script:
    """
    parse_ectyperQC.py \\
    --input ${mikro_file} \\
    --sample_id ${meta.id} \\
    --irida_id ${meta.irida_id} \\
    --species "${meta.Species}" \\
    --validated_toxins ${validated_toxins} \\
    --validated_stx ${validated_stx}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
