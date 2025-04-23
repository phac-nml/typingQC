process SISTRQC {
    tag "Verify SISTR Serotyping Results"
    label 'process_single'

    input:
    tuple val(meta), path(input_file)

    output:
    path "sistr_qc_results.txt",    emit:results
    path "versions.yml",            emit: versions


    script:
    """
    echo "Running SISTRQC on ${meta.id} with file: ${input_file}" > sistr_qc_results.txt
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        custom: v1.0
    END_VERSIONS
    """
}
