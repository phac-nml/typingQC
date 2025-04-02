process SISTRQC {
    input:
    tuple val(meta), path(input_file)

    script:
    """
    echo "Running SISTRQC on ${meta.id} with file: ${input_file}"
    """
}
