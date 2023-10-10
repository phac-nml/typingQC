process IRIDA_NEXT_OUTPUT {
    label 'process_single'

    container 'docker.io/python:3.9.17'

    input:
    path(samples_data)

    output:
    path("output.json"), emit: output_json
    path "versions.yml", emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def samples_data_dir = "samples_data"
    """
    # Copy all input data files into a single directory
    if [ -e ${samples_data_dir} ]
    then
        rm -rf ${samples_data_dir}
    fi

    mkdir ${samples_data_dir}
    echo ${samples_data}

    #cp ${samples_data} ${samples_data_dir}

    #irida-next-output.py \\
    #    $args \\
    #    --samples-data-dir ${samples_data_dir} \\
    #    --json-output output.json
    echo ${samples_data} > output.json

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
       irida-next-output : 0.1.0
    END_VERSIONS
    """
}
