process SISTRQC {
    tag "Verify SISTR Serotyping Results"
    label 'process_single'

    input:
    tuple val(meta), path(input_file)

    output:
    path "*_sistr_qc_results.txt",      emit: results
    path "versions.yml",                emit: versions


    script:
    """
    echo "Running SISTRQC on ${meta.id} with file: ${input_file}" > ${meta.id}_sistr_qc_results.txt
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        custom: TBD
    END_VERSIONS
    """
}
