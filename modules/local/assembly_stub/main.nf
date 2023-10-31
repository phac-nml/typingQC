process ASSEMBLY_STUB {
    tag "$meta.id"
    label 'process_single'

    input:
    tuple val(meta), path(reads)

    output:
    path("*.assembly.fa.gz"), emit: assembly
    path "versions.yml"     , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def prefix = task.ext.prefix ?: "${meta.id}"
    """
    cat <<EOF > ${prefix}.assembly.fa
    >${meta.id}-stub-assembly
    ACGTAACCGGTTAAACCCGGGTTTAAAACCCCGGGGTTTTAAAAACCCCCGGGGGTTTTT
    EOF

    gzip -n ${prefix}.assembly.fa

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        assembly_stub : 0.1
    END_VERSIONS
    """
}
