process ECTYPERQC {
    input:
    tuple val(meta), path(input_file)

    script:
    """
    echo "Running ECTYPERQC on ${meta.id} with file: ${input_file}"
    """
}
