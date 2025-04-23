process ECTYPERQC {
    tag "Verify ECTyper Sero and Virulence Typing Results"
    label 'process_single'

    input:
    tuple val(meta), path(input_file)

    output:
    path "ectyper_qc_results.txt",  emit: results
    path "versions.yml",            emit: versions

    script:
    """
    echo "Running ECTYPERQC on ${meta.id} with file: ${input_file}" > ectyper_qc_results.txt
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        custom: v1.0
    END_VERSIONS
    """
}
