process CSVTK {
    tag "Create RDS_report"
    label 'process_low'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/csvtk:0.31.0--h9ee0642_0' :
        'biocontainers/csvtk:0.31.0--h9ee0642_0' }"

    input:
    path(csv)
    val in_format
    val out_format

    output:
    path("*.${out_extension}"),          emit: csv
    path "versions.yml",                 emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args   ?: ''
    def delimiter = in_format == "tsv" ? "\t" : (in_format == "csv" ? "," : in_format)
    def out_delimiter = out_format == "tsv" ? "\t" : (out_format == "csv" ? "," : out_format)
    out_extension = out_format == "tsv" ? 'tsv' : 'csv'
    """
    # Concatenate all CSV files first
    csvtk concat \\
        $args \\
        --num-cpus $task.cpus \\
        --delimiter "${delimiter}" \\
        --out-delimiter "${out_delimiter}" \\
        $csv > temp_concat.csv

    # Create separate files for each field to merge
    csvtk fold \\
        --fields sample \\
        --vfield rds_qc_message \\
        --separater "; " \\
        temp_concat.csv > quality_merged.csv

    csvtk fold \\
        --fields sample \\
        --vfield quality_metrics \\
        --separater "; " \\
        temp_concat.csv > message_merged.csv

    # Join the two merged files back together
    csvtk join \\
        --fields sample \\
        quality_merged.csv message_merged.csv > RDS_report.${out_extension}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        csvtk: \$(echo \$( csvtk version | sed -e "s/csvtk v//g" ))
    END_VERSIONS
    """
}
