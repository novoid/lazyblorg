#!/bin/sh

## this script calls each unit test script
## if no error is found, the final success statement is shown
## if error occurs, this script stops at the error

end_to_end_test()
{

    ## End-to-end test with multiple Org-mode files resulting
    ## in several different blog files with all kinds of tests:

    echo "\n====> Runing end-to-end test ...\n"

    cd ~/src/lazyblorg
    rm -rf testdata/end_to_end_test/result
    mkdir -p testdata/end_to_end_test/result

    PYTHONPATH="~/src/lazyblorg:" ./lazyblorg.py \
        --targetdir testdata/end_to_end_test/result \
        --autotag-language \
        --previous-metadata testdata/end_to_end_test/lazyblorg-e2e-test-previous-metadata.pk \
        --new-metadata testdata/end_to_end_test/lazyblorg-e2e-test-new-metadata.pk \
        --logfile testdata/end_to_end_test/lazyblorg-e2e-test-logfile.org \
        --orgfiles templates/blog-format.org \
                   testdata/end_to_end_test/orgfiles/*.org  $@ && \
    echo "\n====> Comparing result of end-to-end test ...\n" && \
    if [ `diff -ar testdata/end_to_end_test/result testdata/end_to_end_test/comparison | egrep -vi '(published|updated)' | wc -l` -gt 21 ]; then
        diff -ar testdata/end_to_end_test/result testdata/end_to_end_test/comparison | grep -v '<updated>'
        echo "End-to-end test FAILED!   Check result!"
        exit 1
    else
	## a couple of difference are OK since there are new time-stamps for generation time
        echo "End-to-end test: success."
    fi

}

end_to_end_test $@ && \
echo "\n\n           End-to-end tests ended successfully! :-)\n\n"

#end
