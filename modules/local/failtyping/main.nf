process FAIL_TYPING {
    tag "Identify why sample(s) failed to be typed"
    label 'process_single'

    input:
    val(meta)

    output:
    path "*_fail_typing_results.txt",   emit: results
    path "versions.yml",                emit: versions

    script:
    """
    echo " If ${meta.id} ${meta.Species} is not Escherichia or Salmonella, it is not a REPORTABLE SPECIES. Or the typing file could be missing" > ${meta.id}_fail_typing_results.txt
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        custom: TBD
    END_VERSIONS
    """
}
