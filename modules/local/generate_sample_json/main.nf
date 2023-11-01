process GENERATE_SAMPLE_JSON {
    tag "$meta.id"
    label 'process_single'

    container 'docker.io/python:3.9.17'

    input:
    tuple val(meta), path(reads), path(assembly)

    output:
    tuple val(meta), path("*.json.gz"), emit: json
    path "versions.yml"               , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    def assembly_path = ["${params.outdir}", "assembly", "${assembly}"].join(File.separator)
    """
    cat <<-EOF > "${meta.id}.json"
    {
        "files": {
            "samples": {
                "${meta.id}": {
                    "assembly_contigs": "${assembly_path}"
                }
            }
        },
        "metadata": {
            "samples": {
                "${meta.id}": {
                    "reads.1": "${reads[0]}",
                    "reads.2": "${reads[1]}"
                }
            }
        }
    }
    EOF
    gzip ${meta.id}.json

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        generate_sample_json : 0.1.0.dev0
    END_VERSIONS
    """
}
