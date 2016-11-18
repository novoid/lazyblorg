# rm -rf testdata/2del/*
mkdir --parents testdata/2del/blog

PYTHONPATH="~/src/lazyblorg:" ./lazyblorg.py \
    --targetdir testdata/2del/blog \
    --previous-metadata ./NONEXISTING_-_REPLACE_WITH_YOUR_PREVIOUS_METADATA_FILE.pk \
    --new-metadata ./2del-metadata.pk \
    --logfile ./2del-logfile.org \
    --orgfiles testdata/end_to_end_test/orgfiles/test.org \
               testdata/end_to_end_test/orgfiles/about-placeholder.org \
               templates/blog-format.org $@

#END
