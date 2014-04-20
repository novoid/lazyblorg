# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2014-04-20 21:30:25 vk>


## ===================================================================== ##
##                                                                       ##
##  These are lazyblorg-global configuration settings.                   ##
##                                                                       ##
##  You might not want to modify anything if you do not know, what       ##
##  you are doing :-)                                                    ##
##                                                                       ##
## ===================================================================== ##

## this tag (withing tag list of article) determines if an article
## is a persistent blog page (tag is found) or a time-oriented
## (normal) blog-entry (this tag is missing).
TAG_FOR_TAG_ENTRY = u'lb_tags'  ## if an entry is tagged with this, it's an TAGS entry
TAG_FOR_PERSISTENT_ENTRY = u'lb_persistent'  ## if an entry is tagged with this, it's an PERSISTENT entry
TAG_FOR_TEMPLATES_ENTRY = u'lb_templates'  ## if an entry is tagged with this, it's an TEMPLATES entry
TAG_FOR_HIDDEN = u'hidden'  ## if an entry is tagged with this, it will be omitted in feeds, the main page, and navigation pages

## categories of blog entries:
TAGS = 'TAGS'
PERSISTENT = 'PERSISTENT'
TEMPORAL = 'TEMPORAL'
TEMPLATES = 'TEMPLATES'
ENTRYPAGE = 'ENTRYPAGE'

## INTEGRATION: replace "+01:00" below with your time-zone indicator
## this gets added to the time in order to describe time zone of the blog:
TIME_ZONE_ADDON = '+01:00'

## show this many article teasers on entry page
NUMBER_OF_TEASER_ARTICLES = 999

## base directory of the RSS/ATOM feeds:
FEEDDIR = 'feeds'

## INTEGRATION: put your URL and your name below:
## (not only?) for feed meta-data: FIXXME: move to CLI parameters?
BASE_URL = 'http://Karl-Voit.at'
AUTHOR_NAME = "Karl Voit"

## show this many article in feeds:
NUMBER_OF_FEED_ARTICLES = 10




## END OF FILE #################################################################
# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
