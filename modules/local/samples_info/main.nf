process SAMPLES_INFO {
    tag "$meta.id"
    label 'process_single'

    container 'docker.io/python:3.9.17'

    input:
    tuple val(meta), path(reads)

    output:
    path("*.out")      , emit: info_out
    path "versions.yml", emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    echo "${meta.id}" > ${prefix}_info.out

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
       irida-next-output : 0.1.0
    END_VERSIONS
    """
}
