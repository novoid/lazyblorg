# rm -rf testdata/2del/*
mkdir --parents testdata/2del/blog

PYTHONPATH="~/src/lazyblorg:" ./lazyblorg.py \
    --blogname "Testblogname" \
    --aboutblog "lazyblorg test blog" \
    --targetdir testdata/2del/blog \
    --previous-metadata ./NONEXISTING.pk \
    --new-metadata ./2del-metadata.pk \
    --logfile ./2del-logfile.org \
    --orgfiles testdata/manual_prototype/org/test.org ./templates/blog-format.org $@ 
