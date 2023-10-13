process SAMPLE_METADATA {
    tag "$meta.id"
    label 'process_single'

    container 'docker.io/python:3.9.17'

    input:
    tuple val(meta), path(reads)

    output:
    tuple val(meta), path("*.json.gz"), emit: json
    path "versions.yml"               , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    reads_1=`basename ${reads[0]}`
    reads_2=`basename ${reads[1]}`
    cat <<-EOF > "${meta.id}.json"
    {
        "${meta.id}": {
            "reads": [\${reads_1}, \${reads_2}]
        }
    }
    EOF
    gzip ${meta.id}.json

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        irida-next-output : 0.1.0.dev0
    END_VERSIONS
    """
}
