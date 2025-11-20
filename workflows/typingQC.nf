/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    PRINT PARAMS SUMMARY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { paramsSummaryLog; paramsSummaryMap; fromSamplesheet  } from 'plugin/nf-validation'
include { loadIridaSampleIds                                   } from 'plugin/nf-iridanext'

def logo = NfcoreTemplate.logo(workflow, params.monochrome_logs)
def citation = '\n' + WorkflowMain.citation(workflow) + '\n'
def summary_params = paramsSummaryMap(workflow)

// Print parameter summary log to screen
log.info logo + paramsSummaryLog(workflow) + citation

WorkflowTypingQC.initialise(params, log)

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    CONFIG FILES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT LOCAL MODULES/SUBWORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

include { SEQUENCEQC         } from '../modules/local/sequenceqc/main'
include { SISTRQC            } from '../modules/local/sistrqc/main'
include { ECTYPERQC          } from '../modules/local/ectyperqc/main'
include { EXCLUSIONS         } from '../modules/local/exclusions/main'
include { MERGE_REPORTS      } from '../modules/local/merge_reports/main'

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    IMPORT NF-CORE MODULES/SUBWORKFLOWS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

//
// MODULE: Installed directly from nf-core/modules
//
include { CUSTOM_DUMPSOFTWAREVERSIONS } from '../modules/nf-core/custom/dumpsoftwareversions/main'

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    RUN MAIN WORKFLOW
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow TYPINGQC {

    ch_versions = Channel.empty()

    // Track processed IDS
    def processedIDs = [] as Set

    // Create a new channel of metadata from a sample sheet
    // NB: `input` corresponds to `params.input` and associated sample sheet schema
    input = Channel.fromSamplesheet("input")
        .map { meta, mikro_file ->
            if (!meta.id) {
                meta.id = meta.irida_id
            } else {
                // Non-alphanumeric characters (excluding _,-,.) will be replaced with "_"
                meta.id = meta.id.replaceAll(/[^A-Za-z0-9_.\-]/, '_')
            }
            // Ensure ID is unique by appending meta.irida_id if needed
            while (processedIDs.contains(meta.id)) {
                meta.id = "${meta.id}_${meta.irida_id}"
            }
            // Add the ID to the set of processed IDs
            processedIDs << meta.id

            // Return structured tuple, using a placeholder if input_file is null
            tuple(meta, mikro_file ? [file(mikro_file)] : [])
        }
        .branch {
            salmonella_qcFAIL: !it[1].isEmpty() && it[0].QCStatus == 'FAILED' && (it[0].Species ?: "").contains('Salmonella')
            escherichia_qcFAIL: !it[1].isEmpty() && it[0].QCStatus == 'FAILED' && (it[0].Species ?: "").contains('Escherichia')

            salmonella_PASS: !it[1].isEmpty() && it[0].QCStatus == 'PASSED' && (it[0].Species ?: "").contains('Salmonella')
            escherichia_PASS: !it[1].isEmpty() && it[0].QCStatus == 'PASSED' && (it[0].Species ?: "").contains('Escherichia')

            sequence_FAIL: !it[1].isEmpty() && it[0].QCStatus == 'FAILED'

            fallthrough: true
        }

        sistrqc_input = input.salmonella_PASS.mix(input.salmonella_qcFAIL)
        ectyperqc_input = input.escherichia_PASS.mix(input.escherichia_qcFAIL)
        sequenceqc_input = input.salmonella_qcFAIL.mix(input.escherichia_qcFAIL).mix(input.sequence_FAIL)

    // Create channel for reportable serovars file
    ch_reportable_serovars = Channel.value(file(params.reportable_serovars))

    // Create channel for validated toxin genes
    ch_validated_toxins = Channel.value(file(params.validated_toxins))
    ch_validated_stxsubtypes = Channel.value(file(params.validated_stxsubtypes))

    // Process execution for typing and sequencing results
    sistr_results = SISTRQC(sistrqc_input, ch_reportable_serovars)
    ectyper_results = ECTYPERQC(ectyperqc_input, ch_validated_toxins, ch_validated_stxsubtypes)
    failed_qc_results = SEQUENCEQC(sequenceqc_input)
    untypable_exclusions = EXCLUSIONS(input.fallthrough)

    // Create final consolidated RDS typing report
    // Collect all results
    all_results = sistr_results.results
        .mix(
            ectyper_results.results,
            failed_qc_results.results,
            untypable_exclusions.results
        )

    // Collect CSV files for CSVTK
    report_files = all_results
        .map { meta, csv -> csv }
        .collect()

    MERGE_REPORTS(
        report_files
    )

    CUSTOM_DUMPSOFTWAREVERSIONS (
        ch_versions.unique().collectFile(name: 'collated_versions.yml')
    )
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    COMPLETION EMAIL AND SUMMARY
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/

workflow.onComplete {
    if (params.email || params.email_on_fail) {
        NfcoreTemplate.email(workflow, params, summary_params, projectDir, log)
    }
    NfcoreTemplate.dump_parameters(workflow, params)
    NfcoreTemplate.summary(workflow, params, log)
    if (params.hook_url) {
        NfcoreTemplate.IM_notification(workflow, params, summary_params, projectDir, log)
    }
}

/*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    THE END
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*/
