process SEQUENCEQC {
    input:
    tuple val(meta), path(input_file)

    script:
    """
    echo "Running SEQUENCEQC on ${meta.id}"
    """
}
