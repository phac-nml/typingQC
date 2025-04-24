process FAIL_TYPING {
    tag "Identify why sample(s) failed to be typed"
    label 'process_single'

    input:
    val(meta)

    output:
    path "fail_typing_results.txt",    emit: results
    path "versions.yml",               emit: versions

    script:
    """
    echo "NOT A REPORTABLE SPECIES" > fail_typing_results.txt
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        custom: v1.0
    END_VERSIONS
    """
}
