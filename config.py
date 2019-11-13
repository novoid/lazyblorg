# -*- coding: utf-8; mode: python; -*-
import os

## ===================================================================== ##
##                                                                       ##
##  These are lazyblorg-global configuration settings.                   ##
##                                                                       ##
##  You might not want to modify anything if you do not know, what       ##
##  you are doing :-)                                                    ##
##                                                                       ##
##  You can evaluate basic format and constraints with:                  ##
##                                                   python ./config.py  ##
##                                                                       ##
## ===================================================================== ##


## INTEGRATION: modify variables in this file according to your requirements


# strings: Your personal name and the name of your blog:
AUTHOR_NAME = 'Karl Voit'
BLOG_NAME = 'public voit'

## strings: Define your URLs and your name below:
DOMAIN = 'Karl-Voit.at'
BASE_URL = '//' + DOMAIN
CSS_URL = BASE_URL + '/public_voit.css'
BLOG_LOGO = BASE_URL + '/images/public-voit_logo.svg'
DISQUS_NAME = 'publicvoit'  # gets placed in: '//publicvoit.disqus.com/embed.js'

## string: Email address to send comments to:
COMMENT_EMAIL_ADDRESS = 'publicvoit-comment@Karl-Voit.at'

## integer: Show this many article teasers on entry page
NUMBER_OF_TEASER_ARTICLES = 25

## integer: Show this many top tags in the sidebar
NUMBER_OF_TOP_TAGS = 10

## list of strings: tags to ignore when generating misc things:
IGNORE_FOR_TOP_TAGS = ['suderei', 'personally']
IGNORE_FOR_TAG_CLOUD = ['suderei', 'personally', 'hardware', 'software']

## integer: Show this many article in Atom feeds:
NUMBER_OF_FEED_ARTICLES = 25

## string: This is the Org-mode property :ID: of your blog article which
##         is used for the about page of your blog.
## See example in: testdata/end_to_end_test/orgfiles/about-placeholder.org
ID_OF_ABOUT_PAGE = '2014-03-09-about'

## string: This is the Org-mode property :ID: of your blog article which
##         is used for the "How to use this blog efficiently" page of your blog.
ID_OF_HOWTO_PAGE = '2017-01-03-how-to-use-public-voit'

## string: Your Twitter handle/username which is used in the HTML header
##         metadata (without the @ character)
TWITTER_HANDLE = 'n0v0id'

## string: An image which is added to the HTML header metadata and is used
##         by Twitter in Twitter cards to visualize your blog (also used
##         as og:image)
TWITTER_IMAGE = 'http://Karl-Voit.at/images/public-voit_T_logo_200x200.png'

## string: Replace "+01:00" below with your time-zone indicator
## This string gets added to the time strings in order to describe time zone of the blog:
TIME_ZONE_ADDON = '+01:00'

## string: Customized link key for linking image files within an article
## See https://www.gnu.org/software/emacs/manual/html_node/org/Link-abbreviations.html
## Links that look like "[[tsfile:2017-06-06 a file name.jpg][an optional title]]" are
## replaced with the link to the image "2017-06-06 a file name.jpg" with is either
## - indexed by the Memacs module for filenames containing ISO datestamp:
##   MEMACS_FILE_WITH_IMAGE_FILE_INDEX
##   See https://github.com/novoid/Memacs/blob/master/docs/memacs_filenametimestamps.org
## - or which can be found in the folder stated in DIRECTORIES_WITH_IMAGE_ORIGINALS
##   or one of its sub-folders.
## EMPTY string if including images is disabled
## Please do read the documentation: https://github.com/novoid/lazyblorg/wiki/Orgmode-Elements#images
CUSTOMIZED_IMAGE_LINK_KEY = 'tsfile'  # short for "time-stamp filename"

## string: (optional) path to an existing folder which is used to copy images that
## were resized too meet the width stated by the user (ATTR). To speed up blog data
## generation time, the resized images that have a more recent modification time
## compared to the original file are stored here and copied to the target directory
## on blog data generation time.
## EMPTY string or non-existing path to a folder if image cache is disabled.
IMAGE_CACHE_DIRECTORY = os.path.join(os.path.expanduser("~"), *"src/lazyblorg/testdata/imagecache".split('/'))

## string: path to the Memacs index for filenametimestamps
## Note that the method below is the safe one that works on Windows
## and other operating systems. Alternatively you can use something
## like "/home/user/dir1/memacs_files.org_archive" as string.
## EMPTY string if including images via Memacs index is disabled
## Please do read the documentation: https://github.com/novoid/lazyblorg/wiki/Orgmode-Elements#images
MEMACS_FILE_WITH_IMAGE_FILE_INDEX = os.path.join(os.path.expanduser("~"), "org", "memacs", "files.org_archive")

