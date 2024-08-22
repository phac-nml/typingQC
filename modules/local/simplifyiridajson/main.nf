process SIMPLIFY_IRIDA_JSON {
    tag "$meta.id"
    label 'process_single'

    // Container directive is intentionally using the "override_configure_container_registry" as an example:
    // How to keep a non-biocontainer/quay.io default, see nextflow.config for details

    container "${ task.ext.override_configured_container_registry != false ?
    'docker.io/python:3.10' :
    'python:3.10' }"

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
    """
    simplify_irida_json.py \\
        $args \\
        --json-output ${meta.id}.simple.json \\
        ${json}

    gzip ${meta.id}.simple.json

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        simplifyiridajson : 0.1.0
    END_VERSIONS
    """
}
