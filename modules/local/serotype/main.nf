process SEROTYPE {
    tag "Validate the serotype from mikrokondo outputs"
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python%3A3.12' :
        'biocontainers/python:3.12' }"

    input:
    val(meta_list)
    path(merged_csv)

    output:
    path("TypingQC_report.csv"),    emit: final_report
    path "versions.yml",            emit: versions

    script:
    // Create a simple string representation of the metadata
    def metadata_args = meta_list.collect { meta ->
        def serotype = meta.Serotype ?: ''
        def sample_id = meta.irida_id
        "--sample_data '${sample_id}:${serotype}'"
    }.join(' ')
    def approve_verification_flag = params.approve_verification ? '--approve_verification' : ''
    """
    validate_serotypes.py \\
        --input ${merged_csv} \\
        ${metadata_args} \\
        ${approve_verification_flag} \\
        --output TypingQC_report.csv

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