## string: path to a directory that holds image files (+ sub-directories)
## EMPTY string if including images via traversing the file system is disabled
## Please do read the documentation: https://github.com/novoid/lazyblorg/wiki/Orgmode-Elements#images
DIRECTORIES_WITH_IMAGE_ORIGINALS = ["testdata/testimages",
                                    os.path.join(os.path.expanduser("~"), *"tmp/digicam/tmp".split('/')),
                                    os.path.join(os.path.expanduser("~"), *"tmp/digicam/oneplus5".split('/')),
                                    os.path.join(os.path.expanduser("~"), *"archive/events_memories/2019".split('/')),
                                    os.path.join(os.path.expanduser("~"), *"archive/fromweb/cliparts".split('/'))]

## string: a filetags-tag - see
## http://karl-voit.at/managing-digital-photographs/ and
## https://github.com/novoid/filetags for explanation of filetags
## EMPTY if no check is enforced
## If not empty: Contains a tag which should be part of any image
## file included. If the image file does not contain this filetag,
## a warning is issued in the console output.
WARN_IF_IMAGE_FILE_NOT_TAGGED_WITH="publicvoit"

## According to https://github.com/novoid/lazyblorg/wiki/Images
## you can link to a differently sized image when including a
## (smaller) image to a blog article.
## In order to give the page reader a hint that there is actually
## the possibility to see the same image in a different (usually
## larger) size, you can define help texts here.
## Note: there is a dependency to Utils.STOPWORDS for the detected
## languages for the blog article (auto-tags). Therefore, the following
## dict has to map defined languages to the texts. If you need
## another language, you need to make sure the auto-tag mechanism
## within Utils is extended as well and the language identifier
## matches the dict keys below.
CLUE_TEXT_FOR_LINKED_IMAGES = {'german': '(klicken für größere Version)',
                               'english': '(click for a larger version)'}

## ===================================================================== ##
##                                                                       ##
##  These are INTERNAL lazyblorg-global configuration settings.          ##
##                                                                       ##
##  You might not want to modify anything if you do not REALLY know,     ##
##  what you are doing :-)                                               ##
##                                                                       ##
## ===================================================================== ##


## the assert-statements are doing basic sanity checks on the configured variables
## please do NOT change them unless you are ABSOLUTELY sure what this means for the rest of lazyblorg!

assert(type(BASE_URL) == str)
assert(BASE_URL.startswith('//'))
assert(type(AUTHOR_NAME) == str)

assert(type(NUMBER_OF_TEASER_ARTICLES) == int)
assert(NUMBER_OF_TEASER_ARTICLES > -1)

assert(type(NUMBER_OF_FEED_ARTICLES) == int)
assert(NUMBER_OF_FEED_ARTICLES > -1)

assert(len(ID_OF_ABOUT_PAGE) > 0)
assert(len(ID_OF_HOWTO_PAGE) > 0)

import re
assert(re.match(r'(\+|-)[01][0123456789]:[012345][0123456789]', TIME_ZONE_ADDON))

def assertTag(tag):
    """
    checks formal criteria of an Org-mode tag
    """
    assert(type(tag) == str)
    assert(' ' not in tag)
    assert(':' not in tag)
    assert('-' not in tag)


## string of the state which defines a blog entry to be published; states are not shown in result page
BLOG_FINISHED_STATE = 'DONE'

assertTag(BLOG_FINISHED_STATE)


## tag that is expected in any blog entry category; tag does not get shown in list of user-tags
TAG_FOR_BLOG_ENTRY = 'blog'

assertTag(TAG_FOR_BLOG_ENTRY)


## if an entry is tagged with this, it's an TAGS entry; tag does not get shown in list of user-tags
TAG_FOR_TAG_ENTRY = 'lb_tags'

assertTag(TAG_FOR_TAG_ENTRY)


## if an entry is tagged with this, it's an PERSISTENT entry; tag does not get shown in list of user-tags
TAG_FOR_PERSISTENT_ENTRY = 'lb_persistent'

assertTag(TAG_FOR_PERSISTENT_ENTRY)


## if an entry is tagged with this, it's an TEMPLATES entry; tag does not get shown in list of user-tags
TAG_FOR_TEMPLATES_ENTRY = 'lb_templates'

assertTag(TAG_FOR_TEMPLATES_ENTRY)


## if an entry is tagged with this, it will be omitted in feeds, the main page, and navigation pages; tag is shown in result page
TAG_FOR_HIDDEN = 'hidden'

assertTag(TAG_FOR_HIDDEN)


## INTERNAL category names of blog entries:
TAGS = 'TAGS'
PERSISTENT = 'PERSISTENT'
TEMPORAL = 'TEMPORAL'
TEMPLATES = 'TEMPLATES'
ENTRYPAGE = 'ENTRYPAGE'
TAGOVERVIEWPAGE = 'TAGOVERVIEWPAGE'

assert(type(TAGS) == str)
assert(type(PERSISTENT) == str)
assert(type(TEMPORAL) == str)
assert(type(TEMPLATES) == str)
assert(type(ENTRYPAGE) == str)
assert(type(TAGOVERVIEWPAGE) == str)


## base directory of the RSS/ATOM feeds:
FEEDDIR = 'feeds'

