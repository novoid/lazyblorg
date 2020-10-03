# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2020-10-03 19:25:09 vk>

import config  # lazyblorg-global settings
import sys
import logging
import os
from datetime import datetime
from time import time, localtime, strftime
from math import ceil  # for calculating reading time
import re  # RegEx: for parsing/sanitizing
import codecs
from lib.utils import Utils  # for guess_language_from_stopword_percentages()
from shutil import copyfile  # for copying image files
import cv2  # for scaling image files to their width of choice

try:
    from werkzeug.utils import secure_filename  # for sanitizing path components
except ImportError:
    print("Could not find Python module \"werkzeug\".\nPlease install it, e.g., with \"sudo pip install werkzeug\".")
    sys.exit(1)

try:
    import pypandoc
except ImportError:
    print("Could not find Python module \"pypandoc\".\nPlease install it, e.g., with \"sudo pip install pypandoc\".")
    sys.exit(1)

# reload(sys)
# sys.setdefaultencoding("utf-8")  # for handling UTF-8 characters in filenames like: [x for x in self.filename_dict.keys() if x.startswith(timestamp)]

# NOTE: pdb hides private variables as well. Please use:
# data = self._OrgParser__entry_data ; data['content']


class HtmlizerException(Exception):
    """
    Exception for all kind of self-raised htmlizing errors
    """

    def __init__(self, entry_id, value):
        if entry_id:
            self.value = 'Entry ' + entry_id + ' - ' + value
        else:
            self.value = value

    def __str__(self):
        return repr(self.value)


