process SIMPLIFY_IRIDA_JSON {
    tag "$meta.id"
    label 'process_single'

    container 'docker.io/python:3.9.17'

    input:
    tuple val(meta), path(json)

    output:
    tuple val(meta), path("*.simple.json.gz")  , emit: simple_json
    path "versions.yml"                        , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    def is_gzipped = json.getName().endsWith(".gz") ? true : false
    def json_uncompressed_name = json.getName().replace(".gz", "")
    """
    if [ "$is_gzipped" = "true" ]; then
        gzip -c -d $json > $json_uncompressed_name
    fi

    simplify_irida_json.py \\
        $args \\
        --json-output ${meta.id}.simple.json \\
        ${json_uncompressed_name}

    gzip ${meta.id}.simple.json

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        simplify_irida_json : 0.1.0.dev0
    END_VERSIONS
    """
}