assert(type(FEEDDIR) == str)


# 2018-09-23 Deprecated with migration to Python 3: PICKLE_FORMAT


## checking image inclusion variables:
assert(type(CUSTOMIZED_IMAGE_LINK_KEY) == str)
assert(type(MEMACS_FILE_WITH_IMAGE_FILE_INDEX) == str)
assert(type(DIRECTORIES_WITH_IMAGE_ORIGINALS) == list)

# If DIRECTORIES_WITH_IMAGE_ORIGINALS is a relative path, derive the absolute path:
index = 0
dir_set_and_found = False
dir_set_and_not_found = None
for currentdir in DIRECTORIES_WITH_IMAGE_ORIGINALS:
    if not os.path.isabs(currentdir):
        DIRECTORIES_WITH_IMAGE_ORIGINALS[index] = os.path.join(os.getcwd(), currentdir)
    if os.path.isdir(DIRECTORIES_WITH_IMAGE_ORIGINALS[index]):
        dir_set_and_found = True
    else:
        print('Warning: DIRECTORIES_WITH_IMAGE_ORIGINALS[' + str(index) + '] which is set to \"' + str(currentdir) + '\" is not an existing directory. It will be ignored.')
    index += 1

# define the three possibilities to include image files:
IMAGE_INCLUDE_METHOD = False
IMAGE_INCLUDE_METHOD_MEMACS = 1
IMAGE_INCLUDE_METHOD_MEMACS_THEN_DIR = 2
IMAGE_INCLUDE_METHOD_DIR = 3

## check for the correct image include settings:
if len(CUSTOMIZED_IMAGE_LINK_KEY) > 0:
    file_not_set = len(MEMACS_FILE_WITH_IMAGE_FILE_INDEX) < 1
    file_set_and_found = len(MEMACS_FILE_WITH_IMAGE_FILE_INDEX) > 1 and os.path.isfile(MEMACS_FILE_WITH_IMAGE_FILE_INDEX)
    file_set_and_not_found = len(MEMACS_FILE_WITH_IMAGE_FILE_INDEX) > 1 and not os.path.isfile(MEMACS_FILE_WITH_IMAGE_FILE_INDEX)
    dir_not_set = len(DIRECTORIES_WITH_IMAGE_ORIGINALS) < 1
    dir_set_and_not_found = len(DIRECTORIES_WITH_IMAGE_ORIGINALS) > 1 and not dir_set_and_found

    if file_set_and_not_found:
        print("Warning: MEMACS_FILE_WITH_IMAGE_FILE_INDEX is not empty but contains no existing file. Please fill it with an existing filename containing a Memacs file index or set either MEMACS_FILE_WITH_IMAGE_FILE_INDEX or CUSTOMIZED_IMAGE_LINK_KEY to an empty string.")
    if dir_set_and_not_found:
        print("Warning: DIRECTORIES_WITH_IMAGE_ORIGINALS is not empty but contains no path to an existing directory. Please fill it with an existing path to a directory or set either DIRECTORIES_WITH_IMAGE_ORIGINALS or CUSTOMIZED_IMAGE_LINK_KEY to an empty string.")

    # three to the power of two: nine possibilities
    if file_set_and_found:
        if dir_set_and_found:
            IMAGE_INCLUDE_METHOD = IMAGE_INCLUDE_METHOD_MEMACS_THEN_DIR
        elif dir_not_set or dir_set_and_not_found:
            IMAGE_INCLUDE_METHOD = IMAGE_INCLUDE_METHOD_MEMACS
    elif file_not_set:
        if dir_set_and_found:
            IMAGE_INCLUDE_METHOD = IMAGE_INCLUDE_METHOD_DIR
        elif dir_not_set or dir_set_and_not_found:
            print("Error: if CUSTOMIZED_IMAGE_LINK_KEY is set, at least one of MEMACS_FILE_WITH_IMAGE_FILE_INDEX or DIRECTORIES_WITH_IMAGE_ORIGINALS has to be filled and point to an existing file/directory.")
            import sys
            sys.exit(10)
    elif file_set_and_not_found:
        if dir_set_and_found:
            IMAGE_INCLUDE_METHOD = IMAGE_INCLUDE_METHOD_DIR
        elif dir_not_set or dir_set_and_not_found:
            print("Error: if CUSTOMIZED_IMAGE_LINK_KEY is set, at least one of MEMACS_FILE_WITH_IMAGE_FILE_INDEX or DIRECTORIES_WITH_IMAGE_ORIGINALS has to be filled and point to an existing file/directory.")
            import sys
            sys.exit(11)

if len(IMAGE_CACHE_DIRECTORY) > 0 and not os.path.isdir(IMAGE_CACHE_DIRECTORY):
    print('Warning: IMAGE_CACHE_DIRECTORY is set but points to a directory which does not exist. Either empty the string or create its cache directory at "' + IMAGE_CACHE_DIRECTORY + '".')

## END OF FILE #################################################################
# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
