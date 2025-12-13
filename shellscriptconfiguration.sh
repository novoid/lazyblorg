## This file contains the most important environment variables for the shell scripts (not the Python scripts):

export PROJECTDIR="${HOME}/src/lazyblorg"
export TEMP_RESULT_DIR="${HOME}/public_html"
export FINAL_DESTINATION_DIR="${HOME}/share/karl-voit.at"

export PREVIOUS_METADATA_FILE="${TEMP_RESULT_DIR}/public_voit-metadata.pk"
export NEW_METADATA_FILE="${PROJECTDIR}/testdata/2del/blog/public_voit-metadata.pk"
export ERROR_INDICATION_FILE="${PROJECTDIR}/testdata/2del/blog/WORK_IN_PROGRESS.regenerate_public_voit.delete_me"
export LOGFILE="${HOME}/org/errors.org"
export OMIT_TESTS_FILE="OMIT_TESTS.2del"
export PREVIOUS_FEEDS_FOR_COMPARISON_TEMPDIR=$(mktemp -d)
export METADATA_OF_PREVIOUS_EXECUTION="${PROJECTDIR}/.regenerate_public_voit_last_run.log"

export ORGDOWN_FILES=(
    ./templates/blog-format.org
    ./testdata/end_to_end_test/orgfiles/currently_supported_orgmode_syntax.org
    ~/org/(public_voit|misc|contacts|foodandbeverages|hardware|movies|notes|references|finanzen_behoerden_versicherungen|issues|projects).org*(N)
)
