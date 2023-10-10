process IRIDA_NEXT_OUTPUT {
    tag "$meta.id"
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
    def prefix = task.ext.prefix ?: "${meta.id}"
    def samples_data_dir = "samples_data"
    """
    # Copy all input data files into a single directory
    if [ -e ${samples_data_dir} ]
    then
        rm -rf ${samples_data_dir}
    fi

    mkdir ${samples_data_dir}

    for file in ${samples_data}
    do
        ln -s ../${file} ${samples_data_dir}
    done

    irida-next-output.py \\
        $args \\
        --samples-data-dir ${samples_data_dir} \\
        --json-output output.json

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
       irida-next-output : 0.1.0
    END_VERSIONS
    """
}
