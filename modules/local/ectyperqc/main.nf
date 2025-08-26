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
    path "${meta.id}_ectyperQC.csv",     emit: serotype_results
    path "${meta.id}_toxinQC.csv",       emit: toxin_results
    path "versions.yml",                 emit: versions

    when:
    meta.Species && meta.Species.toLowerCase().contains('escherichia')

    script:
    def args = teask.ext.args ?: ''
    """
    parse_ectyperqc.py \\
    --input ${mikro_file} \\
    --sample_id ${meta.id} \\
    --species "${meta.Species}" \\
    --validated_toxins ${validated_toxins} \\
    --validated_stx ${validated_stx} \\
    ${args}
    
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
