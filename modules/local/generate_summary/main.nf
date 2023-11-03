process GENERATE_SUMMARY {
    label 'process_single'
    container 'docker.io/python:3.9.17'

    input:
    val summaries

    output:
    path("summary.txt.gz"), emit: summary
    path "versions.yml"   , emit: versions

    when:
    task.ext.when == null || task.ext.when

    exec:
    def args = task.ext.args ?: ''    
    def sorted_summaries = summaries.sort{ it[0].id }

    // Generate summary text:
    def summary_text = "IRIDANEXT-EXAMPLE-NF Pipeline Summary\n\nCOMPLETE!\n"

    for (summary in sorted_summaries) {
        summary_text += "\n${summary[0].id}:\n"
        summary_text += "    reads.1: ${summary[1][0]}\n"
        summary_text += "    reads.2: ${summary[1][1]}\n"
        summary_text += "    assembly: ${summary[2]}\n"
    }

    // Create summary text file (GZIP):
    summary_gzip_location = ["${task.workDir}", "summary.txt.gz"].join(File.separator)
    outputStream = new FileOutputStream(summary_gzip_location)
    gzipOutputStream = new java.util.zip.GZIPOutputStream(outputStream)
    printWriter = new PrintWriter(gzipOutputStream)
    printWriter.write(summary_text)
    printWriter.close()

    // Write a versions.yml file:
    version_file_location = ["${task.workDir}", "versions.yml"].join(File.separator)
    version_text = "\n\"${task.process}\":\n    generate_summary : 0.1.0.dev0\n"
    version_file = new File(version_file_location)
    version_file.write(version_text)
}
