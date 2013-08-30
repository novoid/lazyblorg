PYTHONPATH="~/src/lazyblorg:" ./lazyblorg.py \
    --aboutblog "lazyblorg test blog" \
    --targetdir testdata/2del \
    --metadata ./2del-metadata.pk \
    --template ./templates/blog-format.org \
    --logfile ./2del-logfile.org \
    --orgfiles testdata/manual_prototype/org/test.org $@ 
