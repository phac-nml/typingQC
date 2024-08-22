process IRIDA_NEXT_OUTPUT {
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.10' :
        'biocontainers/python:3.10' }"

    input:
    path(samples_data)

    output:
    path("iridanext.output.json.gz"), emit: output_json
    path "versions.yml", emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def samples_data_dir = "samples_data"
    """
    irida-next-output.py \\
        $args \\
        --summary-file ${task.summary_directory_name}/summary.txt.gz \\
        --json-output iridanext.output.json.gz \\
        ${samples_data}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        iridanextoutput : 0.1.0
    END_VERSIONS
    """
}
