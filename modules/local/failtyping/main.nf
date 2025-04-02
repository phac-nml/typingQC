process FAIL_TYPING {
    input:
    tuple val(meta), path(input_file)

    script:
    """
    echo "FAIL - Not a typable species: ${meta.predicted_identification_name}" >&2
    exit 1
    """
}
