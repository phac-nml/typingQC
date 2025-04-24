process SEQUENCEQC {
    tag "Identify Sequencing Error"
    label 'process_single'

    input:
    tuple val(meta), path(input_file)

    output:
    path "*_sequence_qc_results.txt",   emit: results
    path "versions.yml",                emit: versions

    script:
    """
    echo "Running SEQUENCEQC on ${meta.id} with file: ${input_file}" > ${meta.id}_sequence_qc_results.txt
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        custom: TBD
    END_VERSIONS
    """
}