class Htmlizer(object):
    """
    Class for generating HTML output of lazyblorg
    """

    logging = None  # instance of logger

    current_entry_id = None  # holds the current article entry ID when looping within _generate_pages_for_tags_persistent_temporal()

    # list of lists ['description', 'content'] with content being the HTML
    # templates
    template_definitions = None
    targetdir = None  # string of the base directory of the blog
    blog_data = None  # internal representation of the complete blog content
    metadata = None  # metadata as described in the documentation
    generate = None  # list of IDs which blog entries should be generated
    increment_version = None  # list of IDs which blog entries gets an update
    blog_tag = None  # string that marks blog entries (as Org-mode tag)
    autotag_language = False  # boolean, if guessing language + autotag should be done
    ignore_missing_ids = False  # boolean; do not throw respective exception when true
    filename_dict = {}  # dict of basenames of filenames, see config.MEMACS_FILE_WITH_IMAGE_FILE_INDEX and config.DIRECTORIES_WITH_IMAGE_ORIGINALS
    stats_images_resized = 0  # holds the current number of resized image files
    stats_external_org_to_html5_conversion = 0  # holds the number of invocations of external conversion tool (pypandoc so far)
    stats_external_latex_to_html5_conversion = 0  # holds the number of invocations of external conversion tool (pypandoc so far)

    # { 'mytag': [ 'ID1', 'ID2', 'ID2'], 'anothertag': [...] }
    dict_of_tags_with_ids = None

    # holds a list of tags whose tag pages have been generated
    list_of_tag_pages_generated = []

    # find internal links to Org-mode IDs: [[id:simple]] and [[id:with][a
    # description]]
    ID_SIMPLE_LINK_REGEX = re.compile(r'(\[\[id:([^\[]+?)\]\])')
    ID_DESCRIBED_LINK_REGEX = re.compile(r'(\[\[id:([^\]]+?)\]\[([^\]]+?)\]\])')

    # find external links such as [[http(s)://foo.com][bar]]:
    EXT_URL_WITH_DESCRIPTION_REGEX = re.compile(
        r'\[\[(http[^ ]+?)\]\[(.+?)\]\]', flags=re.U)

    # find external links such as [[foo]]:
    EXT_URL_WITHOUT_DESCRIPTION_REGEX = re.compile(
        r'\[\[(.+?)\]\]', flags=re.U)

    # find external links such as http(s)://foo.bar
    EXT_URL_LINK_REGEX = re.compile(
        r'([^"<>\[])(http(s)?:\/\/\S+)', flags=re.U)

    # find '&amp;' in an active URL and fix it to '&':
    FIX_AMPERSAND_URL_REGEX = re.compile(
        r'(href="http(s)?://\S+?)&amp;(\S+?")', flags=re.U)

    # find *bold text*:
    # test with: re.subn(re.compile(u'(\W|\A)\*([^*]+)\*(\W|\Z)', flags=re.U), ur'\1<b>\2</b>\3', '*This* is a *touch* of *bold*.')[0]
    BOLD_REGEX = re.compile(r'(\W|\A)\*([^*]+?)\*(\W|\Z)', flags=re.U)

    # find ~code or source text~ (teletype):
    CODE_REGEX = re.compile(r'(\W|\A)~([^~]+?)~(\W|\Z)', flags=re.U)

    # find =verbatim text= (teletype):
    VERBATIM_REGEX = re.compile(r'(\W|\A)=([^=]+?)=(\W|\Z)', flags=re.U)

    # find +strike through+ text:
    STRIKE_THROUGH_REGEX = re.compile(r'(\W|\A)\+([^~]+?)\+(\W|\Z)', flags=re.U)

    # any ISO date-stamp of format YYYY-MM-DD:
    DATESTAMP = r'([12]\d\d\d)-([012345]\d)-([012345]\d)'
    DATESTAMP_REGEX = re.compile(DATESTAMP, flags=re.U)

    # adapted ISO time-stamp of format YYYY-MM-DDThh.mm.ss: http://karl-voit.at/managing-digital-photographs/
    TIMESTAMP_REGEX = re.compile(DATESTAMP + r'T(([01]\d)|(20|21|22|23)).([012345]\d).([012345]\d)', flags=re.U)

    ID_PREFIX_FOR_EMPTY_TAG_PAGES = 'lb_tag-'

    LINKS_ONLY_FEED_POSTFIX = ".atom_1.0.links-only.xml"
    LINKS_AND_TEASER_FEED_POSTFIX = ".atom_1.0.links-and-teaser.xml"
    LINKS_AND_CONTENT_FEED_POSTFIX = ".atom_1.0.links-and-content.xml"

    defined_languages = [x[0] for x in Utils.STOPWORDS]

    def __init__(
            self,
            template_definitions,
            blog_tag,
            targetdir,
            blog_data,
            metadata,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids):
        """
        This function initializes the class instance with the class variables.

        @param template_definitions: list of lists ['description', 'content'] with content being the HTML templates
        @param blog_tag: string that marks blog entries (as Org-mode tag)
        @param targetdir: string of the base directory of the blog
        @param blog_data: internal representation of the complete blog content
        @param metadata: as described in the documentation
        @param entries_timeline_by_published: dict(year) of list(month) of list(day) of lists(entries) of IDs
        @param generate: list of IDs which blog entries should be generated
        @param increment_version: list of IDs which blog entries gets an update
        @param autotag_language: true, if guessing of language + its auto-tag should be done
        """

        # initialize class variables
        self.template_definitions = template_definitions
        self.blog_tag = blog_tag
        self.targetdir = targetdir
        self.blog_data = blog_data
        self.metadata = metadata
        self.generate = generate
        self.increment_version = increment_version
        self.autotag_language = autotag_language
        self.entries_timeline_by_published = entries_timeline_by_published
        self.ignore_missing_ids = ignore_missing_ids

        # create logger (see
        # http://docs.python.org/2/howto/logging-cookbook.html)
        self.logging = logging.getLogger('lazyblorg.htmlizer')

        # self.logging.debug("Htmlizer initiated with %s templ.def., %s blog_data, %s generate, %s increment" %
        #                    (str(len(template_definitions)), str(len(blog_data)), str(len(generate)),
        #                     str(len(increment_version))))

    def run(self):
        """
        Basic method that creates all the output.

        @param: return: list of: stats_generated_total: total articles generated
                                 stats_generated_temporal: temporal articles generated
                                 stats_generated_persistent: persistent articles generated
                                 stats_generated_tags: tag articles generated
        """

        self.blog_data = self._populate_backreferences(self.blog_data)

        self.dict_of_tags_with_ids = self._populate_dict_of_tags_with_ids(
            self.blog_data)

        dummy_age = 0  # FIXXME: replace with age in days since last usage
        list_of_relevant_tags = list(self.dict_of_tags_with_ids.keys())
        for languagetag in self.defined_languages:  # may be more
            # elegant to use sets? remove language tags that override
            # language auto-tags: they should not be listed somewhere
            # except in auto-tags
            if languagetag in list_of_relevant_tags:
                list_of_relevant_tags.remove(languagetag)
        # tags = list of lists with [tagname, count of tag usage, age in days of last usage]:
        tags = [[tag, len(self.dict_of_tags_with_ids[tag]), dummy_age] for tag in list_of_relevant_tags]

        self.logging.info('• Generating articles …')

        entry_list_by_newest_timestamp, stats_generated_total, stats_generated_temporal, \
            stats_generated_persistent, stats_generated_tags = self._generate_pages_for_tags_persistent_temporal(tags)

        self._generate_tag_overview_page(tags)

        self._generate_feeds(entry_list_by_newest_timestamp)

        return [stats_generated_total,
                stats_generated_temporal,
                stats_generated_persistent,
                stats_generated_tags,
                self.stats_images_resized,
                self.stats_external_org_to_html5_conversion,
                self.stats_external_latex_to_html5_conversion]

    def _populate_backreferences(self, blog_data):
        """
        Traverses all blog articles and collects internal links as references to their corresponding link target.
        In other words, when article X contains a link to article Y then blog_data of Y gets a back-link to X.

        This is a dirty quick hack. It would be better when this search is done (1) in the parser or
        (2) within the sanitizing functions.

        I did not implement it in the parser because the current parser is output format agnostic
        and does not parse for internal links.

        I could not implement it in the sanitizing method because the current workflow is that the
        sanitizing is done shortly before the HTML files are written. This is too late because this
        way we can not add back-references to articles whose files have already written.

        Therefore I did this dirty hack of looking to the str-representation of the whole content
        which might lead to found links which are for example phantasy links within example blocks
        that are not really linked in the output document. We check for those cases later on
        in _generate_back_references_content(). Did I already mention that this is a hack? ;-)

        FIXXME: resolve hack with a better method to look for back-references.

        @param: blog_data: the usual blog data data structure
        @param: return: the modified blog data structure
        """

        for blog_article in blog_data:
            link_targets = set()
            backreference_target = blog_article['id']

            for content_item in blog_article['content']:

                # NOTE: this is the poor man's method of locating ID
                # links. It would be better to look for internal
                # references within the corresponding sanitizing
                # method. Unfortuantely, those sanitizing methods are
                # applied shortly before writing the result file to
                # disk. Therefore, I can not do this for now because I
                # need to locate all references before any file gets
                # written to disk.
                if content_item[0] not in ('colon-block', 'example-block'):
                    simple_links = re.findall(self.ID_SIMPLE_LINK_REGEX, str(content_item))
                    described_links = re.findall(self.ID_DESCRIBED_LINK_REGEX, str(content_item))

                    if simple_links:
                        for link in simple_links:
                            # Omit links to itself:
                            if link != backreference_target:
                                link_targets.add(link[1])
                    if described_links:
                        for link in described_links:
                            # Omit links to itself:
                            if link != backreference_target:
                                link_targets.add(link[1])

            # If any internal links were found, append a back-link to
            # the current ID to their blog_data list item:
            # FIXXME:
            # horrible inefficient because of iterating over all items
            # for each link found.
            if len(link_targets) > 0:
                for current_link_id in link_targets:
                    for blog_data_entry in blog_data:
                        if blog_data_entry['id'] == current_link_id:
                            if 'back-references' in list(blog_data_entry.keys()):
                                blog_data_entry['back-references'].add(backreference_target)
                            else:
                                # the first back-reference of this blog_data_entry
                                blog_data_entry['back-references'] = set([backreference_target])

        return blog_data

    def _populate_dict_of_tags_with_ids(self, blog_data):
        """
        Traverses all blog articles and collects them by tags. Resulting data looks
        like { 'mytag': [ 'ID1', 'ID2', 'ID2'], 'anothertag': [...] }

        @param: blog_data: the usual blog data data structure
        @param: return: dict of lists of IDs
        """

        dict_of_tags_with_ids = {}

        for blog_article in blog_data:
            if config.TAG_FOR_HIDDEN not in blog_article['usertags']:
                for usertag in blog_article['usertags']:
                    # append usertags to dict:
                    if usertag in list(dict_of_tags_with_ids.keys()):
                        dict_of_tags_with_ids[usertag].append(
                            blog_article['id'])
                    else:
                        dict_of_tags_with_ids[usertag] = [blog_article['id']]

                    # FIXXME: append autotags to dict

        return dict_of_tags_with_ids

    def _derive_reading_length(self, rawcontent: str) -> int:
        """
        Determines the number of minutes reading time from the rawcontent of the article.

        Assumption: people are able to read 250 words per minute.

        See https://github.com/novoid/lazyblorg/issues/47 for the idea and implementation notes.
        """

        # remove heading title and drawer in order to get body of content:
        rawcontent_without_header: str = re.sub(r':PROPERTIES:.+?:END:\n', '', rawcontent, flags=re.DOTALL)

        # remove all "words" (according to split()) which contains numbers or other characters that are indicators of non-word elements:
        raw_words: list = [x for x in rawcontent_without_header.split() if not re.match(r'.*[|0123456789].*', x)]
        raw_words = [x for x in raw_words if not x.startswith(('#+', '-', ':'))]

        minutes: int = ceil(len(raw_words) / 250)

        if minutes == 0:
            minutes = 1  # even empty articles should take one minute to watch at
        return minutes

    def _generate_pages_for_tags_persistent_temporal(self, tags):
        """
        Method that creates the pages for tag-pages, persistent pages, and temporal pages.

        @param: tags: dict of the form TAGS = [['python', 28059, 3], [tagname, count, age_in_days]]
        @param: return: stats_generated_total: total articles generated
        @param: return: stats_generated_temporal: temporal articles generated
        @param: return: stats_generated_persistent: persistent articles generated
        @param: return: stats_generated_tags: tag articles generated
        """

        stats_generated_total, \
            stats_generated_temporal, \
            stats_generated_persistent, \
            stats_generated_tags = 0, 0, 0, 0

        for entry in self.blog_data:

            # example entry:
            # {'level': 2,
            # 'latestupdateTS': datetime(2013, 2, 14, 19, 2),
            # 'usertags': [u'mytest', u'programming'],
            # 'autotags': [u'german', u'short'],
            # 'lbtags': [u'blog'],
            # 'created': datetime(2013, 2, 12, 10, 58),
            # 'finished-timestamp-history': [datetime(2013, 2, 14, 19, 2)],
            # 'title': u'This is an example blog entry',
            # 'id': u'2013-02-12-lazyblorg-example-entry',
            # 'content': [['par', u'foo...'], [...]]
            #  }

            self.current_entry_id = entry['id']

            entry = self.sanitize_and_htmlize_blog_content(entry)

            # populate reading time indicator:
            if 'rawcontent' in entry.keys():
                entry['reading_minutes'] = self._derive_reading_length(entry['rawcontent'])

            htmlcontent = None

            if entry['category'] == config.TAGS:
                self.logging.debug(self.current_entry_id_str() + "entry is a tag page")
                htmlfilename, orgfilename, htmlcontent = self._generate_tag_page(
                    entry)
                stats_generated_tags += 1

            elif entry['category'] == config.PERSISTENT:
                self.logging.debug(self.current_entry_id_str() + "entry is a persistent page")
                htmlfilename, orgfilename, htmlcontent = self._generate_persistent_article(
                    entry)
                stats_generated_persistent += 1

            elif entry['category'] == config.TEMPORAL:
                self.logging.debug(self.current_entry_id_str() + "entry is an ordinary time-oriented blog entry")
                htmlfilename, orgfilename, htmlcontent = self._generate_temporal_article(
                    entry)
                stats_generated_temporal += 1

            elif entry['category'] == config.TEMPLATES:
                self.logging.debug(self.current_entry_id_str() + "entry is the/a HTML template definition. Ignoring.")

            else:
                message = self.current_entry_id_str() + "entry has an unknown category [" + \
                    repr(entry['category']) + "]. Please check and fix before next run."
                self.logging.critical(message)
                raise HtmlizerException(self.current_entry_id, message)

            if entry['category'] == config.TAGS or entry[
                    'category'] == config.PERSISTENT or entry['category'] == config.TEMPORAL:
                self.write_content_to_file(htmlfilename, htmlcontent)
                self.write_orgcontent_to_file(orgfilename, entry['rawcontent'])
                stats_generated_total += 1

        # generate (empty) tag pages for all tags which got no user-defined tag page content:
        stats_generated_empty_tags = self._generate_tag_pages_which_got_no_userdefined_tag_page()
        stats_generated_total += stats_generated_empty_tags
        stats_generated_tags += stats_generated_empty_tags

        entry_list_by_newest_timestamp = self.generate_entry_list_by_newest_timestamp()
        self.generate_entry_page(entry_list_by_newest_timestamp, tags)
        stats_generated_total += 1

        return entry_list_by_newest_timestamp, stats_generated_total, stats_generated_temporal, \
            stats_generated_persistent, stats_generated_tags

    def _generate_auto_tag_list_items(self, entry):
        """
        Creates the HTML snippet for a HTML list containing the auto tags and their links.

        @param entry: blog entry data
        @param return: htmlcontent: the HTML content of the entry like '                <li><a class="autotag" href="../../2016/11/16/empty-language-autotag-page">language:english</a></li>\n'
        """

        htmlcontent = ''
        if 'autotags' in list(entry.keys()):
            for autotagkey in sorted(list(entry['autotags'].keys())):
                if autotagkey == 'language':
                    htmlsnippet = self.template_definition_by_name('article-autotag-language').replace('#AUTOTAGLANGUAGELINK',
                                                                                                       '[[id:empty-language-autotag-page][language:' +
                                                                                                       entry['autotags'][autotagkey] + ']]')
                    # resolving id:empty-language-autotag-page to its HTML link:
                    htmlsnippet = self.sanitize_internal_links(htmlsnippet,
                                                               keep_orgmode_format=False)
                    # dirty hack to insert CSS class to link:
                    htmlsnippet = htmlsnippet.replace('a href', 'a class="autotag" href')
                else:
                    # generic auto-tag: this section is a
                    # never-reached place-holder until more auto-tags
                    # than just language are implemented
                    htmlsnippet = self._replace_tag_placeholders([autotagkey + ":" + entry['autotags'][autotagkey]],
                                                                 self.template_definition_by_name('article-autotag-generic'))

                htmlcontent += htmlsnippet

        return htmlcontent

    def _generate_feeds(self, entry_list_by_newest_timestamp):
        """
        Method that creates the feed files.
        """

        feed_folder = os.path.join(self.targetdir, config.FEEDDIR)
        if not os.path.isdir(feed_folder):
            try:
                self.logging.debug(
                    "creating path for feeds: \"%s\"" %
                    feed_folder)
                os.makedirs(feed_folder)
            except OSError:
                # thrown, if it exists (no problem) or can not be created ->
                # check!
                if os.path.isdir(feed_folder):
                    self.logging.debug(
                        "feed path [%s] already existed" %
                        feed_folder)
                else:
                    message = "feed path [" + feed_folder + \
                        "] could not be created. Please check and fix before next run."
                    self.logging.critical(message)
                    raise HtmlizerException(self.current_entry_id, message)

        self.__generate_feeds_for_everything(entry_list_by_newest_timestamp)

    def __generate_feed_file_path(self, feedstring):
        """
        Generator function for RSS/ATOM feed files.

        @param feedstring: part of the feed file which describes the feed itself
        @param return: ATOM feed file path and names
        """

        filenames = self.__generate_feed_file_names(feedstring)

        return \
            os.path.join(self.targetdir, config.FEEDDIR, filenames[0]), \
            os.path.join(self.targetdir, config.FEEDDIR, filenames[1]), \
            os.path.join(self.targetdir, config.FEEDDIR, filenames[2])

    def __generate_feed_file_names(self, feedstring):
        """
        Generator function for RSS/ATOM feed files.

        @param feedstring: part of the feed file which describes the feed itself
        @param return: ATOM feed file names
        """

        return \
            os.path.join("lazyblorg-" + feedstring + self.LINKS_ONLY_FEED_POSTFIX), \
            os.path.join("lazyblorg-" + feedstring + self.LINKS_AND_TEASER_FEED_POSTFIX), \
            os.path.join("lazyblorg-" + feedstring + self.LINKS_AND_CONTENT_FEED_POSTFIX)

    def __generate_new_feed(self):
        """
        Generator function for a new RSS/ATOM feed.

        @param return: a string containing all feed-related meta-data
        """

        feed = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:thr="http://purl.org/syndication/thread/1.0"
      xml:lang="en-us">
  <link rel="self" href=\"""" + config.BASE_URL + """/feeds/lazyblorg-all#LINKPOSTFIX#\" />
  <title type="text">""" + config.BLOG_NAME + """</title>
  <id>""" + config.BASE_URL + """/</id>
  <link href=\"""" + config.BASE_URL + """\" />
  <icon>/favicon.ico</icon>
  <updated>""" + strftime('%Y-%m-%dT%H:%M:%S' + config.TIME_ZONE_ADDON, localtime()) + """</updated>
  <author>
    <name>""" + config.AUTHOR_NAME + """</name>
  </author>
  <subtitle type="text">""" + config.BLOG_NAME + """</subtitle>
  <rights>All content written by """ + config.AUTHOR_NAME + """</rights>
  <generator uri='https://github.com/novoid/lazyblorg'>Generated from Org-mode source code using lazyblorg which is written in Python. Industrial-strength technology, baby.</generator>"""

        return feed.replace('>' + config.BASE_URL, '>http:' + config.BASE_URL).replace('\'' + config.BASE_URL, '\'http:' + config.BASE_URL).replace('\"' + config.BASE_URL, '\"http:' + config.BASE_URL)

    def __generate_feeds_for_everything(self, entry_list_by_newest_timestamp):
        """
        Generator function for the global RSS/ATOM feed.

        @param return: none
        """

        atom_targetfile_links, atom_targetfile_teaser, atom_targetfile_content = self.__generate_feed_file_path("all")
        links_atom_feed = self.__generate_new_feed().replace('#LINKPOSTFIX#', self.LINKS_ONLY_FEED_POSTFIX)
        teaser_atom_feed = self.__generate_new_feed().replace('#LINKPOSTFIX#', self.LINKS_AND_TEASER_FEED_POSTFIX)
        content_atom_feed = self.__generate_new_feed().replace('#LINKPOSTFIX#', self.LINKS_AND_CONTENT_FEED_POSTFIX)

        number_of_current_feed_entries = 0
        listentry = None
        listentry_index = 0

        while number_of_current_feed_entries < config.NUMBER_OF_FEED_ARTICLES and \
                len(entry_list_by_newest_timestamp) > listentry_index:

            # get next element from entry_list
            listentry = entry_list_by_newest_timestamp[listentry_index]
            listentry_index += 1

            # ignore pseudo/empty tag pages without user content:
            while listentry['id'].startswith(self.ID_PREFIX_FOR_EMPTY_TAG_PAGES):
                listentry = entry_list_by_newest_timestamp[listentry_index]
                listentry_index += 1

            if listentry['category'] == config.TEMPLATES:
                continue

            # listentry: (examples)
            # {'url': 'about', 'latestupdateTS': datetime(2014, 3, 9, 14, 57), 'category': 'PERSISTENT',
            #  'id': u'2014-03-09-about'}
            # {'url': '2013/08/22/testid', 'latestupdateTS': datetime(2013, 8, 22, 21, 6),
            #  'category': 'TEMPORAL', 'id': u'2013-08-22-testid'}

            blog_data_entry = self.blog_data_with_id(listentry['id'])
            # blog_data_entry.keys() = ['category', 'level', 'latestupdateTS', 'usertags', 'autotags', 'lbtags', 'created', 'content',
            #                           'htmlteaser-equals-content', 'rawcontent', 'finished-timestamp-history', 'title', 'id']

            # omit hidden entries:
            if config.TAG_FOR_HIDDEN in blog_data_entry['usertags']:
                continue

            # filling feed entry string:
            feedentry = """\n<!-- ############################################################################################# -->\n<entry>
    <title type="text">""" + self.sanitize_feed_html_characters(blog_data_entry['title']) + """</title>
    <link href='""" + config.BASE_URL + "/" + listentry['url'] + """' />
    <published>""" + blog_data_entry['firstpublishTS'].strftime('%Y-%m-%dT%H:%M:%S' + config.TIME_ZONE_ADDON) + """</published>
    <updated>""" + blog_data_entry['latestupdateTS'].strftime('%Y-%m-%dT%H:%M:%S' + config.TIME_ZONE_ADDON) + "</updated>"

            # adding all tags:
            for tag in blog_data_entry['usertags']:

                feedentry += "\n    <category scheme='" + config.BASE_URL + \
                    "/" + "tags" + "/" + tag + "' term='" + tag + "' />"
            # handle autotags:
            if 'autotags' in list(blog_data_entry.keys()):
                for autotag in list(blog_data_entry['autotags'].keys()):
                    tag = autotag + ":" + blog_data_entry['autotags'][autotag]
                    feedentry += "\n    <category scheme='" + config.BASE_URL + "/" + \
                        "autotags" + "/" + autotag + "' term='" + tag + "' />"

            # write feedentry to links_atom_feed before any summary is added:
            links_atom_feed += feedentry + "\n    <id>" + config.BASE_URL + "/" + \
                listentry['url'] + "-from-feed-with-links" + "</id>\n</entry>"

            # add article summary to feedentry:
            feedentry += "\n    <summary type='xhtml'>\n<div xmlns='http://www.w3.org/1999/xhtml'>"

            # what part of the data is to show on the entry page?
            teaser_html_content = False
            if blog_data_entry['htmlteaser-equals-content']:
                teaser_html_content = blog_data_entry['content']
            else:
                teaser_html_content = blog_data_entry['htmlteaser']

            # adding article paths to embedded images:
            teaser_html_content = self._add_absolute_path_to_image_src(teaser_html_content, listentry['url'])

            feedentry += self.sanitize_feed_html_characters('\n'.join(teaser_html_content))
            feedentry += "</div>\n    </summary>"

            # add content to content-feed OR end entry for links-feed:
            teaser_atom_feed += feedentry + "\n    <id>" + config.BASE_URL + "/" + \
                listentry['url'] + "-from-feed-with-teaser" + "</id>\n</entry>"
            content_atom_feed += feedentry + """    <content type='xhtml'>
      <div xmlns='http://www.w3.org/1999/xhtml'>
	""" + self.sanitize_feed_html_characters('\n'.join(blog_data_entry['content'])) + """
      </div>
    </content>
    <id>""" + config.BASE_URL + "/" + listentry['url'] + "-from-feed-with-content" + \
                "</id>\n</entry>"

            # replace "\\example.com" with "http:\\example.com" to calm down feed verifiers/aggregators:
            links_atom_feed = links_atom_feed.replace('>' + config.BASE_URL, '>http:' + config.BASE_URL)
            links_atom_feed = links_atom_feed.replace('\'' + config.BASE_URL, '\'http:' + config.BASE_URL)
            teaser_atom_feed = teaser_atom_feed.replace('>' + config.BASE_URL, '>http:' + config.BASE_URL)
            teaser_atom_feed = teaser_atom_feed.replace('\'' + config.BASE_URL, '\'http:' + config.BASE_URL)
            content_atom_feed = content_atom_feed.replace('>' + config.BASE_URL, '>http:' + config.BASE_URL)
            content_atom_feed = content_atom_feed.replace('\'' + config.BASE_URL, '\'http:' + config.BASE_URL)

            number_of_current_feed_entries += 1

        links_atom_feed += "</feed>"
        teaser_atom_feed += "</feed>"
        content_atom_feed += "</feed>"

        assert(isinstance(links_atom_feed, str))
        assert(isinstance(teaser_atom_feed, str))
        assert(isinstance(content_atom_feed, str))

        # Save the feed to a file in various formats
        self.write_content_to_file(atom_targetfile_links, links_atom_feed)
        self.write_content_to_file(atom_targetfile_teaser, teaser_atom_feed)
        self.write_content_to_file(atom_targetfile_content, content_atom_feed)

        return

    def generate_entry_list_by_newest_timestamp(self):
        """

        Returns a sorted list of dicts of entry-IDs and their newest time-stamp.
        Sort order ist newest time-stamp at the front.

        @param: return: a sorted list like [ {'id':'a-new-entry', 'latestupdateTS':datetime(), 'url'="<URL>"}, {...}]
        """

        entrylist = []

        for entry in self.blog_data:
            entry_to_add = {
                'id': entry['id'],
                'latestupdateTS': entry['latestupdateTS'],
                'firstpublishTS': entry['firstpublishTS'],
                'url': self._target_path_for_id_without_targetdir(entry['id']),
                'category': entry['category']
            }
            if entry_to_add not in entrylist:
                entrylist.append(entry_to_add)
            else:
                # FIXXME: find out how those entries got into blog_data multiple times in the first place:
                # I guess this has something to do with using self.ID_PREFIX_FOR_EMPTY_TAG_PAGES
                pass
                # logging.warning('Trying to add an entry twice: ' + str(entry_to_add))

        return sorted(
            entrylist,
            key=lambda entry: entry['latestupdateTS'],
            reverse=True)

    def generate_entry_page(self, entry_list_by_newest_timestamp, tags):
        """
        Generates and writes the blog entry page with sneak previews of the most recent articles/updates.

        @param: tags: dict of the form TAGS = [['python', 28059, 3], [tagname, count, age_in_days]]
        @param: entry_list_by_newest_timestamp: a sorted list like [ {'id':'a-new-entry', 'latestupdateTS':datetime(), 'url'="<URL>"}, {...}]
        """

        entry_page_filename = os.path.join(self.targetdir, "index.html")

        htmlcontent = '' + \
            self.template_definition_by_name('entrypage-header')

        listentry = None
        listentry_index = 0
        number_of_teasers_generated = 0

        while number_of_teasers_generated < config.NUMBER_OF_TEASER_ARTICLES and \
                listentry_index < len(entry_list_by_newest_timestamp):

            # get next element from entry_list
            listentry = entry_list_by_newest_timestamp[listentry_index]
            listentry_index += 1

            # ignore pseudo/empty tag pages without user content:
            if listentry['id'].startswith(self.ID_PREFIX_FOR_EMPTY_TAG_PAGES):
                continue

            entry = self.blog_data_with_id(listentry['id'])

            # omit hidden entries:
            if config.TAG_FOR_HIDDEN in entry['usertags']:
                continue
                # FIXXME: for each hidden entry within
                # config.NUMBER_OF_TEASER_ARTICLES, there will be one
                # entry missing. Fix this by switching to "until
                # enough articles on main page or no articles left:
                # find next article"

            if entry['category'] == 'TEMPORAL' or entry[
                    'category'] == 'PERSISTENT':

                content = ""

                for articlepart in [
                    'article-preview-header',
                        'article-preview-tags-begin']:
                    content += self.template_definition_by_name(articlepart)

                # tags of article
                content += self._replace_tag_placeholders(
                    entry['usertags'], self.template_definition_by_name('article-preview-usertag'))

                # handle autotags
                content += self._generate_auto_tag_list_items(entry)

                for articlepart in [
                    'article-preview-tags-end',
                        'article-preview-begin']:
                    content += self.template_definition_by_name(articlepart)

                assert('htmlteaser-equals-content' in list(entry.keys()))

                if not entry['htmlteaser-equals-content']:
                    # there is more in the article than in the teaser alone:
                    content += self.template_definition_by_name(
                        'article-preview-more')

                content += self.template_definition_by_name(
                    'article-preview-end')

                # replacing keywords:

                content = self.sanitize_internal_links(content)
                content = content.replace(
                    '#ARTICLE-TITLE#',
                    self.sanitize_external_links(
                        self.sanitize_html_characters(
                            entry['title'])))
                content = content.replace('#ARTICLE-URL#', listentry['url'])
                content = content.replace('#ARTICLE-ID#', entry['id'])

                year, month, day, hours, minutes = str(
                    listentry['latestupdateTS'].year).zfill(2), str(
                    listentry['latestupdateTS'].month).zfill(2), str(
                    listentry['latestupdateTS'].day).zfill(2), str(
                    listentry['latestupdateTS'].hour).zfill(2), str(
                    listentry['latestupdateTS'].minute).zfill(2)
                iso_timestamp = '-'.join([year, month, day]) + \
                    'T' + hours + ':' + minutes

                content = content.replace('#ARTICLE-YEAR#', year)
                content = content.replace('#ARTICLE-MONTH#', month)
                content = content.replace('#ARTICLE-DAY#', day)
                content = content.replace(
                    '#ARTICLE-PUBLISHED-HTML-DATETIME#',
                    iso_timestamp + config.TIME_ZONE_ADDON)
                content = content.replace(
                    '#ARTICLE-PUBLISHED-HUMAN-READABLE#', iso_timestamp)

                # what part of the data is to show on the feed?
                teaser_html_content = False
                if entry['htmlteaser-equals-content']:
                    teaser_html_content = entry['content']
                else:
                    teaser_html_content = entry['htmlteaser']

                # adding article paths to embedded images:
                teaser_html_content = self._add_absolute_path_to_image_src(teaser_html_content, listentry['url'])

                # join all HTML lines and apply the teaser HTML content template
                content = content.replace(
                    '#ARTICLE-TEASER#',
                    '\n'.join(
                        teaser_html_content))

                htmlcontent += content
                number_of_teasers_generated += 1

            elif entry['category'] == 'TAGS':
                pass  # FIXXME: implement if you want sneak previews of tag pages on entry page

        if number_of_teasers_generated < config.NUMBER_OF_TEASER_ARTICLES:
            logging.debug('number_of_teasers_generated == ' +
                          str(number_of_teasers_generated) +
                          ' and NUMBER_OF_TEASER_ARTICLES == ' +
                          str(config.NUMBER_OF_TEASER_ARTICLES) +
                          ' and therefore I got less teaser than configured in NUMBER_OF_TEASER_ARTICLES')

        # add footer:
        htmlcontent += self.template_definition_by_name('entrypage-footer')

        htmlcontent = htmlcontent.replace(
            '#COMMON-SIDEBAR#',
            self.template_definition_by_name('common-sidebar'))
        htmlcontent = self._replace_general_article_placeholders(
            entry, htmlcontent)

        htmlcontent = htmlcontent.replace(
            '#TAGOVERVIEW-CLOUD#',
            self._generate_tag_cloud(tags))

        htmlcontent = self.sanitize_internal_links(htmlcontent)
        self.write_content_to_file(entry_page_filename, htmlcontent)

        return

    def _add_absolute_path_to_image_src(self, content, url):
        """
        Parses a content data list and stupidly adds absolute paths to all img tags.

        FIXXME: this search&replace depends on the HTML source used and might break :-(
        This is a dirty workaround until I find a better solution:

        @param: content: list of elements that contain HTML sources
        @param: url: string that holds the URL of the article
        @param: return: the modified content
        """
        # adding article paths to embedded images:
        element_index = 0
        for element in content:
            if element.startswith('\n<figure class="'):
                content[element_index] = content[element_index].replace('">\n<img src="',
                                                                        '">\n<img src="http:' +
                                                                        config.BASE_URL + '/' +
                                                                        url + '/')
            element_index += 1
        return content

    def _generate_tag_cloud(self, tags):
        """
        Generates a tag cloud which is linked and assigns multiple CSS attributes according to age and number of usage.

        @param: tags: dict of the form TAGS = [['python', 28059, 3], [tagname, count, age_in_days]]
        @param: return: string with linked tag cloud of form: <a href="cloud/" class="usertag tagcloud-size-0 tagcloud-age-2">cloud</a>
        """

        result = ''

        # removing tags that should be ignored due to user configuration:
        for tagitem in tags:
            if tagitem[0] in config.IGNORE_FOR_TAG_CLOUD:
                tags.remove(tagitem)

        # defines the number of steps of different sizes according to tag usage in numbers:
        COUNT_SIZES = list(range(1, 7))  # requires 0..6 size-X definitions in CSS

        COUNT_MAX = max([x[1] for x in tags])  # Needed to calculate the steps for the font-size
        if len(tags) < len(COUNT_SIZES):
            COUNT_STEP = 1  # edge case when testing with less than ~7 tags: use only first count steps
        else:
            COUNT_STEP = COUNT_MAX / len(COUNT_SIZES)
            if COUNT_STEP < 1:
                COUNT_STEP = 1

        # defines the number and interval of steps of different colors according to last tag usage in days:
        AGE_RANGES = [31, 31 * 3, 31 * 6, 365, 365 * 3]  # requires 0..5 age-X definitions

        for currenttag in sorted(tags):
            if currenttag in config.IGNORE_FOR_TAG_CLOUD:
                continue  # ignore some tags
            tag = currenttag[0]
            count = currenttag[1]
            age = currenttag[2]

            css_size = int(count / COUNT_STEP)

            css_age = 0
            for age_range in AGE_RANGES:
                if age < age_range:
                    break
                css_age += 1

            result += '<li><a href="' + config.BASE_URL + '/tags/' + tag + '/" class="tagcloud-usertag tagcloud-size-' + \
                      str(css_size) + ' tagcloud-age-' + str(css_age) + '">' + tag + '</a></li>\n'

        return result

    def _generate_tag_overview_page(self, tags):
        """
        Generates and writes the overview page for all tags. It contains a simple tag cloud.

        @param: tags: dict of the form TAGS = [['python', 28059, 3], [tagname, count, age_in_days]]
        """

        tag_overview_filename = os.path.join(self.targetdir, 'tags', 'index.html')

        htmlcontent = ''
        for articlepart in [
                'tagoverviewpage-header',
                'tagoverviewpage-body',
                'tagoverviewpage-footer']:
            htmlcontent += self.template_definition_by_name(articlepart)

        htmlcontent = htmlcontent.replace(
            '#COMMON-SIDEBAR#',
            self.template_definition_by_name('common-sidebar'))

        htmlcontent = htmlcontent.replace(
            '#TAGOVERVIEW-CLOUD#',
            self._generate_tag_cloud(tags))

        htmlcontent = self._replace_general_blog_placeholders(htmlcontent)

        htmlcontent = self.sanitize_internal_links(htmlcontent)

        self.write_content_to_file(tag_overview_filename, htmlcontent)

        return

    def write_content_to_file(self, filename, content):
        """
        Creates a file and writes the content into it.

        @param filename: the name of the file to write to including path
        @param htmlcontent: the (UTF-8) string of the HTML content
        @param return: True if success
        """

        if filename and content:
            with codecs.open(filename, 'wb', encoding='utf-8') as output:
                try:
                    output.write(content)
                except:
                    self.logging.critical(self.current_entry_id_str() +
                                          "Error when writing file: " + str(filename))
                    raise
                    return False
            return True
        else:
            self.logging.critical(self.current_entry_id_str() +
                                  "No filename (" +
                                  str(filename) +
                                  ") or content when writing file: " +
                                  str(filename))
            return False

    def write_orgcontent_to_file(self, orgfilename, rawcontent):
        """
        Creates the file and writes the raw Org-mode source into it.

        @param orgfilename: the name of the file to write to including path
        @param rawcontent: the (UTF-8) string of the HTML content
        @param return: True if success
        """

        if orgfilename and rawcontent:
            with codecs.open(orgfilename, 'wb', encoding='utf-8') as output:
                try:
                    output.write(rawcontent)
                except:
                    self.logging.critical(self.current_entry_id_str() +
                                          "Error when writing file: " + str(orgfilename))
                    raise
            return True
        else:
            self.logging.critical(self.current_entry_id_str() +
                                  "No filename (" +
                                  str(orgfilename) +
                                  ") or Org-mode raw content when writing file: " +
                                  str(orgfilename))
            return False

    def convert_org_to_html5(self, orgmode):
        """Converts an arbitrary Org mode syntax element (a string) to its
        corresponding HTML5 representation.

        @param orgmode: Org mode text
        @param return: HTML5 representation of Org mode text
        """

        assert(isinstance(orgmode, str))
        self.stats_external_org_to_html5_conversion += 1
        return pypandoc.convert_text(orgmode, 'html5', format='org')

    def convert_latex_to_html5(self, latex):
        """Converts an arbitrary LaTeX syntax element (a string) to its
        corresponding HTML5 representation.

        @param latex: LaTeX text
        @param return: HTML5 representation of Org mode text
        """

        assert(isinstance(latex, str))
        self.stats_external_latex_to_html5_conversion += 1
        return pypandoc.convert_text(latex, 'html5', format='latex')

    def sanitize_and_htmlize_blog_content(self, entry):
        """
        Inspects a selection of the entry content data and sanitizes
        it for HTML. Each element gets converted to HTML as well.

        The teaser text of temporal articles is generated as well: entry['htmlteaser']

        Currently things that get sanitized:
        - [[foo][bar]] -> <a href="foo">bar</a>
        - id:foo -> internal links to blog article if "foo" is found as an id
        - [[id:foo]] -> see id:foo above

        @param entry: blog entry data
        @param return: entry containing partially sanitized and completely htmlized entry['content']
        """

        # debug:  [x[0] for x in entry['content']] -> which element types

        teaser_finished = False  # teaser is finished on first sub-heading or <hr>-element

        if self.autotag_language:

            if 'autotags' not in list(entry.keys()):
                entry['autotags'] = {}

            usertag_overriding_language_set = set(self.defined_languages).intersection(entry['usertags'])
            language_is_within_usertags = len(usertag_overriding_language_set) == 1

            if language_is_within_usertags:
                usertag_overriding_language = usertag_overriding_language_set.pop()
                self.logging.debug('guessing the language auto-tag was overridden by a manual tag "' + str(usertag_overriding_language) + '"')
                entry['autotags']['language'] = usertag_overriding_language  # set auto-tag
                entry['usertags'].remove(usertag_overriding_language)  # remove manual language tag from usertags because it will be handled as auto-tag; FIXXME: as of 2019-10-17, this does not get re-propagated back to the "tags" variable
            else:
                guessed_language_autotag = Utils.guess_language_from_stopword_percentages(
                    [entry['rawcontent']])

                if guessed_language_autotag:
                    entry['autotags']['language'] = guessed_language_autotag
                else:
                    # language could not be determined clearly and user
                    # did not override language tag:
                    self.logging.warning(self.current_entry_id_str() + "language of ID " +
                                         str(entry['id']) +
                                         " is not recognized clearly; using guessed_language_autotag \"unsure\"")
                    entry['autotags']['language'] = 'unsure'

        # for element in entry['content']:
        for index in range(0, len(entry['content'])):

            # initialize result with default error message for unknown entry
            # elements:
            result = '<strong>lazyblorg: Sorry, content element "' + str(entry['content'][index][0]) + \
                '" is not supported by htmlizer.py/sanitize_and_htmlize_blog_content() yet. ' + \
                'Raw content follows:</strong><br />\n<PRE>' + \
                repr(entry['content'][index][1:]) + '</PRE><br /><strong>lazyblorg: raw output end.</strong>'

            if entry['content'][index][0] == 'par':

                # example:
                # ['par', u'This is a line', u'second line']

                # join all lines of a paragraph to one single long
                # line in order to enable sanitizing URLs and such:
                result = ' '.join(entry['content'][index][1:])

                result = self.sanitize_html_characters(result)
                result = self.sanitize_internal_links(result)
                result = self.sanitize_external_links(result)
                result = self.htmlize_simple_text_formatting(result)
                result = self.fix_ampersands_in_url(result)
                template = self.template_definition_by_name('paragraph')
                result = template.replace('#PAR-CONTENT#', result)

            elif entry['content'][index][0] == 'hr':

                if not teaser_finished:
                    entry['htmlteaser'] = entry['content'][:index]
                    teaser_finished = True

                result = "<div class=\"orgmode-hr\" ></div>"

            elif entry['content'][index][0] == 'heading':

                if not teaser_finished:
                    entry['htmlteaser'] = entry['content'][:index]
                    teaser_finished = True

                # example:
                # ['heading', {'title': u'Sub-heading foo', 'level': 3}]

                # relative level: if entry has Org-mode level 3 and heading has level 5:
                # 5-3 = 2 ... relative level
                # However, article itself is <h1> so the heading is <h3>
                # (instead of <h2) -> +1
                relative_level = entry['content'][index][
                    1]['level'] - entry['level'] + 1
                self.logging.debug(self.current_entry_id_str() +
                                   'heading [' + entry['content'][index][1]['title'] +
                                   '] has relative level ' + str(relative_level))

                result = entry['content'][index][1]['title']
                result = self.sanitize_html_characters(result)
                result = self.sanitize_internal_links(result)
                result = self.sanitize_external_links(result)
                result = self.htmlize_simple_text_formatting(result)
                result = self.fix_ampersands_in_url(result)
                result = self.template_definition_by_name(
                    'section-begin').replace('#SECTION-TITLE#', result)
                result = result.replace('#SECTION-LEVEL#', str(relative_level))

            elif entry['content'][index][0] == 'DISABLEDlist':

                # For now, let's use the fall-back of pandoc to render lists instead.

                # example:
                # FIXXME example for list

                result = self.template_definition_by_name('ul-begin')
                for listitem in entry['content'][index][1]:
                    content = self.sanitize_html_characters(listitem)
                    content = self.sanitize_internal_links(content)
                    content = self.sanitize_external_links(content)
                    content = self.htmlize_simple_text_formatting(result)
                    content = self.fix_ampersands_in_url(content)
                    content += self.template_definition_by_name(
                        'ul-item').replace('#CONTENT#', content)
                    result += content

                result += self.template_definition_by_name('ul-end')

            elif entry['content'][index][0] == 'html-block':

                # example:
                # ['html-block', u'my-HTML-example name', [u'    foo', u'bar', u'  <foo />', u'<a href="bar">baz</a>']]

                if not entry['content'][index][1]:
                    # if html-block has no name -> insert as raw HTML
                    result = '\n'.join(entry['content'][index][2])
                else:
                    # if html-block has a name -> insert as
                    # html-source-code-example
                    result = self.template_definition_by_name('html-begin')
                    result = result.replace(
                        '#NAME#', entry['content'][index][1] + '<br />:')
                    result += self.sanitize_html_characters(
                        '\n'.join(
                            entry['content'][index][2])).replace(
                        ' ', '&nbsp;').replace(
                        '\n', '<br />\n')
                    result += self.template_definition_by_name('html-end')

            elif entry['content'][index][0] == 'verse-block' or \
                    entry['content'][index][0] == 'example-block' or \
                    entry['content'][index][0] == 'colon-block':

                # example:
                # ['verse-block', False, [u'first line', u'second line']]
                # ['verse-block', u'This is something:', [u'first line', u'second line']]
                # ['example-block', False, [u'first line', u'second line']]
                # ['example-block', u'This is my example:', [u'first line', u'second line']]
                # ['colon-block', False, [u'first line', u'second line']]
                result = None

                result = self.template_definition_by_name('named-pre-begin')
                if entry['content'][index][1]:
                    result = self.template_definition_by_name(
                        'named-pre-begin')
                    result = result.replace(
                        '#NAME#', entry['content'][index][1])
                else:
                    result = self.template_definition_by_name('pre-begin')

                # concatenate the content lines:
                if entry['content'][index][0] == 'colon-block':
                    # remove the leading colons:
                    mycontent = '\n'.join(entry['content'][index][2])[
                        1:].replace('\n:', '\n')
                else:
                    mycontent = '\n'.join(entry['content'][index][2])

                # for verse blocks, do org-mode formatting:
                if entry['content'][index][0] == 'verse-block':
                    mycontent = self.htmlize_simple_text_formatting(
                        self.sanitize_external_links(
                            self.sanitize_internal_links(self.sanitize_html_characters(mycontent))))

                if entry['content'][index][0] in ['example-block', 'colon-block']:
                    mycontent = self.sanitize_html_characters(mycontent)

                result += mycontent
                if entry['content'][index][1]:
                    result += self.template_definition_by_name('named-pre-end')
                else:
                    result += self.template_definition_by_name('pre-end')

            elif entry['content'][index][0] == 'quote-block':

                # example:
                # ['quote-block', False, [u'first line', u'second line']]

                # FIXXME: add interpretation of quotes: things like lists can
                # occur within

                result = self.template_definition_by_name('blockquote-begin')
                mycontent = '\n'.join(entry['content'][index][2])
                result += self.htmlize_simple_text_formatting(
                    self.sanitize_external_links(
                        self.sanitize_html_characters(mycontent)))
                result = self.sanitize_internal_links(result).replace('\n\n', '<br />\n')
                result += self.template_definition_by_name('blockquote-end')

            elif entry['content'][index][0] == 'src-block':

                # example:
                # ['src-block', False, [u'first line', u'second line']]

                result = None

                if entry['content'][index][1]:
                    result = self.template_definition_by_name(
                        'named-src-begin')
                    result = result.replace(
                        '#NAME#', entry['content'][index][1])
                else:
                    result = self.template_definition_by_name('src-begin')

                result += self.sanitize_html_characters('\n'.join(entry['content'][index][2]))
                if entry['content'][index][1]:
                    result += self.template_definition_by_name('named-src-end')
                else:
                    result += self.template_definition_by_name('src-end')

            elif entry['content'][index][0] == 'mytable':

                # entry['content'][index][0] == 'mytable':
                #  ['table', u'Table-name', [u'| My  | table |     |',
                #                            u'|-----+-------+-----|',
                #                            u'| 23  | 42    |  65 |',
                #                            u'| foo | bar   | baz |']]
                # entry['content'][index][1] == u'Table-name'
                # entry['content'][index][2] -> list of table rows

                # FIXXME: table name is ignored so far; probably don't separate
                # it in orgparser?

                sanitized_lines = []
                for tablerow in entry['content'][index][2]:
                    sanitized_lines.append(
                        self.sanitize_internal_links(
                            tablerow,
                            keep_orgmode_format=True))
                result = self.convert_org_to_html5('\n'.join(sanitized_lines))

            elif entry['content'][index][0] == 'cust_link_image':
                # ['cust_link_image',
                #  u'2017-03-11T18.29.20 Sterne im Baum -- mytag.jpg', -> file name of customized image link
                #  u'Link description of the image',  -> the optional description of a link; like "bar" in [[foo][bar]]
                #  u'Some beautiful stars in a tree', -> an optional caption
                #  {u'width': u'300', u'alt': u'Stars in a Tree', u'align': u'right', u'title': u'Some Stars'}
                # ]    -> attr_html attributes (dict)

                filename = self.locate_cust_link_image(entry['content'][index][1])

                # check if filename is the original one or was replaced by a similar one:
                if filename != entry['content'][index][1]:
                    # write back new filename if an alternative filename was derived:
                    logging.info('filename ' + filename + ' is an alternative to ' + entry['content'][index][1])
                    entry['content'][index][1] = filename

                # issue a warning if
                # WARN_IF_IMAGE_FILE_NOT_TAGGED_WITH is non-empty and
                # the tag is not found in the filename
                if config.WARN_IF_IMAGE_FILE_NOT_TAGGED_WITH and \
                   len(config.WARN_IF_IMAGE_FILE_NOT_TAGGED_WITH) > 0 and \
                   not Utils.contains_tag(filename, config.WARN_IF_IMAGE_FILE_NOT_TAGGED_WITH):
                    self.logging.warning('WARN_IF_IMAGE_FILE_NOT_TAGGED_WITH("' +
                                         config.WARN_IF_IMAGE_FILE_NOT_TAGGED_WITH + '"): filename "' + filename +
                                         '" of entry [[id:' + entry['id'] + ']] does not contain the tag')

                description = entry['content'][index][2]
                caption = entry['content'][index][3]
                attributes = entry['content'][index][4]

                # start building the result string
                result = '\n' + '<figure'

                # apply alignment things
                if 'align' in list(attributes.keys()):
                    if attributes['align'].lower() in ['left', 'right', 'float-left', 'float-right', 'center']:
                        result += ' class="image-' + attributes['align'].lower() + '"'
                    else:
                        self.logging.warning(self.current_entry_id_str() + 'image used an align parameter value which is not left|center|right: ' + str(attributes['align']))
                else:
                    # if no alignment is given, use center:
                    result += ' class="image-center"'

                # get scaled image filename
                result += '>\n'

                add_linked_image_width = False
                linked_image_filename = ''
                if 'linked-image-width' in attributes.keys():
                    # opening the href link to the externally linked
                    # image file via 'linked-image-width' attribute
                    value = attributes['linked-image-width'].lower()
                    # NOTE: detailed checks of this parameter is done
                    # in _create_path_and_generate_filenames_and_copy_images()
                    if value == 'none':
                        pass  # not linking anything
                    elif value == 'original':
                        linked_image_filename = self.get_scaled_filename(filename, False).replace(' ', '%20')
                        result += '<a href="' + linked_image_filename + '">'
                        add_linked_image_width = True
                    else:
                        linked_image_filename = self.get_scaled_filename(filename, value).replace(' ', '%20')
                        result += '<a href="' + linked_image_filename + '">'
                        add_linked_image_width = True

                if 'width' in attributes.keys():
                    result += '<img src="' + self.get_scaled_filename(filename, attributes['width']).replace(' ', '%20') + '" '
                else:
                    result += '<img src="' + self.get_scaled_filename(filename, False).replace(' ', '%20') + '" '

                # FIXXME: currently, all other attributes are ignored:
                if 'alt' in list(attributes.keys()):
                    result += 'alt="' + attributes['alt'] + '" '
                else:
                    result += 'alt="" '  # alt tag must not be omitted in HTML5 (except when using figcaption, where it is optional)
                if 'width' in list(attributes.keys()):
                    result += 'width="' + attributes['width'] + '" '

                result += '/>'

                if add_linked_image_width:
                    # closing the href link to the externally linked
                    # image file via 'linked-image-width' attribute
                    result += '</a>'

                # determine, if a caption (of a description) is necessary:
                if description == filename:
                    # If filename equals description, omit it because it does not make sense to me:
                    description = None
                if description and caption:
                    # We've got both: a description and a caption. I'm
                    # deciding to use the description in those cases
                    # and issue a warning:
                    self.logging.warning(self.current_entry_id_str() + 'a customized image had description *and* caption. I used the caption: [' +
                                         repr(entry['content'][index][1:]) + ']')
                    description = caption
                elif caption:
                    # a caption always results in a caption of course
                    description = caption
                if description:
                    # generate the figcaption
                    result += '\n<figcaption>' + description

                    # add config.CLUE_TEXT_FOR_LINKED_IMAGES when all
                    # checks are positive:
                    if 'linked-image-width' in attributes.keys() and \
                       attributes['linked-image-width'] != 'none' and \
                       'autotags' in entry.keys() and \
                       'language' in entry['autotags'].keys() and \
                       entry['autotags']['language'] in self.defined_languages and \
                       entry['autotags']['language'] in config.CLUE_TEXT_FOR_LINKED_IMAGES.keys():
                        result += ' <a class="figcaption-clue-link" href="' + linked_image_filename + '">'
                        result += config.CLUE_TEXT_FOR_LINKED_IMAGES[entry['autotags']['language']]
                        result += '</a>'

                    result += '</figcaption>'

                result += '\n</figure>\n'

                # append filename and attributes to the current entry so that
                # _create_path_and_generate_filenames_and_copy_images() can copy the image file:
                # Example:
                # entry['attachments'] => [['cust_link_image', u'2017-03-11T18.29.20 Sterne im Baum -- mytag.jpg', {}],
                #                          ['cust_link_image', u'2017-03-11T18.29.20 Sterne im Baum with attributes -- mytag.jpg', {u'width': u'300', u'alt': u'Stars in a Tree', u'align': u'right', u'title': u'Some Stars'}]]
                if 'attachments' in list(entry.keys()):
                    entry['attachments'].append(['cust_link_image', filename, attributes])
                else:
                    entry['attachments'] = [['cust_link_image', filename, attributes]]

            else:  # fall-back for all content elements which do not require special treatment:

                # entry['content'][index][0] == 'mylist':
                #  ['table', [u'- an example',
                #             u'  - list subitem',
                #             u'- another line',
                #             u'  with additional line']]
                # entry['content'][index][1] -> list of lines

                list_with_element_data = []

                # assumption: content is stored in a list either on index 1 or
                # 2:
                if isinstance(entry['content'][index][1], list):
                    list_with_element_data = entry['content'][index][1]
                elif isinstance(entry['content'][index][2], list):
                    list_with_element_data = entry['content'][index][2]
                else:
                    # no content list is found:
                    message = self.current_entry_id_str() + "htmlizer.py/sanitize_and_htmlize_blog_content(): content element [" + str(
                        entry['content'][index][0]) + "] is not recognized (yet?)."
                    self.logging.critical(message)
                    raise HtmlizerException(self.current_entry_id, message)

                # sanitize internal links and send to pypandoc:
                sanitized_lines = []
                for list_item in list_with_element_data:
                    sanitized_lines.append(
                        self.sanitize_internal_links(
                            list_item,
                            keep_orgmode_format=True))
                if entry['content'][index][0] == 'latex-block':
                    result = self.convert_latex_to_html5('\n'.join(sanitized_lines))
                else:
                    result = self.convert_org_to_html5('\n'.join(sanitized_lines))

                # pandoc is converting
                #   [[//Karl-Voit.at/foo][bar]]
                # to
                #   <a href="file:////Karl-Voit.at/foo">bar</a>
                # which is wrong. This hack replaces occurrences of
                # 'file:////Karl-Voit.at' with '//Karl-Voit.at' and
                # fixes this issue, resulting in
                #   <a href="//Karl-Voit.at/foo">bar</a>
                # NOTE: if you can think of a cleaner way, let me know!
                result = result.replace('file://' + config.BASE_URL, config.BASE_URL)

                if result == '\n':
                    self.logging.warning(self.current_entry_id_str() + 'Block of type ' +
                                         {str(entry['content'][index][0])} +
                                         ' could not converted into html5 via pypandoc (or it is empty): ' +
                                         '\n'.join(sanitized_lines))

            # replace element in entry with the result string:
            entry['content'][index] = result

        # in case no sub-heading or <hr>-element was found: everything is the
        # teaser:
        if not teaser_finished:
            entry['htmlteaser-equals-content'] = True
        else:
            entry['htmlteaser-equals-content'] = False

        return entry

    def get_scaled_filename(self, filename, width):
        """
        If the attributes dict contains an attribute for width, return a
        file name which contains the scaled value in its name.

        @param filename: a string containing a file name (basename) without path
        @param width: image width as string
        @param returns: a string of a file-name (basename) that holds the scaled value or the original name if no width attribute is found
        """

        if width:
            (basename, extension) = os.path.splitext(filename)
            return basename + ' - scaled width ' + width + extension
        else:
            return filename

    def fix_ampersands_in_url(self, content):
        """
        sanitize_html_characters() is really dumb and replaces
        ampersands in URLs as well. This method finds those broken
        URLs and fixes them.

        If this method of fixing something that should be done in a
        correct way in the first place smells funny, you are
        right. However, this seemed to be the more efficient way
        regarding to implementation. Fix it, if you like :-)

        NOTE: Does not replace several ampersands in the very same
        URL. However, this use-case of several ampersands in one URL
        is very rare.

        @param entry: string
        @param return: fixed string
        """

        result = re.sub(self.FIX_AMPERSAND_URL_REGEX, r'\1&\3', content)
        if result != content:
            self.logging.debug(self.current_entry_id_str() +
                               'fix_ampersands_in_url: fixed \"' + content +
                               '\" to \"' + result + '\"')
        return result

    def htmlize_simple_text_formatting(self, content):
        """
        Transforms simple text formatting syntax into HTML entities such as
        *bold*, ~source~.

        FIXXME: not yet implemented: /italic/ (<i>), _underlined_, +strikethrough+ (<s>)

        @param entry: string
        @param return: HTMLized string

        """

        assert(isinstance(content, str))

        content = re.subn(self.BOLD_REGEX, r'\1<b>\2</b>\3', content)[0]
        content = re.subn(self.CODE_REGEX, r'\1<code>\2</code>\3', content)[0]
        content = re.subn(self.VERBATIM_REGEX, r'\1<code>\2</code>\3', content)[0]
        content = re.subn(self.STRIKE_THROUGH_REGEX, r'\1<s>\2</s>\3', content)[0]

        assert(isinstance(content, str))

        return content

    def sanitize_html_characters(self, content):
        """
        Replaces all occurrences of [<>] with their HTML representation.

        Numeric values: http://www.ascii.cl/htmlcodes.htm

        FIXXME: build an exhaustive list of replacement characters

        FIXXME: use a more elegant replacement construct such as http://stackoverflow.com/questions/5499078/fastest-method-to-escape-html-tags-as-html-entities
        or https://wiki.python.org/moin/EscapingHtml

        @param entry: string
        @param return: sanitized string
        """

        return content.replace(
            '&',
            '&amp;').replace(
            '<',
            '&lt;').replace(
            '>',
            '&gt;').replace(
            '—',
            '&mdash;')

    def sanitize_feed_html_characters(self, content):
        """
        Replaces all occurrences of [<>] with their HTML representation for the atom feeds.

        According to http://stackoverflow.com/questions/281682/reference-to-undeclared-entity-exception-while-working-with-xml
        HTML-entities like &mdash; must not be part of XML.

        Numeric values: http://www.ascii.cl/htmlcodes.htm

        FIXXME: build an exhaustive list of replacement characters

        FIXXME: use a more elegant replacement construct such as http://stackoverflow.com/questions/5499078/fastest-method-to-escape-html-tags-as-html-entities
        or https://wiki.python.org/moin/EscapingHtml

        @param entry: string
        @param return: sanitized string
        """

        return content.replace(
            '<script async src=',
            '<script async="async" src=').replace(
            '&mdash;',
            '&#8212;')

    def generate_absolute_url(self, targetid):
        """
        returns a string containing the absolutes link for any article ID.

        @param targetid: ID of blog_data entry
        @param return: string with relative URL
        """

        assert(isinstance(targetid, str))

        url_for_the_target_id = self._target_path_for_id_without_targetdir(targetid)
        if url_for_the_target_id is None:
            return False
        return config.BASE_URL + '/' + url_for_the_target_id

    def sanitize_internal_links(
            self,
            content,
            keep_orgmode_format=False):
        """
        Replaces all internal Org-mode links of type [[id:foo]] or [[id:foo][bar baz]].

        @param content: string containing the Org-mode content
        @param keep_orgmode_format: boolean: if True, return Org-mode format instead of HTML format
        @param return: sanitized string (or False if the targetid could not be found)
        """

        assert(type(content) == str)

        allmatches = re.findall(self.ID_SIMPLE_LINK_REGEX, content)
        if allmatches != []:
            # allmatches == [(u'[[id:2014-03-02-my-persistent]]', u'2014-03-02-my-persistent')]
            #   ... FOR ONE MATCH OR FOR MULTIPLE:
            #               [(u'[[id:2014-03-02-my-temporal]]', u'2014-03-02-my-temporal'), \
            #                (u'[[id:2015-03-02-my-additional-temporal]]', u'2015-03-02-my-additional-temporal')]
            for currentmatch in allmatches:
                # internal links that contain "ignoreme" will be
                # ignored. This is the only way I can think of for
                # providing the ability to add demo links to
                # colon-blocks and so forth.
                if 'ignoreme' in currentmatch[1]:
                    continue

                internal_link = currentmatch[0]
                targetid = currentmatch[1]
                url = self.generate_absolute_url(targetid)
                if type(url) != str:
                    return False
                if keep_orgmode_format:
                    content = content.replace(
                        internal_link, "[[" + url + "][" + targetid + "]]")
                else:
                    content = content.replace(
                        internal_link, "<a href=\"" + url + "\">" + targetid + "</a>")

        allmatches = re.findall(self.ID_DESCRIBED_LINK_REGEX, content)
        if allmatches != []:
            for currentmatch in allmatches:
                # internal links that contain "ignoreme" will be
                # ignored. This is the only way I can think of for
                # providing the ability to add demo links to
                # colon-blocks and so forth.
                if 'ignoreme' in currentmatch[1]:
                    continue

                internal_link = currentmatch[0]
                targetid = currentmatch[1]
                description = currentmatch[2]
                url = self.generate_absolute_url(targetid)
                if type(url) != str:
                    return False
                if keep_orgmode_format:
                    content = content.replace(
                        internal_link, "[[" + url + "][" + description + "]]")
                else:
                    content = content.replace(
                        internal_link, "<a href=\"" + url + "\">" + description + "</a>")

        return content

    def sanitize_external_links(self, content):
        """
        Replaces all external Org-mode links of type [[foo][bar]] with
        <a href="foo">bar</a>.

        Additionally, directly written URLs are transformed in a-hrefs
        as well.

        @param entry: string
        @param return: sanitized string
        """

        content = re.sub(
            self.EXT_URL_LINK_REGEX,
            r'\1<a href="\2">\2</a>',
            content)

        content = re.sub(
            self.EXT_URL_WITH_DESCRIPTION_REGEX,
            r'<a href="\1">\2</a>',
            content)

        content = re.sub(
            self.EXT_URL_WITHOUT_DESCRIPTION_REGEX,
            r'<a href="\1">\1</a>',
            content)

        return content

    def is_int(self, string):
        """
        Checks if a given string can be casted to an integer without an error.

        @param string: string that potentially contains an integer number as text
        @param return: False if 'string' could not be casted to an integer; the int value of 'string' otherwise
        """
        try:
            value = int(string)
            return value
        except ValueError:
            return False

    def _create_path_and_generate_filenames_and_copy_images(self, entry):
        """
        Creates the target path directory, generates the filenames for org and html, and copies the
        image files to the target directory.

        @param entry: blog entry data
        @param return: htmlfilename: string containing the file name of the HTML file
        @param return: orgfilename: string containing the file name of the Org-mode raw content file
        """

        path = self._create_target_path_for_id_with_targetdir(entry['id'])

        if 'attachments' in list(entry.keys()):
            for attachment in entry['attachments']:
                if attachment[0] == 'cust_link_image':
                    # ['cust_link_image', u'2017-03-11T18.29.20 Sterne im Baum with attributes -- mytag.jpg',
                    #  {u'width': u'300', u'alt': u'Stars in a Tree', u'align': u'right', u'title': u'Some Stars'}]
                    filename = attachment[1]
                    attributes = attachment[2]

                    if 'width' in attributes.keys():
                        self.copy_cust_link_image_file(filename, path, attributes['width'])
                    else:
                        self.copy_cust_link_image_file(filename, path, False)

                    if 'linked-image-width' in attributes.keys():
                        # additionally to the image in the HTML
                        # result, we now need to generate an image (to
                        # be linked as href target) and optionally
                        # scale it

                        value = attributes['linked-image-width'].lower()  # could be one of: [none|original|<integer>]

                        if not value or (value not in ['none', 'original'] and not self.is_int(value)):
                            self.logging.error('Value of "linked-image-width" was not [none|original|<integer>] for attachment ' + str(attachment))
                        else:
                            # value of attribute is OK
                            if value == 'none':
                                self.logging.debug('User added "linked-image-width" with value ' +
                                                   '"none" which means that no external linked ' +
                                                   'image is to be added.')
                            elif value == 'original':
                                self.copy_cust_link_image_file(filename, path, None)
                            else:
                                # according to check above, the only
                                # remaining possibility is an integer
                                # that resembles the new width
                                intvalue = self.is_int(value)
                                if intvalue < 1:
                                    self.logging.error('Value of "linked-image-width" is an integer less than 1 for attachment ' + str(attachment))
                                else:
                                    self.copy_cust_link_image_file(filename, path, value)

                else:
                    message = self.current_entry_id_str() + \
                        'entry data error: _create_path_and_generate_filenames_and_copy_images(' + \
                        str(attachment) + ') used an unknown type (' + str(attachment[0]) + ').'
                    self.logging.critical(message)
                    raise HtmlizerException(self.current_entry_id, message)

        htmlfilename = os.path.join(path, "index.html")
        orgfilename = os.path.join(path, "source.org.txt")

        return orgfilename, htmlfilename

    def _generate_back_references_content(self, entry, sourcecategory):
        """
        Creates the snippet of the output file that contains the back-references to articles linked to the current one.

        @param entry: blog entry data
        @param sourcecategory: constant string determining type of current entry
        @param return: the HTML content of the entry
        """

        assert(type(sourcecategory) == str)
        content = ""
        number_of_back_references = 0

        # Adding back-references:
        if 'back-references' in list(entry.keys()):
            # FIXXME: other languages than german have to be added
            # here: (generalize using a configured list of known
            # languages?)
            if 'autotags' in list(entry.keys()):
                if 'language' in list(entry['autotags'].keys()) and entry['autotags']['language'] == 'deutsch':
                    content += self.template_definition_by_name('backreference-header-de')
                else:
                    content += self.template_definition_by_name('backreference-header-en')

            for back_reference_id in sorted(list(entry['back-references'])):

                # determine the blog_data entry whose id is like
                # back_reference_id which is a list with only one
                # entry (ideally):
                back_reference_title_list = [x for x in self.blog_data if back_reference_id == x['id']]

                # Ignore the (hard-coded) templates heading
                if back_reference_title_list[0]['id'] != 'lazyblorg-templates':

                    # If we found exactly one entry with an existing title…
                    if len(back_reference_title_list) == 1 and \
                       type(back_reference_title_list[0]['title']) == str:

                        # We re- or mis-use the sanitize function to
                        # translate the reference link to its HTML
                        # link:
                        sanitized_content = self.sanitize_internal_links(
                            self.template_definition_by_name('backreference-item').replace('#REFERENCE#',
                                                                                           '[[id:' +
                                                                                           back_reference_id +
                                                                                           '][' +
                                                                                           back_reference_title_list[0]['title'] +
                                                                                           ']]'))
                        # Sometimes, the sanitize function returns
                        # False. This is the case when my dirty
                        # quick-hack search method
                        # self._populate_backreferences() for
                        # back-references returns something stupid
                        # like a link to a phantasy item within an
                        # example block or similar. Therefore we check
                        # its content before adding it:
                        if sanitized_content:
                            content += sanitized_content
                            number_of_back_references += 1
                        else:
                            logging.warning('Article ' + entry['id'] + ' contains the back-reference to ' +
                                            back_reference_id +
                                            ' which could not be located (id: ' +
                                            back_reference_title_list[0]['id'] +
                                            '). Might be okay or a warning which you should check out.')
                    else:
                        # I'm note sure if this is reached but you
                        # never know. I chose a slightly different
                        # working than above so that you are able to
                        # differentiate the two error messages:
                        logging.warning('Article ' + entry['id'] + ' contains a back-reference to ' +
                                        back_reference_id +
                                        ' which could not be found (id: ' +
                                        back_reference_title_list[0]['id'] +
                                        '). Might be okay or a warning which you should check out.')

            content += self.template_definition_by_name('backreference-footer')

        # We now check whether or not we found at least one working
        # back-reference. If there was no working back-reference, we
        # skip the whole section instead of returning header and
        # footer without a reference in between:
        if number_of_back_references == 0:
            logging.debug('Article ' + entry['id'] + ' contains only back-references which could not be located. ' +
                          'I therefore omit the whole section alltogether.')
            return ""
        else:
            return content

    def _generate_temporal_article(self, entry):
        """
        Creates a (normal) time-oriented blog article (in contrast to a persistent blog article).

        @param entry: blog entry data
        @param return: htmlfilename: string containing the file name of the HTML file
        @param return: orgfilename: string containing the file name of the Org-mode raw content file
        @param return: htmlcontent: the HTML content of the entry
        """

        orgfilename, htmlfilename = self._create_path_and_generate_filenames_and_copy_images(entry)
        htmlcontent = ''

        for articlepart in [
            'article-header',
            'article-header-begin',
                'article-tags-begin']:
            htmlcontent += self.template_definition_by_name(articlepart)

        htmlcontent += self._replace_tag_placeholders(
            sorted(entry['usertags']), self.template_definition_by_name('article-usertag'))
        htmlcontent += self._generate_auto_tag_list_items(entry)

        for articlepart in ['article-tags-end', 'article-header-end']:
            htmlcontent += self.template_definition_by_name(articlepart)

        htmlcontent += self.__collect_raw_content(entry['content'])
        htmlcontent += self.template_definition_by_name('article-end')
        htmlcontent += self._generate_back_references_content(entry, config.TEMPORAL)
        htmlcontent += self.template_definition_by_name('article-footer')

        # replace and sanitize:
        htmlcontent = self._replace_general_article_placeholders(entry, htmlcontent)
        htmlcontent = self.sanitize_internal_links(htmlcontent)
        htmlcontent = self._insert_reading_minutes_if_found(entry, htmlcontent)

        return htmlfilename, orgfilename, htmlcontent

    def _generate_persistent_article(self, entry):
        """
        Creates a persistent blog article.

        @param entry: blog entry data
        @param return: htmlfilename: string containing the file name of the HTML file
        @param return: orgfilename: string containing the file name of the Org-mode raw content file
        @param return: htmlcontent: the HTML content of the entry
        """

        orgfilename, htmlfilename = self._create_path_and_generate_filenames_and_copy_images(entry)
        htmlcontent = ''

        for articlepart in [
                'persistent-header',
                'persistent-header-begin',
                'article-tags-begin']:
            htmlcontent += self.template_definition_by_name(articlepart)

        htmlcontent += self._replace_tag_placeholders(
            sorted(entry['usertags']), self.template_definition_by_name('article-usertag'))

        htmlcontent += self._generate_auto_tag_list_items(entry)

        for articlepart in ['article-tags-end', 'persistent-header-end']:
            htmlcontent += self.template_definition_by_name(articlepart)

        htmlcontent += self.__collect_raw_content(entry['content'])
        htmlcontent += self.template_definition_by_name('persistent-end')
        htmlcontent += self._generate_back_references_content(entry, config.PERSISTENT)
        htmlcontent += self.template_definition_by_name('persistent-footer')

        # replace and sanitize:
        htmlcontent = self._replace_general_article_placeholders(entry, htmlcontent)
        htmlcontent = self.sanitize_internal_links(htmlcontent)
        htmlcontent = self._insert_reading_minutes_if_found(entry, htmlcontent)

        return htmlfilename, orgfilename, htmlcontent

    def _generate_tag_page(self, entry):
        """
        Creates a blog article for a tag (in contrast to a temporal or persistent blog article).

        @param entry: blog entry data
        @param return: htmlfilename: string containing the file name of the HTML file
        @param return: orgfilename: string containing the file name of the Org-mode raw content file
        @param return: htmlcontent: the HTML content of the entry
        """

        logging.debug(self.current_entry_id_str() + '_generate_tag_page(' + str(entry) + ')')
        tag = entry['title']
        self.list_of_tag_pages_generated.append(tag)

        orgfilename, htmlfilename = self._create_path_and_generate_filenames_and_copy_images(entry)
        htmlcontent = ''

        for articlepart in [
            'tagpage-header',
            'tagpage-header-begin',
                'tagpage-tags-begin']:
            htmlcontent += self.template_definition_by_name(articlepart)

        htmlcontent += self._generate_auto_tag_list_items(entry)

        for articlepart in ['tagpage-tags-end', 'tagpage-header-end']:
            htmlcontent += self.template_definition_by_name(articlepart)

        htmlcontent += self.__collect_raw_content(entry['content'])
        htmlcontent += self.template_definition_by_name('tagpage-end')
        htmlcontent += self._generate_back_references_content(entry, config.TEMPORAL)
        htmlcontent += self.template_definition_by_name('article-footer')

        # replace and sanitize:
        htmlcontent = self._replace_general_article_placeholders(entry, htmlcontent)
        htmlcontent = self.sanitize_internal_links(htmlcontent)
        htmlcontent = self._insert_reading_minutes_if_found(entry, htmlcontent)

        return htmlfilename, orgfilename, htmlcontent

    def _generate_tag_pages_which_got_no_userdefined_tag_page(self):
        """
        For all tag pages where the user did not define a tag page entry
        by him/herself, create a tag page with no specific content but
        the list of entries related to the tag.
        """

        count = 0
        set_of_all_tags = set()

        # collect list of all tags (from blog_data)
        for entry in self.blog_data:
            if config.TAG_FOR_HIDDEN not in entry['usertags']:
                set_of_all_tags = set_of_all_tags.union(set(entry['usertags']))

        set_of_tags_with_no_userdefined_tag_page = set_of_all_tags - \
            set(self.list_of_tag_pages_generated) - \
            set([config.TAG_FOR_BLOG_ENTRY,
                 config.TAG_FOR_TAG_ENTRY,
                 config.TAG_FOR_PERSISTENT_ENTRY,
                 config.TAG_FOR_TEMPLATES_ENTRY,
                 config.TAG_FOR_HIDDEN])

        entry = {'content': '',
                 'category': config.TAGS,
                 'finished-timestamp-history': [datetime(2017, 1, 1, 0, 0)],  # use hard-coded date to prevent unnecessary updates
                 'firstpublishTS': datetime(2017, 1, 1, 0, 0),  # use hard-coded date to prevent unnecessary updates
                 'latestupdateTS': datetime(2017, 1, 1, 0, 0),  # use hard-coded date to prevent unnecessary updates
                 'type': 'this is an entry stub for an empty tag page'
                 }

        # for each: generate pseudo-entry containing the tag and call
        # self._generate_tag_page(entry)
        for tag in set_of_tags_with_no_userdefined_tag_page:
            entry['id'] = self.ID_PREFIX_FOR_EMPTY_TAG_PAGES + tag
            entry['title'] = tag
            self.blog_data.append(entry)
            logging.info('----> Generating tag page for: ' + tag)
            htmlfilename, orgfilename, htmlcontent = self._generate_tag_page(entry)
            self.write_content_to_file(htmlfilename, htmlcontent)
            # omit writing org file since there is no user-generated org-mode file for it
            count += 1

        return count

    def __collect_raw_content(self, contentarray):
        """
        Iterates over the contentarray and returns a concatenated string in unicode.

        @param contentarray: array of strings containing the content-elements
        @param return: string with collected content strings in unicode
        """

        htmlcontent = ''

        for element in contentarray:
            if not isinstance(element, str) and not isinstance(element, str):
                message = self.current_entry_id_str() + "element in entry['content'] is of type \"" + str(type(element)) + \
                    "\" which can not be written: [" + repr(element) + "]. Please do fix it in " + \
                    "htmlizer.py/sanitize_and_htmlize_blog_content()"
                self.logging.critical(message)
                raise HtmlizerException(self.current_entry_id, message)
            else:
                try:
                    htmlcontent += str(element)
                except:
                    self.logging.critical(self.current_entry_id_str() +
                                          "Error in entry: Element type: " + str(type(element)))
                    raise

        assert(isinstance(htmlcontent, str))
        return htmlcontent

    def _replace_tag_placeholders(self, tags, template_string):
        """
        Takes the list of user-tags and the template definition for tags
        and returns their concatenated string.

        @param tags: list of strings containing all tags of an entry
        @param template_string: string with placeholders instead of tag
        @param return: string with replaced placeholders
        """

        assert(isinstance(tags, list))
        assert(template_string)

        result = ''

        for tag in tags:
            result += template_string.replace('#TAGNAME#', tag)

        return result

    def _replace_general_blog_placeholders(self, content):
        """
        General blog placeholders (independent of an article entry) are:
        - #DOMAIN#: the domain (server) of the blog (without "(http:)//" or paths)
        - #BASE_URL#: the domain (server) of the blog with "(http:)//"
        - #COMMON-SIDEBAR#: the side-bar which is shared on all pages
        - and further more

        This method replaces all placeholders from above with their
        corresponding content.

        @param content: string with placeholders instead of content data
        @param return: content with replaced placeholders
        """

        content = content.replace(
            '#COMMON-SIDEBAR#',
            self.template_definition_by_name('common-sidebar'))
        content = content.replace('#TOP-TAG-LIST#', self._generate_top_tag_list())  # FIXXME: generate only once for performance reasons?
        content = content.replace('#DOMAIN#', config.DOMAIN)
        content = content.replace('#BASE-URL#', config.BASE_URL)
        content = content.replace('#CSS-URL#', config.CSS_URL)
        content = content.replace('#AUTHOR-NAME#', config.AUTHOR_NAME)
        content = content.replace('#BLOG-NAME#', config.BLOG_NAME)
        content = content.replace('#BLOG-LOGO#', config.BLOG_LOGO)
        content = content.replace('#DISQUS-NAME#', config.DISQUS_NAME)
        content = content.replace('#ABOUT-PAGE-ID#', config.ID_OF_ABOUT_PAGE)
        content = content.replace('#HOWTO-PAGE-ID#', config.ID_OF_HOWTO_PAGE)
        content = content.replace('#COMMENT-EMAIL-ADDRESS#', config.COMMENT_EMAIL_ADDRESS)
        content = content.replace('#TWITTER-HANDLE#', config.TWITTER_HANDLE)
        content = content.replace('#TWITTER-IMAGE#', config.TWITTER_IMAGE)
        content = content.replace('#FEEDURL_LINKS#', config.BASE_URL + '/' + config.FEEDDIR + '/' + self.__generate_feed_file_names("all")[0])
        content = content.replace('#FEEDURL_TEASER#', config.BASE_URL + '/' + config.FEEDDIR + '/' + self.__generate_feed_file_names("all")[1])
        content = content.replace('#FEEDURL_CONTENT#', config.BASE_URL + '/' + config.FEEDDIR + '/' + self.__generate_feed_file_names("all")[2])
        return content

    def _replace_general_article_placeholders(self, entry, template):
        """
        General article placeholders are:
        - #TITLE#
        - #ARTICLE-ID#: the (manually set) ID from the PROPERTIES drawer
        - #ARTICLE-URL#: the URL of the article without protocol and domain
        - #ARTICLE-YEAR#: four digit year of the article (folder path)
        - #ARTICLE-MONTH#: two digit month of the article (folder path)
        - #ARTICLE-DAY#: two digit day of the article (folder path)
        - #ARTICLE-PUBLISHED-HTML-DATETIME#: time-stamp of publishing in HTML date-time format
        - #ARTICLE-PUBLISHED-HUMAN-READABLE#: time-stamp of publishing in
        - #TAG-PAGE-LIST#: list of all blog pages using a specific tag
        - and further more

        This method replaces all placeholders from above with their
        blog article content.

        @param entry: blog entry data
        @param template: string with placeholders instead of content data
        @param return: template with replaced placeholders
        """

        content = self._replace_general_blog_placeholders(template)

        content = content.replace(
            '#ARTICLE-TITLE#',
            self.sanitize_external_links(
                self.sanitize_html_characters(
                    entry['title'])))

        year, month, day, hours, minutes = Utils.get_YY_MM_DD_HH_MM_from_datetime(entry['firstpublishTS'])
        iso_timestamp = '-'.join([year, month, day]) + \
            'T' + hours + ':' + minutes

        content = content.replace('#ARTICLE-ID#', entry['id'])
        content = content.replace('#ARTICLE-URL#', str(self._target_path_for_id_without_targetdir(entry['id'])))
        content = content.replace('#ARTICLE-YEAR#', year)
        content = content.replace('#ARTICLE-MONTH#', month)
        content = content.replace('#ARTICLE-DAY#', day)
        content = content.replace(
            '#ARTICLE-PUBLISHED-HTML-DATETIME#',
            iso_timestamp + config.TIME_ZONE_ADDON)
        content = content.replace(
            '#ARTICLE-PUBLISHED-HUMAN-READABLE#',
            iso_timestamp)

        if entry['category'] == config.TAGS:
            # replace #TAG-PAGE-LIST#
            content = content.replace(
                '#TAG-PAGE-LIST#',
                self._generate_tag_page_list(
                    entry['title']))

        if 'reading_minutes' in entry.keys():
            content = content.replace('#READINGMINUTES#', str(entry['reading_minutes']))

        return content

    def _generate_top_tag_list(self):
        """
        Generates a HTML snippet which contains the list of the top XX tags (by usage).

        FIXXME: move to populate_top_tag_list data structure to avoid re-generation for every page.

        @param return: HTML content
        """

        # Example: <li><a class="usertag" href="#BASE-URL#/tags/#TAGNAME#/">#TAGNAME#</a></li>

        tag_occurrence_list = []

        for tag in self.dict_of_tags_with_ids:
            if tag not in config.IGNORE_FOR_TOP_TAGS and \
               tag not in self.defined_languages:  # if user overrides language autotag manually, ignore it here
                tag_occurrence_list.append((tag, len(self.dict_of_tags_with_ids[tag])))

        top_tag_list = sorted(
            tag_occurrence_list,
            key=lambda entry: entry[1],
            reverse=True)[:config.NUMBER_OF_TOP_TAGS]
        # Example: top_tag_list == [(u'lazyblorg', 4), (u'programming', 3), (u'exampletag', 2),
        #                           (u'mytest', 1), (u'testtag1', 1)]

        htmlcontent = ''
        for tag in top_tag_list:
            htmlcontent += '\n              <li><a class="usertag" href="' + \
                           config.BASE_URL + '/tags/' + tag[0] + \
                           '">' + tag[0] + '</a> (' + str(tag[1]) + ')</li>'

        return htmlcontent

    def _generate_tag_page_list(self, tag):
        """
        Generates a HTML snippet which contains the list of pages of a given tag.

        @param tag: a string holding a word which is interpreted as tag
        @param return: HTML content
        """

        content = '\n<ul class=\'tag-pages-link-list\'>\n'

        if not self.dict_of_tags_with_ids or tag not in self.dict_of_tags_with_ids:
            return '\nNo blog entries with this tag so far.\n'

        # generate a list of timestamps (last update) and IDs for all
        # entries (in order to be able to sort it according to last
        # update):
        array_with_timestamp_and_ids = []
        for reference in self.dict_of_tags_with_ids[tag]:
            array_with_timestamp_and_ids.append((self.metadata[reference]['latestupdateTS'], reference))

        # generate the content according to sorted list (sort by last
        # update timestamp):
        for entry in sorted(array_with_timestamp_and_ids):

            reference = entry[1]
            year = self.metadata[reference]['firstpublishTS'].year
            month = self.metadata[reference]['firstpublishTS'].month
            day = self.metadata[reference]['firstpublishTS'].day
            minutes = self.metadata[reference]['firstpublishTS'].minute
            hours = self.metadata[reference]['firstpublishTS'].hour
            iso_timestamp = '-'.join([str(year), str(month).zfill(2), str(day).zfill(
                2)]) + 'T' + str(hours).zfill(2) + ':' + str(minutes).zfill(2)

            content += self.sanitize_internal_links(
                '  <li> <span class=\'timestamp\'>' +
                iso_timestamp +
                '</span> [[id:' +
                reference +
                '][' +
                self.metadata[reference]['title'] +
                ']]</li>\n')

        return content + '</ul>\n'

    def _get_entry_folder_name_from_entryid(self, entryid):
        """
        Takes the entry ID as string, removes optionally ISO datestamp,
        and returns a string that can be securely used as folder name.
        """

        folder = secure_filename(entryid)

        if self.DATESTAMP_REGEX.match(folder[0:10]):
            # folder contains any date-stamp in ISO format -> get rid of it
            # (it's in the path anyway)
            folder = folder[11:]

        return folder

    def _target_path_for_id_with_targetdir(self, entryid):
        """
        Returnes a directory path for a given blog ID such as:
        PERSISTENT: "TARGETDIR/ID" from the oldest finished time-stamp.
        TAGS: "TARGETDIR/tags/ID" from the oldest finished time-stamp.
        TEMPORAL: "TARGETDIR/2013/02/12/ID" from the oldest finished time-stamp.

        @param entryid: ID of a blog entry
        @param return: the resulting path as os.path string
        """

        return os.path.join(
            self.targetdir,
            self._target_path_for_id_without_targetdir(entryid))

    def _target_path_for_id_without_targetdir(self, entryid):
        """
        Returnes a directory path for a given blog ID such as:
        PERSISTENT: "ID" from the oldest finished time-stamp.
        TAGS: "tags/TITLE" if title consists of a single word.
        TEMPORAL: "2013/02/12/ID" from the oldest finished time-stamp.

        @param entryid: ID of a blog entry
        @param return: the resulting path as os.path string
        """

        if entryid.startswith(self.ID_PREFIX_FOR_EMPTY_TAG_PAGES):
            # if it is a pseudo entry for an empty tag page, extract the tag name from entryid
            return os.path.join("tags", entryid[len(self.ID_PREFIX_FOR_EMPTY_TAG_PAGES):])

        entry = self.blog_data_with_id(entryid)
        folder = self._get_entry_folder_name_from_entryid(entryid)

        if entry['category'] == config.TAGS:
            # TAGS: url is like "/tags/mytag/"
            title = entry['title']
            if ' ' in title:
                title = title.split(None, 1)[0]
                message = self.current_entry_id_str() + \
                    "article is marked as tag page by tag \"" + config.TAG_FOR_TAG_ENTRY + \
                    "\" but its title is not a single word (which is the tag): \"" + \
                    entry['title'] + "\". Please fix it now by choosing only one word as title."
                self.logging.error(message)
                # FIXXME: maybe an Exception is too harsh here?
                # (error-recovery?)
                raise HtmlizerException(self.current_entry_id, message)
            return os.path.join("tags", title)

        if entry['category'] == config.PERSISTENT:
            # PERSISTENT: url is like "/my-id/"
            return os.path.join(folder)

        if entry['category'] == config.TEMPORAL:
            # TEMPORAL: url is like "/2014/03/30/my-id/"

            year, month, day, hours, minutes = Utils.get_YY_MM_DD_HH_MM_from_datetime(entry['firstpublishTS'])
            return os.path.join(year, month, day, folder)

    def _create_target_path_for_id_with_targetdir(self, entryid):
        """
        Creates a folder hierarchy for a given blog ID such as: TARGETDIR/2013/02/12/ID

        @param entryid: ID of a blog entry
        @param return: path that was created
        """

        self.logging.debug(self.current_entry_id_str() +
                           "_create_target_path_for_id_with_targetdir(%s) called" %
                           entryid)

        assert(os.path.isdir(self.targetdir))
        idpath = self._target_path_for_id_with_targetdir(entryid)

        try:
            self.logging.debug(self.current_entry_id_str() + "creating path: \"" + idpath + "\"")
            os.makedirs(idpath)
        except OSError:
            # thrown, if it exists (no problem) or can not be created -> check!
            if os.path.isdir(idpath):
                self.logging.debug(self.current_entry_id_str() + "path [" + idpath + "] already existed")
            else:
                message = self.current_entry_id_str() + "path [" + idpath + \
                    "] could not be created. Please check and fix before next run."
                self.logging.critical(message)
                raise HtmlizerException(self.current_entry_id, message)

        return idpath

    def template_definition_by_name(self, name):
        """
        Returns the template definition whose name matches "name".

        Implicit assumptions:
        - template_definitions is a list of list of exactly three elements
        - this does not check if "name" is a valid/existing template definition string

        @param entryid: name of a template definition
        @param return: content of the template definition
        """

        # examples:
        # self.template_definitions[0][1] -> u'article-header'
        # self.template_definitions[0][2] -> [u'  <!DOCTYPE html>', u'  <html
        # xmlns="http...']
        try:
            return '\n'.join(
                [x[2:][0] for x in self.template_definitions if x[1] == name][0])
        except IndexError:
            message = "template_definition_by_name(\"" + str(name) + \
                      "\") could not find its definition within template_definitions"
            self.logging.critical(message)
            raise HtmlizerException(self.current_entry_id, message)

    def blog_data_with_id(self, entryid):
        """
        Returns the blog_data entry whose id matches entryid.

        @param entryid: ID of a blog entry
        @param return: blog_data element
        """

        matching_elements = [x for x in self.blog_data if entryid == x['id']]

        if len(matching_elements) == 1:
            return matching_elements[0]
        else:
            message = "blog_data_with_id(\"" + entryid + \
                "\") did not find exactly one result (as expected): [" + str(matching_elements) + \
                "]. Maybe you mistyped an internal link id (or there are multiple blog entries sharing IDs)?"
            if self.ignore_missing_ids:
                self.logging.warning(message)
                return self.blog_data[0]  # FIXXME: just take the first entry; cleaner solution: add a placeholder entry to blog_data?
            else:
                self.logging.error(message)
                # FIXXME: maybe an Exception is too harsh here? (error-recovery?)
                raise HtmlizerException(self.current_entry_id, message)

    def locate_cust_link_image(self, filename):
        """
        Locates image files via IMAGE_INCLUDE_METHOD. If not found, it
        tries to find alternatives if an ISO timestamp is found.

        @param filename: the base filename of an image
        @param return: string with filename that can be used
        """

        # parse Memacs file and/or traverse file system only ONCE and store its result in dir_file_dict:
        if len(self.filename_dict) == 0:
            self._populate_filename_dict()
        assert(len(self.filename_dict) > 0)

        filename = filename.replace('%20', ' ')  # replace HTML space characters with spaces

        if filename in list(self.filename_dict.keys()):
            return filename

        if filename not in list(self.filename_dict.keys()) and re.match(self.TIMESTAMP_REGEX, filename[:19]):
            # filename starts with a time-stamp
            timestamp = filename[:19]

            # try to locate a similar named file (if ISO timestamp, look if there is a file with same timestamp)
            files_with_matching_timestamps = [x for x in list(self.filename_dict.keys()) if x.startswith(timestamp)]

            if len(files_with_matching_timestamps) == 1:
                # one alternative found -> use it
                alternative_filename = files_with_matching_timestamps[0]
                self.logging.warning(self.current_entry_id_str() +
                                     'Image file \"' + filename +
                                     '\" could not be found within MEMACS_FILE_WITH_IMAGE_FILE_INDEX and/or ' +
                                     'DIRECTORIES_WITH_IMAGE_ORIGINALS. However, I found \"' +
                                     alternative_filename + '\" which has the same unique time-stamp. I\'ll take it instead.')
                return alternative_filename

            elif len(files_with_matching_timestamps) == 0:
                # no matching alternative found
                message = self.current_entry_id_str() + 'File \"' + filename + '\" could not be ' + \
                    'located within MEMACS_FILE_WITH_IMAGE_FILE_INDEX ' + \
                    'and/or DIRECTORIES_WITH_IMAGE_ORIGINALS. Its time-stamp could not be found in ' + \
                    'another filename as well.'
                self.logging.critical(message)
                raise HtmlizerException(self.current_entry_id, message)

            else:
                # multiple matching alternatives found -> error
                message = self.current_entry_id_str() + 'File \"' + filename + '\" could not be ' + \
                    'located within MEMACS_FILE_WITH_IMAGE_FILE_INDEX and/or ' + \
                    'DIRECTORIES_WITH_IMAGE_ORIGINALS. It starts with a time-stamp which could be found in ' + \
                    'other files but it is not unique. Please adapt accordingly: ' + str(files_with_matching_timestamps)
                self.logging.critical(message)
                raise HtmlizerException(self.current_entry_id, message)

        if filename not in list(self.filename_dict.keys()):
            # recover mechanism (using ISO timestamp) did not work either -> error
            message = self.current_entry_id_str() + 'File \"' + filename + '\" could not be located ' + \
                'within MEMACS_FILE_WITH_IMAGE_FILE_INDEX ' + \
                'and/or DIRECTORIES_WITH_IMAGE_ORIGINALS.'
            self.logging.critical(message)
            raise HtmlizerException(self.current_entry_id, message)

    def _insert_reading_minutes_if_found(self, entry, htmlcontent):
        """
        Handles the snippet that contains the estimation for the reading minutes.
        Deletes the snippet of the template if none found.
        """
        content = ''
        if 'reading_minutes' in entry.keys():
            if '#READING-MINUTES-SECTION#' in htmlcontent:
                # insert snippet
                snippetname = 'reading-time-'

                # handle one or many minutes: (I do have different snippets for those cases)
                if entry['reading_minutes'] == 1:
                    snippetname += 'one-minute-'
                else:
                    snippetname += 'multiple-minutes-'

                # handle different languages:
                if entry['autotags']['language'] == 'deutsch':
                    # FIXXME: other languages than german have to be added
                    # here: (generalize using a configured list of known
                    # languages?)
                    snippetname += 'de'
                else:
                    snippetname += 'en'

                # insert snippet:
                content = htmlcontent.replace('#READING-MINUTES-SECTION#', self.template_definition_by_name(snippetname))
                # replace actual minutes (if found):
                content = self._replace_general_article_placeholders(entry, content)
                return content
            else:
                # remove template snippet because we've got no minutes to insert
                # NOTE: Should be dead code
                logging.warning('Entry %s: missing reading minutes, removing snippet' % entry['id'])
                return htmlcontent.replace('#READING-MINUTES-SECTION#', '')
        else:
            # missing reading minutes should only be OK with
            # auto-generated tag pages. Report error if otherwise:
            if not entry['id'].startswith(self.ID_PREFIX_FOR_EMPTY_TAG_PAGES):
                logging.warning('Entry %s: missing reading minutes in "entry[]"' % entry['id'])
            return htmlcontent

    def _scale_and_write_image_file(self, image_data, destinationfile, newwidth, newheight):
        """
        Writes a scaled image file.

        @param image_data: the original filename of an image
        @param destinationfile: the filename of the scaled image
        @param newwidth: string of new width when scaling
        @param newheight: string of new height when scaling
        """
        try:
            cv2.imwrite(destinationfile,
                        cv2.resize(image_data, (int(newwidth), int(newheight)), interpolation=cv2.INTER_CUBIC))
        except:
            self.logging.critical('Error when scaling file \"' + image_data +
                                  '\" to file \"' + destinationfile + '\"')
            raise

    def _copy_image_file_without_exif(self, sourcefilename, destinationfilename):
        """
        Copies an image file and remoevs the optional Exif headers.

        @param sourcefilename: the original path to the filename of an image
        @param destinationfilename: the filename of the copied image
        """
        image_file_data = cv2.imread(sourcefilename)
        height, width = image_file_data.shape[:2]
        try:
            cv2.imwrite(destinationfilename,
                        cv2.resize(image_file_data, (int(width), int(height)), interpolation=cv2.INTER_CUBIC))
        except:
            self.logging.critical('Error when copying image file \"' + sourcefilename +
                                  '\" to file \"' + destinationfilename + '\"')
            raise

    def _copy_a_file(self, sourcefile, destinationfile):
        """
        Copies a file and does exception handling.

        @param sourcefile: the original filename
        @param destinationfile: the filename of the resulting copy
        """
        try:
            copyfile(sourcefile, destinationfile)
            self.logging.debug('Copied the file "' + sourcefile + '" to "' + destinationfile + '"')
        except:
            self.logging.critical("Error when copying the image file: " + str(destinationfile))
            raise

    def _update_image_cache(self, original_filename, cached_image_file_name):
        """
        If the cache directory is found, make sure that its cached file is
        either created or replaced with the original_filename.

        @param original_filename: the original filename
        @param cached_image_file_name: the filename of the resulting cached copy
        """
        if os.path.isdir(config.IMAGE_CACHE_DIRECTORY):
            if os.path.isfile(cached_image_file_name):
                self.logging.debug('Removing the old cached image file "' + cached_image_file_name + '" in the IMAGE_CACHE_DIRECTORY')
                os.remove(cached_image_file_name)
            self._copy_a_file(original_filename, cached_image_file_name)
        else:
            self.logging.debug('config.IMAGE_CACHE_DIRECTORY "' + config.IMAGE_CACHE_DIRECTORY + '" is not an existing directory. Skipping the cache update.')

    def copy_cust_link_image_file(self, filename, articlepath, width):
        """
        Locates image files via IMAGE_INCLUDE_METHOD and copies it to the blog article directory.

        If config.IMAGE_CACHE_DIRECTORY is set to an existing directory, scaling of image files
        is reduced to non-existing cached files or updated original files where the cached file
        is older than the original one.

        @param filename: the base filename of an image
        @param articlepath: the directory path to put the file into
        @param width: string containing the width of the target image file. If False, no scaling will be done.
        """

        # image was located using locate_cust_link_image() prior to this function
        assert(filename in list(self.filename_dict.keys()))

        image_file_path = self.filename_dict[filename]
        if not os.path.isfile(image_file_path):
            # image found in index but not on hard disk
            message = self.current_entry_id_str() + 'File \"' + filename + '\" is found within Memacs index (\"' + \
                image_file_path + '\") but could not be located in the file system.'
            self.logging.critical(message)
            raise HtmlizerException(self.current_entry_id, message)
        else:
            # path to image file was found
            destinationfile = os.path.join(articlepath, self.get_scaled_filename(filename, width))

            if not width and not os.path.isfile(destinationfile):
                # User did not state any width → use original file but
                # get rid of exif header by scaling to same size
                self._copy_image_file_without_exif(image_file_path, destinationfile)

            elif width and not os.path.isfile(destinationfile):
                # User did specify a width → resize if necessary
                try:

                    cached_image_file_name = os.path.join(config.IMAGE_CACHE_DIRECTORY, os.path.basename(destinationfile))

                    if os.path.isfile(cached_image_file_name) and os.path.getmtime(cached_image_file_name) > os.path.getmtime(image_file_path):
                            self.logging.debug('CACHE HIT: cached file "' + cached_image_file_name +
                                               '" is newer than the original file "' + image_file_path +
                                               '". Therefore I copy the cached one instead of scaling a new one.')
                            self._copy_a_file(cached_image_file_name, destinationfile)
                    else:
                        # Cache miss cases:

                        image_file_data = cv2.imread(image_file_path)
                        current_height, current_width = image_file_data.shape[:2]
                        newwidth = float(width)
                        newheight = current_height * (newwidth / current_width)

                        if abs(current_width - newwidth) < 2:
                            # If there is no big difference between the image
                            # size and the width specified by the user, copy
                            # original image instead of interpolate a new one but
                            # get rid of exif header by scaling to same size
                            self._copy_image_file_without_exif(image_file_path, destinationfile)

                        elif os.path.isfile(cached_image_file_name):
                            # If a cached copy is found, check if it still
                            # newer than the original file. Re-generate
                            # file and update cache if necessary
                            if os.path.getmtime(cached_image_file_name) < os.path.getmtime(image_file_path):
                                self.logging.debug('CACHE MISS: mtime of cached file "' + cached_image_file_name +
                                                   '" is older than the original file "' + image_file_path +
                                                   '". Therefore I scale a new one to "' + destinationfile + '".')
                                self._scale_and_write_image_file(image_file_data, destinationfile, newwidth, newheight)
                                self.stats_images_resized += 1
                                self._update_image_cache(destinationfile, cached_image_file_name)
                        else:
                            # We did not find any cached file. So generate
                            # a new image and update cache if necessary
                            self.logging.debug('CACHE MISS: no cached file "' + cached_image_file_name + '" found. Scaling a new one.')
                            self._scale_and_write_image_file(image_file_data, destinationfile, newwidth, newheight)
                            self.stats_images_resized += 1
                            self._update_image_cache(destinationfile, cached_image_file_name)
                except:
                    # This is only to add the entry ID to the
                    # exception output which is catched and re-raised
                    # from the invoked methods
                    self.logging.critical('Something happened with entry ID: ' + self.current_entry_id_str())
                    raise

            else:
                self.logging.debug('Image file \"' + filename + '\" was already copied for this directory \"' + articlepath + '\" -> multiple usages within same blog article')

        # FIXXME: FUTURE? generate scaled version when width/height is set

    def _populate_filename_dict(self):
        """
        Locates and parses the directory config.DIRECTORIES_WITH_IMAGE_ORIGINALS for filename index. Result is stored in self.filename_dict.
        """

        self.logging.info('• Building index of files …')
        time_before = time()
        if (config.IMAGE_INCLUDE_METHOD == config.IMAGE_INCLUDE_METHOD_MEMACS or
                config.IMAGE_INCLUDE_METHOD == config.IMAGE_INCLUDE_METHOD_MEMACS_THEN_DIR):

            assert(os.path.isfile(config.MEMACS_FILE_WITH_IMAGE_FILE_INDEX))

            # t = '** <2010-03-18 18:11> [[file:/home/user/directory/subdirectory/2010-03-18_Presentation_ProductXY.pdf][2010-03-18_Presentation_ProductXY.pdf]]'
            # re.match(r'^\*\* <.+> \[\[file:([^\]]+)\]\[(.+)\]\]$', t).groups()
            # results in: ('/home/user/directory/subdirectory/2010-03-18_Presentation_ProductXY.pdf', '2010-03-18_Presentation_ProductXY.pdf')
            MEMACS_FILE_LINE_REGEX = re.compile(r'^\*\* <.+> \[\[file:([^\]]+)\]\[(.+)\]\]$')

            self.logging.debug('Building index of Memacs as stated in MEMACS_FILE_WITH_IMAGE_FILE_INDEX  \"' + config.MEMACS_FILE_WITH_IMAGE_FILE_INDEX + '\" …')
            with codecs.open(config.MEMACS_FILE_WITH_IMAGE_FILE_INDEX, encoding='utf-8') as memacs_file_handle:
                for line in memacs_file_handle:
                    components = re.match(MEMACS_FILE_LINE_REGEX, line)
                    if components:
                        path, filename = components.groups()
                        # FIXXME: *no* check for double entries in the Memacs file because next line is *very* slow:
                        # if filename in self.filename_dict.keys():
                        #     # there is already an entry for the filename
                        #     multiple_entries += 1
                        #     message = u'The Memacs file \"' + filename + '\" appears multiple times: ' + path + ' AND ' + self.filename_dict[filename]
                        #     #self.logging.warning(message)
                        # else:
                        #     append entry to dict
                        self.filename_dict[filename] = path

        if config.IMAGE_INCLUDE_METHOD == config.IMAGE_INCLUDE_METHOD_MEMACS_THEN_DIR or \
           config.IMAGE_INCLUDE_METHOD == config.IMAGE_INCLUDE_METHOD_DIR:

            index = 0
            for currentdir in config.DIRECTORIES_WITH_IMAGE_ORIGINALS:

                if not os.path.isdir(currentdir):
                    # warnings already done by checks in config.py
                    # if an image could not be located later on, there will be an error
                    continue

                self.logging.debug('Building index of files as stated in DIRECTORIES_WITH_IMAGE_ORIGINALS[' + str(index) + '] \"' + currentdir + '\" …')
                for (dirpath, dirnames, filenames) in os.walk(currentdir):
                    # Example:
                    # (Pdb) dirpath
                    #     '/home/user/src/lazyblorg/testdata/testimages'
                    # (Pdb) dirnames
                    #     []
                    # (Pdb) filenames
                    #     ['2017-03-11T18.29.20 Sterne im Baum -- mytag.jpg']
                    for filename in filenames:
                        self.filename_dict[filename] = os.path.join(dirpath, filename)
                index += 1

        time_after = time()
        self.logging.info('Built index for ' + str(len(self.filename_dict)) +
                          ' files (in %.2f seconds)' % (time_after - time_before))

    def current_entry_id_str(self):
        "returns a string representation of self.current_entry_id"
        if self.current_entry_id:
            return '[Entry ID ' + self.current_entry_id + '] • '
        else:
            return '[Not related to a specific entry ID] • '

# Local Variables:
# End:
