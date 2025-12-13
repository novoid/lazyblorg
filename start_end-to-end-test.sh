#!/usr/bin/env zsh
## this script calls each unit test script
## if no error is found, the final success statement is shown
## if error occurs, this script stops at the error

## load the project settings (depends on your specific path situation!)
. ./shellscriptconfiguration.sh

end_to_end_test()
{

    ## End-to-end test with multiple Org-mode files resulting
    ## in several different blog files with all kinds of tests:

    echo "\n====> Runing end-to-end test ...\n"

    cd "${PROJECTDIR}"
    rm -rf "${PROJECTDIR}/testdata/end_to_end_test/result"
    mkdir -p "${PROJECTDIR}/testdata/end_to_end_test/result"

    uv --project "${PROJECTDIR}" run "${PROJECTDIR}/lazyblorg.py" \
        --targetdir "${PROJECTDIR}/testdata/end_to_end_test/result" \
        --autotag-language \
        --previous-metadata "${PREVIOUS_METADATA_FILE}" \
        --new-metadata "${NEW_METADATA_FILE}" \
        --logfile "${PROJECTDIR}/testdata/end_to_end_test/lazyblorg-e2e-test-logfile.org" \
        --orgfiles "${PROJECTDIR}/templates/blog-format.org" \
                   "${PROJECTDIR}/testdata/end_to_end_test/orgfiles/"*.org $@ && \
    echo "\n====> Comparing result of end-to-end test ...\n" && \
    if [ `diff -ar "${PROJECTDIR}/testdata/end_to_end_test/result" "${PROJECTDIR}/testdata/end_to_end_test/comparison" | egrep -vi '(published|updated)' | wc -l` -gt 15 ]; then
        diff -ar "${PROJECTDIR}/testdata/end_to_end_test/result" "${PROJECTDIR}/testdata/end_to_end_test/comparison" | grep -v '<updated>'
        echo "End-to-end test FAILED!   Check result! You can also use meld: meld \"${PROJECTDIR}/testdata/end_to_end_test/result\" \"${PROJECTDIR}/testdata/end_to_end_test/comparison\""
        exit 1
    else
	## a couple of difference are OK since there are new time-stamps for generation time
        echo "End-to-end test: success."
    fi

}

[ -z "${PROJECTDIR}" ] && { echo "Error: PROJECTDIR not set"; exit 1; }
[ ! -d "${PROJECTDIR}" ] && { echo "Error: ${PROJECTDIR} is not a directory"; exit 2; }

end_to_end_test "$@" && \
echo "\n\n           End-to-end tests ended successfully! :-)\n\n"

#end
