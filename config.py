# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2016-11-18 19:46:58 vk>


## ===================================================================== ##
##                                                                       ##
##  These are lazyblorg-global configuration settings.                   ##
##                                                                       ##
##  You might not want to modify anything if you do not know, what       ##
##  you are doing :-)                                                    ##
##                                                                       ##
## ===================================================================== ##


## INTEGRATION: modify variables in this file according to your requirements


# strings: Your personal name and the name of your blog:
AUTHOR_NAME = u'Karl Voit'
BLOG_NAME = u'public voit'

## strings: Define your URLs and your name below:
DOMAIN = u'Karl-Voit.at'
BASE_URL = u'//' + DOMAIN
CSS_URL = BASE_URL + '/public_voit.css'
BLOG_LOGO = BASE_URL + '/images/public-voit_logo.svg'
DISQUS_NAME = 'publicvoit'  # gets placed in: '//publicvoit.disqus.com/embed.js'

## string: Email address to send comments to:
COMMENT_EMAIL_ADDRESS = 'publicvoit-comment@Karl-Voit.at'

## integer: Show this many article teasers on entry page
NUMBER_OF_TEASER_ARTICLES = 15

## integer: Show this many article in Atom feeds:
NUMBER_OF_FEED_ARTICLES = 10

## string: This is the Org-mode property :ID: of your blog article which
##         is used for the about page of your blog.
## See example in: testdata/end_to_end_test/orgfiles/about-placeholder.org
ID_OF_ABOUT_PAGE = '2014-03-09-about'

## string: Your Twitter handle/username which is used in the HTML header
##         metadata (without the @ character)
TWITTER_HANDLE = 'n0v0id'

## string: An image which is added to the HTML header metadata and is used
##         by Twitter in Twitter cards to visualize your blog (also used
##         as og:image)
TWITTER_IMAGE = 'http://Karl-Voit.at/images/public-voit_T_logo_200x200.png'

## string: Replace "+01:00" below with your time-zone indicator
## This gets added to the time in order to describe time zone of the blog:
TIME_ZONE_ADDON = u'+01:00'




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

assert(type(BASE_URL) == unicode)
assert(BASE_URL.startswith(u'//'))
assert(type(AUTHOR_NAME) == unicode)

assert(type(NUMBER_OF_TEASER_ARTICLES) == int)
assert(NUMBER_OF_TEASER_ARTICLES > -1)

assert(type(NUMBER_OF_FEED_ARTICLES) == int)
assert(NUMBER_OF_FEED_ARTICLES > -1)

assert(TIME_ZONE_ADDON[0] == (u'+' or u'-'))


def assertTag(tag):
    """
    checks formal criteria of an Org-mode tag
    """
    assert(type(tag) == unicode)
    assert(u' ' not in tag)
    assert(u':' not in tag)
    assert(u'-' not in tag)


## string of the state which defines a blog entry to be published; states are not shown in result page
BLOG_FINISHED_STATE = u'DONE'

assertTag(BLOG_FINISHED_STATE)


## tag that is expected in any blog entry category; tag does not get shown in list of user-tags
TAG_FOR_BLOG_ENTRY = u'blog'

assertTag(TAG_FOR_BLOG_ENTRY)


## if an entry is tagged with this, it's an TAGS entry; tag does not get shown in list of user-tags
TAG_FOR_TAG_ENTRY = u'lb_tags'

assertTag(TAG_FOR_TAG_ENTRY)


## if an entry is tagged with this, it's an PERSISTENT entry; tag does not get shown in list of user-tags
TAG_FOR_PERSISTENT_ENTRY = u'lb_persistent'

assertTag(TAG_FOR_PERSISTENT_ENTRY)


## if an entry is tagged with this, it's an TEMPLATES entry; tag does not get shown in list of user-tags
TAG_FOR_TEMPLATES_ENTRY = u'lb_templates'

assertTag(TAG_FOR_TEMPLATES_ENTRY)


## if an entry is tagged with this, it will be omitted in feeds, the main page, and navigation pages; tag is shown in result page
TAG_FOR_HIDDEN = u'hidden'

assertTag(TAG_FOR_HIDDEN)


## INTERNAL category names of blog entries:
TAGS = 'TAGS'
PERSISTENT = 'PERSISTENT'
TEMPORAL = 'TEMPORAL'
TEMPLATES = 'TEMPLATES'
ENTRYPAGE = 'ENTRYPAGE'

assert(type(TAGS) == str)
assert(type(PERSISTENT) == str)
assert(type(TEMPORAL) == str)
assert(type(TEMPLATES) == str)
assert(type(ENTRYPAGE) == str)


## base directory of the RSS/ATOM feeds:
FEEDDIR = u'feeds'

assert(type(FEEDDIR) == unicode)


## format of the internal storage file
## pickle offers, e.g., 0 (ASCII; human-readable) or pickle.HIGHEST_PROTOCOL (binary; more efficient)
## see https://docs.python.org/2/library/pickle.html#data-stream-format
#PICKLE_FORMAT = pickle.HIGHEST_PROTOCOL
PICKLE_FORMAT = 0

assert(type(PICKLE_FORMAT) == int)
assert(PICKLE_FORMAT in [0, 1, 2])


## END OF FILE #################################################################
# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
