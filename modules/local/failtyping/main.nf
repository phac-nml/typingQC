process FAIL_TYPING {
    tag "Identify why sample(s) failed to be typed"
    label 'process_single'

    input:
    tuple val(meta), path(mikro_file)

    output:
    path "*_fail_typing_results.txt",   emit: results
    path "versions.yml",                emit: versions

    script:
    def reason = mikro_file ? "The typing file is present but the species is not Escherichia or Salmonella" : "The typing file is missing"
    """
    echo "Sample ${meta.id} ${meta.Species} failed typing. Reason: ${reason}" > ${meta.id}_fail_typing_results.txt
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        custom: TBD
    END_VERSIONS
    """
}
