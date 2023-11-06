process IRIDA_NEXT_OUTPUT {
    label 'process_single'

    container 'docker.io/python:3.9.17'

    input:
    path(samples_data)

    output:
    path("output.json.gz"), emit: output_json
    path "versions.yml", emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def samples_data_dir = "samples_data"
    """
    irida-next-output.py \\
        $args \\
        --summary-file ${params.summary_directory_name}/summary.txt \\
        --json-output output.json.gz \\
        ${samples_data}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        irida-next-output : 0.1.0.dev0
    END_VERSIONS
    """
}
