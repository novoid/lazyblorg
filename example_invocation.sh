#!/bin/sh

blog=/tmp/lazyblorg/blog
# create the output directory (and parents):
mkdir -p $blog

# get help on the following parameters:
#     python ./lazyblorg.py --help

# when setting up your own system, you might want to:
# 1. have separate directories for generating your blog and staging/publishing your blog
# 2. copy generated blog data to staging/publishing directory
# 3. point --previous-metadata to the corresponding pk-file in your staging/publishing directory
# 4. modify --orgfiles so that your org-mode files are parsed
#    don't forget to include your version of «about-placeholder.org» and «blog-format.org»

PYTHONPATH="~/src/lazyblorg:" ./lazyblorg.py \
    --targetdir $blog \
    --previous-metadata $blog/metadata.pk \
    --new-metadata $blog/metadata.pk \
    --logfile $(dirname $blog)/logfile.org \
    --orgfiles testdata/end_to_end_test/orgfiles/test.org \
               testdata/end_to_end_test/orgfiles/about-placeholder.org \
               templates/blog-format.org $@

#END
