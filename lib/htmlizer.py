# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2015-05-20 18:56:50 vk>

import config  # lazyblorg-global settings
import sys
import logging
import os
from datetime import datetime
from time import localtime, strftime
import re  # RegEx: for parsing/sanitizing
import codecs
from lib.utils import Utils  # for guess_language_from_stopword_percentages()

try:
    from werkzeug.utils import secure_filename  # for sanitizing path components
except ImportError:
    print "Could not find Python module \"werkzeug\".\nPlease install it, e.g., with \"sudo pip install werkzeug\"."
    sys.exit(1)

try:
    import pypandoc
except ImportError:
    print "Could not find Python module \"pypandoc\".\nPlease install it, e.g., with \"sudo pip install pypandoc\"."
    sys.exit(1)


## NOTE: pdb hides private variables as well. Please use:   data = self._OrgParser__entry_data ; data['content']


class HtmlizerException(Exception):
    """
    Exception for all kind of self-raised htmlizing errors
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Htmlizer(object):
    """
    Class for generating HTML output of lazyblorg
    """

    logging = None  # instance of logger

    template_definitions = None  # list of lists ['description', 'content'] with content being the HTML templates
    targetdir = None  # string of the base directory of the blog
    blog_data = None  # internal representation of the complete blog content
    generate = None  # list of IDs which blog entries should be generated
    increment_version = None  # list of IDs which blog entries gets an update
    blogname = None  # string which is the base directory after targetdirectory
    blog_tag = None  # string that marks blog entries (as Org-mode tag)
    about_blog = None  # string containing a short description of the blog
    autotag_language = False  # boolean, if guessing language + autotag should be done

    ## find internal links to Org-mode IDs: [[id:simple]] and [[id:with][a description]]
    ID_SIMPLE_LINK_REGEX = re.compile('(\[\[id:([^\[]+?)\]\])')
    ID_DESCRIBED_LINK_REGEX = re.compile('(\[\[id:([^\]]+?)\]\[([^\]]+?)\]\])')

    ## find external links such as [[http(s)://foo.com][bar]]:
    EXT_URL_WITH_DESCRIPTION_REGEX = re.compile(u'\[\[(http[^ ]+?)\]\[(.+?)\]\]', flags=re.U)

    ## find external links such as [[foo]]:
    EXT_URL_WITHOUT_DESCRIPTION_REGEX = re.compile(u'\[\[(.+?)\]\]', flags=re.U)

    ## find external links such as http(s)://foo.bar
    EXT_URL_LINK_REGEX = re.compile(u'([^"<>\[])(http(s)?:\/\/\S+)', flags=re.U)

    ## find '&amp;' in an active URL and fix it to '&':
    FIX_AMPERSAND_URL_REGEX = re.compile(u'(href="http(s)?://\S+?)&amp;(\S+?")', flags=re.U)

    ## find *bold text*:
    BOLD_REGEX = re.compile(u'\*([^*]+)\*', flags=re.U)

    ## find ~teletype or source text~:
    TELETYPE_REGEX = re.compile(u'~([^~]+)~', flags=re.U)

    ## any ISO date-stamp of format YYYY-MM-DD:
    DATESTAMP_REGEX = re.compile('([12]\d\d\d)-([012345]\d)-([012345]\d)', flags=re.U)

    def __init__(self, template_definitions, blogname, blog_tag, about_blog, targetdir, blog_data,
                 generate, increment_version, autotag_language):
        """
        This function initializes the class instance with the class variables.

        @param template_definitions: list of lists ['description', 'content'] with content being the HTML templates
        @param blogname: string which is the base directory after targetdirectory
        @param blog_tag: string that marks blog entries (as Org-mode tag)
        @param about_blog: string containing a short description of the blog
        @param targetdir: string of the base directory of the blog
        @param blog_data: internal representation of the complete blog content
        @param generate: list of IDs which blog entries should be generated
        @param increment_version: list of IDs which blog entries gets an update
        @param autotag_language: true, if guessing of language + its auto-tag should be done
        """

        ## initialize class variables
        self.template_definitions = template_definitions
        self.blogname = blogname
        self.blog_tag = blog_tag
        self.about_blog = about_blog
        self.targetdir = targetdir
        self.blog_data = blog_data
        self.generate = generate
        self.increment_version = increment_version
        self.autotag_language = autotag_language

         ## create logger (see http://docs.python.org/2/howto/logging-cookbook.html)
        self.logging = logging.getLogger('lazyblorg.htmlizer')

        self.logging.debug("Htmlizer initiated with %s templ.def., %s blog_data, %s generate, %s increment" %
                           (str(len(template_definitions)), str(len(blog_data)), str(len(generate)),
                            str(len(increment_version))))

    def run(self):
        """
        Basic method that creates all the output.

        @param: return: stats_generated_total: total articles generated
        @param: return: stats_generated_temporal: temporal articles generated
        @param: return: stats_generated_persistent: persistent articles generated
        @param: return: stats_generated_tags: tag articles generated
        """

        stats_generated_total, stats_generated_temporal, stats_generated_persistent, stats_generated_tags = 0, 0, 0, 0

        for entry in self.blog_data:

            ## example entry:
            ## {'level': 2,
            ## 'timestamp': datetime(2013, 2, 14, 19, 2),
            ## 'usertags': [u'mytest', u'programming'],
            ## 'autotags': [u'german', u'short'],
            ## 'lbtags': [u'blog'],
            ## 'created': datetime(2013, 2, 12, 10, 58),
            ## 'finished-timestamp-history': [datetime(2013, 2, 14, 19, 2)],
            ## 'title': u'This is an example blog entry',
            ## 'id': u'2013-02-12-lazyblorg-example-entry',
            ## 'content': [['par', u'foo...'], [...]]
            ##  }

            entry = self.sanitize_and_htmlize_blog_content(entry)

            htmlcontent = None

            if entry['category'] == config.TAGS:
                self.logging.debug("entry \"%s\" is a tag page" % entry['id'])
                self.logging.warn("generating tag pages not implemented yet")
                stats_generated_tags += 1
                ## FIXXME: generate tag blog entry

            elif entry['category'] == config.PERSISTENT:
                self.logging.debug("entry \"%s\" is a persistent page" % entry['id'])
                htmlfilename, orgfilename, htmlcontent = self._generate_persistent_article(entry)
                stats_generated_persistent += 1

            elif entry['category'] == config.TEMPORAL:
                self.logging.debug("entry \"%s\" is an ordinary time-oriented blog entry" % entry['id'])
                htmlfilename, orgfilename, htmlcontent = self._generate_temporal_article(entry)
                stats_generated_temporal += 1

            elif entry['category'] == config.TEMPLATES:
                self.logging.debug("entry \"%s\" is the/a HTML template definition. Ignoring." % entry['id'])

            else:
                message = "entry [" + entry['id'] + "] has an unknown category [" + \
                    repr(entry['category']) + "]. Please check and fix before next run."
                self.logging.critical(message)
                raise HtmlizerException(message)

            if entry['category'] == config.TAGS or entry['category'] == config.PERSISTENT or entry['category'] == config.TEMPORAL:
                self.write_content_to_file(htmlfilename, htmlcontent)
                self.write_orgcontent_to_file(orgfilename, entry['rawcontent'])
                stats_generated_total += 1

        entry_list_by_newest_timestamp = self.generate_entry_list_by_newest_timestamp()
        self.generate_entry_page(entry_list_by_newest_timestamp)
        stats_generated_total += 1

        ## generate feeds:
        feed_folder = os.path.join(self.targetdir, config.FEEDDIR)
        if not os.path.isdir(feed_folder):
            try:
                self.logging.debug("creating path for feeds: \"%s\"" % feed_folder)
                os.makedirs(feed_folder)
            except OSError:
                ## thrown, if it exists (no problem) or can not be created -> check!
                if os.path.isdir(feed_folder):
                    self.logging.debug("feed path [%s] already existed" % feed_folder)
                else:
                    message = "feed path [" + feed_folder + "] could not be created. Please check and fix before next run."
                    self.logging.critical(message)
                    raise HtmlizerException(message)
        self.__generate_feeds_for_everything(entry_list_by_newest_timestamp)

        return stats_generated_total, stats_generated_temporal, stats_generated_persistent, stats_generated_tags

    def __generate_feed_filename(self, feedstring):
        """
        Generator function for RSS/ATOM feed files.

        @param feedstring: part of the feed file which describes the feed itself
        @param return: ATOM feed file names
        """

        return \
            os.path.join(self.targetdir, config.FEEDDIR, "lazyblorg-" + feedstring + ".atom_1.0.links-only.xml"), \
            os.path.join(self.targetdir, config.FEEDDIR, "lazyblorg-" + feedstring + ".atom_1.0.links-and-content.xml")

    def __generate_new_feed(self):
        """
        Generator function for a new RSS/ATOM feed.

        @param return: a string containing all feed-related meta-data
        """

        feed = u"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom'
      xmlns:thr='http://purl.org/syndication/thread/1.0'
      xml:lang='en-us'>
  <title>""" + self.blogname + """</title>
  <id>""" + config.BASE_URL + """</id>
  <link href='""" + config.BASE_URL + """' />
  <icon>/favicon.ico</icon>
  <updated>""" + strftime('%Y-%m-%dT%H:%M:%S' + config.TIME_ZONE_ADDON, localtime()) + """</updated>
  <author>
    <name>""" + config.AUTHOR_NAME + """</name>
  </author>
  <subtitle>""" + self.about_blog + """</subtitle>
  <rights>All content written by """ + config.AUTHOR_NAME + """</rights>
  <generator uri='https://github.com/novoid/lazyblorg'>Generated from Org-mode source code using lazyblorg which is written in Python. Industrial-strength technology, baby.</generator>

        """

        return feed

    def __generate_feeds_for_everything(self, entry_list_by_newest_timestamp):
        """
        Generator function for the global RSS/ATOM feed.

        @param return: none
        """

        atom_targetfile_links, atom_targetfile_content = self.__generate_feed_filename("all")
        links_atom_feed = self.__generate_new_feed()
        content_atom_feed = self.__generate_new_feed()

        number_of_current_feed_entries = 0
        listentry = None
        listentry_index = 0

        while number_of_current_feed_entries < config.NUMBER_OF_FEED_ARTICLES and \
              len(entry_list_by_newest_timestamp) > listentry_index:

            ## get next element from entry_list
            listentry = entry_list_by_newest_timestamp[listentry_index]
            listentry_index += 1

            if listentry['category'] == config.TEMPLATES:
                continue

            ## listentry: (examples)
            ## {'url': 'about', 'timestamp': datetime(2014, 3, 9, 14, 57), 'category': 'PERSISTENT',
            ##  'id': u'2014-03-09-about'}
            ## {'url': '2013/08/22/testid', 'timestamp': datetime(2013, 8, 22, 21, 6),
            ##  'category': 'TEMPORAL', 'id': u'2013-08-22-testid'}

            blog_data_entry = self.blog_data_with_id(listentry['id'])
            ## blog_data_entry.keys() = ['category', 'level', 'timestamp', 'usertags', 'autotags', 'lbtags', 'created', 'content',
            ##                           'htmlteaser-equals-content', 'rawcontent', 'finished-timestamp-history', 'title', 'id']

            ## omit hidden entries:
            if config.TAG_FOR_HIDDEN in blog_data_entry['usertags']:
                continue

            ## filling feed entry string:
            feedentry = u"""<entry>
    <title>""" + blog_data_entry['title'] + """</title>
    <link href='""" + config.BASE_URL + "/" + listentry['url'] + """' />
    <published>""" + self._get_oldest_timestamp_for_entry(blog_data_entry)[0].strftime('%Y-%m-%dT%H:%M:%S' + config.TIME_ZONE_ADDON) + """</published>
    <updated>""" + self._get_newest_timestamp_for_entry(blog_data_entry)[0].strftime('%Y-%m-%dT%H:%M:%S' + config.TIME_ZONE_ADDON) + "</updated>\n"

            ## adding all tags:
            for tag in blog_data_entry['usertags']:

                feedentry += "    <category scheme='" + config.BASE_URL + "/" + "tags" + "/" + tag + "' term='" + tag + "' />\n"
            ## handle autotags:
            if 'autotags' in blog_data_entry.keys():
                for autotag in blog_data_entry['autotags'].keys():
                    tag = autotag + ":" + blog_data_entry['autotags'][autotag]
                    feedentry += "    <category scheme='" + config.BASE_URL + "/" + "autotags" + "/" + autotag + "' term='" + tag + "' />\n"

            ## add summary:
            feedentry += "    <summary type='xhtml'>\n<div xmlns='http://www.w3.org/1999/xhtml'>"
            if blog_data_entry['htmlteaser-equals-content']:
                feedentry += '\n'.join(blog_data_entry['content'])
            else:
                feedentry += '\n'.join(blog_data_entry['htmlteaser'])
            feedentry += "</div>\n    </summary>"

            ## add content to content-feed OR end entry for links-feed:
            links_atom_feed += feedentry + "\n    <id>" + \
                               config.BASE_URL + "/" + listentry['url'] + u"-from-feed-with-links" + \
                               "</id>\n  </entry>\n\n"
            content_atom_feed += feedentry + """    <content type='xhtml'>
      <div xmlns='http://www.w3.org/1999/xhtml'>
	""" + '\n'.join(blog_data_entry['content']) + """
      </div>
    </content>
    <id>""" + config.BASE_URL + "/" + listentry['url'] + u"-from-feed-with-content" + \
        "</id>\n  </entry>\n"

            number_of_current_feed_entries += 1

        links_atom_feed += "</feed>"
        content_atom_feed += "</feed>"

        assert(type(links_atom_feed) == unicode)
        assert(type(content_atom_feed) == unicode)

        # Save the feed to a file in various formats
        self.write_content_to_file(atom_targetfile_links, links_atom_feed)
        self.write_content_to_file(atom_targetfile_content, content_atom_feed)

        return

    def generate_entry_list_by_newest_timestamp(self):
        """

        Returns a sorted list of dicts of entry-IDs and their newest time-stamp.
        Sort order ist newest time-stamp at the front.

        @param: return: a sorted list like [ {'id':'a-new-entry', 'timestamp':datetime(), 'url'="<URL>"}, {...}]
        """

        entrylist = []

        for entry in self.blog_data:
            entrylist.append({
                'id':entry['id'],
                'timestamp':self._get_newest_timestamp_for_entry(entry)[0],
                'url':self._target_path_for_id_without_targetdir(entry['id']),
                'category':entry['category']
            })

        return sorted(entrylist, key=lambda entry: entry['timestamp'], reverse=True)

    def generate_entry_page(self, entry_list_by_newest_timestamp):
        """
        Generates and write the blog entry page with sneak previews of the most recent articles/updates.

        @param: entry_list_by_newest_timestamp: a sorted list like [ {'id':'a-new-entry', 'timestamp':datetime(), 'url'="<URL>"}, {...}]
        """

        entry_page_filename = os.path.join(self.targetdir, "index.html")

        htmlcontent = u'' + self.template_definition_by_name('entrypage-header')

        listentry = None
        listentry_index = 0
        number_of_current_teaser_entries = 0

        while number_of_current_teaser_entries < config.NUMBER_OF_TEASER_ARTICLES and \
              len(entry_list_by_newest_timestamp) > listentry_index:

            ## get next element from entry_list
            listentry = entry_list_by_newest_timestamp[listentry_index]
            listentry_index += 1

            entry = self.blog_data_with_id(listentry['id'])

            ## omit hidden entries:
            if config.TAG_FOR_HIDDEN in entry['usertags']:
                continue
                ## FIXXME: for each hidden entry within
                ## config.NUMBER_OF_TEASER_ARTICLES, there will be one
                ## entry missing. Fix this by switching to "until
                ## enough articles on main page or no articles left:
                ## find next article"

            if entry['category'] == 'TEMPORAL' or entry['category'] == 'PERSISTENT':

                content = u""

                for articlepart in ['article-preview-header', 'article-preview-tags-begin']:
                    content += self.template_definition_by_name(articlepart)

                ## tags of article
                content += self._replace_tag_placeholders(entry['usertags'],
                                                          self.template_definition_by_name('article-preview-usertag'))
                ## handle autotags
                if 'autotags' in entry.keys():
                    for autotag in entry['autotags'].keys():
                        content += self._replace_tag_placeholders([autotag + ":" + entry['autotags'][autotag]],
                                                                  self.template_definition_by_name('article-preview-autotag'))

                for articlepart in ['article-preview-tags-end', 'article-preview-begin']:
                    content += self.template_definition_by_name(articlepart)

                assert('htmlteaser-equals-content' in entry.keys())

                if not entry['htmlteaser-equals-content']:
                    ## there is more in the article than in the teaser alone:
                    content += self.template_definition_by_name('article-preview-more')

                content += self.template_definition_by_name('article-preview-end')

                ## replacing keywords:

                content = self.sanitize_internal_links(entry['category'], content)
                content = content.replace('#ARTICLE-TITLE#', self.sanitize_external_links(
                    self.sanitize_html_characters(entry['title'])))
                content = content.replace('#ARTICLE-URL#', listentry['url'])
                content = content.replace('#ARTICLE-ID#', entry['id'])

                year, month, day, hours, minutes = str(listentry['timestamp'].year).zfill(2), \
                                                   str(listentry['timestamp'].month).zfill(2), \
                                                   str(listentry['timestamp'].day).zfill(2), \
                                                   str(listentry['timestamp'].hour).zfill(2), \
                                                   str(listentry['timestamp'].minute).zfill(2)
                iso_timestamp = '-'.join([year, month, day]) + 'T' + hours + ':' + minutes

                content = content.replace('#ARTICLE-YEAR#', year)
                content = content.replace('#ARTICLE-MONTH#', month)
                content = content.replace('#ARTICLE-DAY#', day)
                content = content.replace('#ARTICLE-PUBLISHED-HTML-DATETIME#', iso_timestamp + config.TIME_ZONE_ADDON)
                content = content.replace('#ARTICLE-PUBLISHED-HUMAN-READABLE#', iso_timestamp)

                if entry['htmlteaser-equals-content']:
                    content = content.replace('#ARTICLE-TEASER#', '\n'.join(entry['content']))
                else:
                    content = content.replace('#ARTICLE-TEASER#', '\n'.join(entry['htmlteaser']))

                htmlcontent += content

            elif entry['category'] == 'TAGS':
                pass # FIXXME: implement!

        number_of_current_teaser_entries += 1

        ## add footer:
        htmlcontent += self.template_definition_by_name('entrypage-footer')

        htmlcontent = htmlcontent.replace('#ABOUT-BLOG#', self.sanitize_external_links(self.sanitize_html_characters(self.about_blog)))
        htmlcontent = htmlcontent.replace('#BLOGNAME#', self.sanitize_external_links(self.sanitize_html_characters(self.blogname)))
        htmlcontent = htmlcontent.replace('#COMMON-SIDEBAR#', self.template_definition_by_name('common-sidebar'))
        htmlcontent = self.sanitize_internal_links(config.ENTRYPAGE, htmlcontent)
        self.write_content_to_file(entry_page_filename, htmlcontent)

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
                    self.logging.critical("Error when writing file: " + str(filename))
                    raise
                    return False
            return True
        else:
            self.logging.critical("No filename (" + str(filename) + ") or content when writing file: " + str(filename))
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
                    self.logging.critical("Error when writing file: " + str(orgfilename))
                    raise
            return True
        else:
            self.logging.critical("No filename (" + str(orgfilename) + ") or Org-mode raw content when writing file: " + str(orgfilename))
            return False

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
        @param return: partially sanitized and completely htmlized entry['content']
        """

        #debug:  [x[0] for x in entry['content']] -> which element types

        teaser_finished = False  # teaser is finished on first sub-heading or <hr>-element

        #for element in entry['content']:
        for index in range(0, len(entry['content'])):

            ## initialize result with default error message for unknown entry elements:
            result = u'<strong>lazyblorg: Sorry, content element "' + str(entry['content'][index][0]) + \
                '" is not supported by htmlizer.py/sanitize_and_htmlize_blog_content() yet. ' + \
                'Raw content follows:</strong><br />\n<PRE>' + \
                repr(entry['content'][index][1:]) + '</PRE><br /><strong>lazyblorg: raw output end.</strong>'

            if entry['content'][index][0] == 'par':

                ## example:
                ## ['par', u'This is a line', u'second line']

                ## join all lines of a paragraph to one single long
                ## line in order to enable sanitizing URLs and such:
                result = u' '.join(entry['content'][index][1:])

                result = self.sanitize_html_characters(result)
                result = self.sanitize_internal_links(entry['category'], result)
                result = self.sanitize_external_links(result)
                result = self.htmlize_simple_text_formatting(result)
                result = self.fix_ampersands_in_url(result)
                template = self.template_definition_by_name('paragraph')
                result = template.replace('#PAR-CONTENT#', result)

            elif entry['content'][index][0] == 'hr':

                if not teaser_finished:
                    entry['htmlteaser'] = entry['content'][:index]
                    teaser_finished = True

                result="<div class=\"orgmode-hr\" />"

            elif entry['content'][index][0] == 'heading':

                if not teaser_finished:
                    entry['htmlteaser'] = entry['content'][:index]
                    teaser_finished = True

                ## example:
                ## ['heading', {'title': u'Sub-heading foo', 'level': 3}]

                ## relative level: if entry has Org-mode level 3 and heading has level 5:
                ## 5-3 = 2 ... relative level
                ## However, article itself is <h1> so the heading is <h3> (instead of <h2) -> +1
                relative_level = entry['content'][index][1]['level'] - entry['level'] + 1
                self.logging.debug('heading [%s] has relative level %s' %
                                   (entry['content'][index][1]['title'], str(relative_level)))

                result = entry['content'][index][1]['title']
                result = self.sanitize_html_characters(result)
                result = self.sanitize_internal_links(entry['category'], result)
                result = self.sanitize_external_links(result)
                result = self.htmlize_simple_text_formatting(result)
                result = self.fix_ampersands_in_url(result)
                result = self.template_definition_by_name('section-begin').replace('#SECTION-TITLE#', result)
                result = result.replace('#SECTION-LEVEL#', str(relative_level))

            elif entry['content'][index][0] == 'list-itemize':

                ## example:
                ## FIXXME

                result = self.template_definition_by_name('ul-begin')
                for listitem in entry['content'][index][1]:
                    content = self.sanitize_html_characters(listitem)
                    content = self.sanitize_internal_links(entry['category'], content)
                    content = self.sanitize_external_links(content)
                    content = self.htmlize_simple_text_formatting(result)
                    content = self.fix_ampersands_in_url(content)
                    content += self.template_definition_by_name('ul-item').replace('#CONTENT#', content)
                    result += content

                result += self.template_definition_by_name('ul-end')

            elif entry['content'][index][0] == 'html-block':

                ## example:
                ## ['html-block', u'my-HTML-example name', [u'    foo', u'bar', u'  <foo />', u'<a href="bar">baz</a>']]

                if not entry['content'][index][1]:
                    ## if html-block has no name -> insert as raw HTML
                    result = '\n'.join(entry['content'][index][2])
                else:
                    ## if html-block has a name -> insert as html-source-code-example
                    result = self.template_definition_by_name('html-begin')
                    result = result.replace('#NAME#', entry['content'][index][1] + u'<br />:')
                    result += self.sanitize_html_characters(
                        '\n'.join(entry['content'][index][2])).replace(' ', '&nbsp;').replace('\n', '<br />\n')
                    result += self.template_definition_by_name('html-end')

            elif entry['content'][index][0] == 'verse-block' or \
                entry['content'][index][0] == 'example-block' or \
                entry['content'][index][0] == 'colon-block':

                ## example:
                ## ['verse-block', False, [u'first line', u'second line']]
                ## ['verse-block', u'This is something:', [u'first line', u'second line']]
                ## ['example-block', False, [u'first line', u'second line']]
                ## ['example-block', u'This is my example:', [u'first line', u'second line']]
                ## ['colon-block', False, [u'first line', u'second line']]
                result = None

                result = self.template_definition_by_name('named-pre-begin')
                if entry['content'][index][1]:
                    result = self.template_definition_by_name('named-pre-begin')
                    result = result.replace('#NAME#', entry['content'][index][1])
                else:
                    result = self.template_definition_by_name('pre-begin')

                ## concatenate the content lines:
                if entry['content'][index][0] == 'colon-block':
                    ## remove the leading colons:
                    mycontent = '\n'.join(entry['content'][index][2])[1:].replace('\n:', '\n')
                else:
                    mycontent = '\n'.join(entry['content'][index][2])

                ## for verse blocks, do org-mode formatting:
                if entry['content'][index][0] == 'verse-block':
                    mycontent = self.htmlize_simple_text_formatting(
                        self.sanitize_external_links(
                            self.sanitize_internal_links(entry['category'],
                                                         self.sanitize_html_characters(mycontent))))

                self.logging.debug("result [%s]" % repr(result))
                self.logging.debug("mycontent [%s]" % repr(mycontent))
                result += mycontent
                if entry['content'][index][1]:
                    result += self.template_definition_by_name('named-pre-end')
                else:
                    result += self.template_definition_by_name('pre-end')

            elif entry['content'][index][0] == 'quote-block':

                ## example:
                ## ['quote-block', False, [u'first line', u'second line']]

                ## FIXXME: add interpretation of quotes: things like lists can occur within

                result = self.template_definition_by_name('blockquote-begin')
                mycontent = u'\n'.join(entry['content'][index][2])
                self.logging.debug("result [%s]" % repr(result))
                self.logging.debug("mycontent [%s]" % repr(mycontent))
                result += self.htmlize_simple_text_formatting(self.sanitize_external_links(self.sanitize_html_characters(mycontent)))
                result = self.sanitize_internal_links(entry['category'], result)
                result += self.template_definition_by_name('blockquote-end')

            elif entry['content'][index][0] == 'src-block':

                ## example:
                ## ['src-block', False, [u'first line', u'second line']]

                result = None

                if entry['content'][index][1]:
                    result = self.template_definition_by_name('named-src-begin')
                    result = result.replace('#NAME#', entry['content'][index][1])
                else:
                    result = self.template_definition_by_name('src-begin')

                mycontent = '\n'.join(entry['content'][index][2])

                self.logging.debug("result [%s]" % repr(result))
                self.logging.debug("mycontent [%s]" % repr(mycontent))
                result += mycontent
                if entry['content'][index][1]:
                    result += self.template_definition_by_name('named-src-end')
                else:
                    result += self.template_definition_by_name('src-end')

            elif entry['content'][index][0] == 'mytable':

                ## entry['content'][index][0] == 'mytable':
                ##  ['table', u'Table-name', [u'| My  | table |     |',
                ##                            u'|-----+-------+-----|',
                ##                            u'| 23  | 42    |  65 |',
                ##                            u'| foo | bar   | baz |']]
                ## entry['content'][index][1] == u'Table-name'
                ## entry['content'][index][2] -> list of table rows

                ## FIXXME: table name is ignored so far; probably don't separate it in orgparser?

                sanitized_lines = []
                for tablerow in entry['content'][index][2]:
                    sanitized_lines.append(
                            self.sanitize_internal_links(entry['category'], tablerow, keep_orgmode_format=True))
                result = pypandoc.convert('\n'.join(sanitized_lines),
                                          'html5', format='org')

            else:  # fall-back for all content elements which do not require special treatment:

                ## entry['content'][index][0] == 'mylist':
                ##  ['table', [u'- an example',
                ##             u'  - list subitem',
                ##             u'- another line',
                ##             u'  with additional line']]
                ## entry['content'][index][1] -> list of lines

                list_with_element_data = []

                ## assumption: content is stored in a list either on index 1 or 2:
                if type(entry['content'][index][1]) == list:
                    list_with_element_data = entry['content'][index][1]
                elif type(entry['content'][index][2]) == list:
                    list_with_element_data = entry['content'][index][2]
                else:
                    ## no content list is found:
                    message = "htmlizer.py/sanitize_and_htmlize_blog_content(): content element [" + str(entry['content'][index][0]) + \
                              "] of ID " + str(entry['id']) + " is not recognized (yet?)."
                    self.logging.critical(message)
                    raise HtmlizerException(message)

                ## sanitize internal links and send to pypandoc:
                sanitized_lines = []
                for list_item in list_with_element_data:
                    sanitized_lines.append(
                            self.sanitize_internal_links(entry['category'], list_item, keep_orgmode_format=True))
                result = pypandoc.convert('\n'.join(sanitized_lines),
                                          'html5', format='org')


            ## replace element in entry with the result string:
            entry['content'][index] = result

        ## in case no sub-heading or <hr>-element was found: everything is the teaser:
        if not teaser_finished:
            entry['htmlteaser-equals-content'] = True
        else:
            entry['htmlteaser-equals-content'] = False

        if self.autotag_language:
            if 'autotags' not in entry.keys():
                entry['autotags'] = {}
            autotag = Utils.guess_language_from_stopword_percentages([entry['rawcontent']])
            if autotag:
                entry['autotags']['language'] = autotag
            else:
                ## language could not be determined clearly:
                self.logging.warning(u"language of ID " + str(entry['id']) + " is not recognized clearly")
                entry['autotags']['language'] = u'unsure'

        return entry

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

        result = re.sub(self.FIX_AMPERSAND_URL_REGEX, ur'\1&\3', content)
        if result != content:
            self.logging.debug("fix_ampersands_in_url: fixed \"%s\" to \"%s\"" % (content, result))

        return result

    def htmlize_simple_text_formatting(self, content):
        """
        Transforms simple text formatting syntax into HTML entities such as
        *bold*, ~source~.

        FIXXME: not yet implemented: /italic/ (<i>), _underlined_, +strikethrough+ (<s>)

        @param entry: string
        @param return: HTMLized string

        """

        assert(type(content) == unicode)

        content = re.subn(self.BOLD_REGEX, ur'<b>\1</b>', content)[0]
        content = re.subn(self.TELETYPE_REGEX, ur'<code>\1</code>', content)[0]

        assert(type(content) == unicode)

        return content

    def sanitize_html_characters(self, content):
        """
        Replaces all occurrences of [<>] with their HTML representation.

        @param entry: string
        @param return: sanitized string
        """

        return content.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;')

    def generate_relative_url_from_sourcecategory_to_id(self, sourcecategory, targetid):
        """
        returns a string containing a relative link from any article of same
        category as sourcecategory to the page of targetid.

        @param sourcecategory: constant string determining type of source entry
        @param targetid: ID of blog_data entry
        @param return: string with relative URL
        """

        assert(type(targetid) == unicode or type(targetid) == str)

        url = u""

        ## build back-traverse URL
        if sourcecategory == config.TEMPORAL:
            url = u"../../../../"
        elif sourcecategory == config.PERSISTENT:
            url = u"../"
        elif sourcecategory == config.TAGS:
            url = u"../../"
        elif sourcecategory == config.ENTRYPAGE:
            url = u""
        else:
            message = "generate_relative_url_from_sourcecategory_to_id() found an unknown sourcecategory [" + \
                      str(sourcecategory) + "]"
            self.logging.critical(message)
            raise HtmlizerException(message)

        ## add targetid-URL
        url += self._target_path_for_id_without_targetdir(targetid)

        return url

    def sanitize_internal_links(self, sourcecategory, content, keep_orgmode_format=False):
        """
        Replaces all internal Org-mode links of type [[id:foo]] or [[id:foo][bar baz]].

        @param sourcecategory: constant string determining type of current entry
        @param content: string containing the Org-mode content
        @param keep_orgmode_format: boolean: if True, return Org-mode format instead of HTML format
        @param return: sanitized string
        """

        assert(type(content) in [unicode, str])

        allmatches = re.findall(self.ID_SIMPLE_LINK_REGEX, content)
        if allmatches != []:
            ## allmatches == [(u'[[id:2014-03-02-my-persistent]]', u'2014-03-02-my-persistent')]
            ##   ... FOR ONE MATCH OR FOR MULTIPLE:
            ##               [(u'[[id:2014-03-02-my-temporal]]', u'2014-03-02-my-temporal'), \
            ##                (u'[[id:2015-03-02-my-additional-temporal]]', u'2015-03-02-my-additional-temporal')]
            for currentmatch in allmatches:
                internal_link = currentmatch[0]
                targetid = currentmatch[1]
                url = self.generate_relative_url_from_sourcecategory_to_id(sourcecategory, targetid)
                if keep_orgmode_format:
                    content = content.replace(internal_link, "[[" + url + "][" + targetid + "]]")
                else:
                    content = content.replace(internal_link, "<a href=\"" + url + "\">" + targetid + "</a>")

        allmatches = re.findall(self.ID_DESCRIBED_LINK_REGEX, content)
        if allmatches != []:
            for currentmatch in allmatches:
                internal_link = currentmatch[0]
                targetid = currentmatch[1]
                description = currentmatch[2]
                url = self.generate_relative_url_from_sourcecategory_to_id(sourcecategory, targetid)
                if keep_orgmode_format:
                    content = content.replace(internal_link, "[[" + url + "][" + description + "]]")
                else:
                    content = content.replace(internal_link, "<a href=\"" + url + "\">" + description + "</a>")

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

        content = re.sub(self.EXT_URL_LINK_REGEX, ur'\1<a href="\2">\2</a>', content)

        content = re.sub(self.EXT_URL_WITH_DESCRIPTION_REGEX, ur'<a href="\1">\2</a>', content)

        content = re.sub(self.EXT_URL_WITHOUT_DESCRIPTION_REGEX, ur'<a href="\1">\1</a>', content)

        return content

    def _generate_temporal_article(self, entry):
        """
        Creates a (normal) time-oriented blog article (in contrast to a persistent blog article).

        @param entry: blog entry data
        @param return: htmlfilename: string containing the file name of the HTML file
        @param return: orgfilename: string containing the file name of the Org-mode raw content file
        @param return: htmlcontent: the HTML content of the entry
        """

        path = self._create_target_path_for_id_with_targetdir(entry['id'])
        htmlfilename = os.path.join(path, "index.html")
        orgfilename = os.path.join(path, "source.org.txt")
        htmlcontent = u''
        content = u''

        for articlepart in ['article-header', 'article-header-begin', 'article-tags-begin']:
            content += self.template_definition_by_name(articlepart)
        htmlcontent += self._replace_general_article_placeholders(entry, content)
        htmlcontent += self._replace_tag_placeholders(entry['usertags'], self.template_definition_by_name('article-usertag'))
        ## handle autotags:
        if 'autotags' in entry.keys():
            for autotag in entry['autotags'].keys():
                htmlcontent += self._replace_tag_placeholders([autotag + ":" + entry['autotags'][autotag]],
                                                              self.template_definition_by_name('article-autotag'))

        content = u''
        for articlepart in ['article-tags-end', 'article-header-end']:
            content += self.template_definition_by_name(articlepart)
        htmlcontent += self._replace_general_article_placeholders(entry, content)

        htmlcontent += self.__collect_raw_content(entry['content'])

        content = u''
        for articlepart in ['article-end', 'article-footer']:
            content += self.template_definition_by_name(articlepart)
        htmlcontent += self._replace_general_article_placeholders(entry, content)
        htmlcontent = self.sanitize_internal_links(config.TEMPORAL, htmlcontent)

        return htmlfilename, orgfilename, htmlcontent

    def _generate_persistent_article(self, entry):
        """
        Creates a persistent blog article.

        @param entry: blog entry data
        @param return: htmlfilename: string containing the file name of the HTML file
        @param return: orgfilename: string containing the file name of the Org-mode raw content file
        @param return: htmlcontent: the HTML content of the entry
        """

        path = self._create_target_path_for_id_with_targetdir(entry['id'])
        htmlfilename = os.path.join(path, "index.html")
        orgfilename = os.path.join(path, "source.org.txt")
        htmlcontent = u''
        content = u''

        for articlepart in ['persistent-header', 'persistent-header-begin', 'article-tags-begin']:
            content += self.template_definition_by_name(articlepart)
        htmlcontent += self._replace_general_article_placeholders(entry, content)
        #htmlcontent = self.sanitize_internal_links(entry['category'], htmlcontent)
        htmlcontent += self._replace_tag_placeholders(entry['usertags'], self.template_definition_by_name('article-usertag'))
        ## handle autotags:
        if 'autotags' in entry.keys():
            for autotag in entry['autotags'].keys():
                htmlcontent += self._replace_tag_placeholders([autotag + ":" + entry['autotags'][autotag]],
                                                              self.template_definition_by_name('article-autotag'))

        content = u''
        for articlepart in ['article-tags-end', 'persistent-header-end']:
            content += self.template_definition_by_name(articlepart)
        htmlcontent += self._replace_general_article_placeholders(entry, content)

        htmlcontent += self.__collect_raw_content(entry['content'])

        content = u''
        for articlepart in ['persistent-end', 'persistent-footer']:
            content += self.template_definition_by_name(articlepart)
        htmlcontent += self._replace_general_article_placeholders(entry, content)
        htmlcontent = self.sanitize_internal_links(config.PERSISTENT, htmlcontent)

        return htmlfilename, orgfilename, htmlcontent

    def __collect_raw_content(self, contentarray):
        """
        Iterates over the contentarray and returns a concatenated string in unicode.

        @param contentarray: array of strings containing the content-elements
        @param return: string with collected content strings in unicode
        """

        htmlcontent = u''

        for element in contentarray:
            if type(element) != str and type(element) != unicode:
                message = "element in entry['content'] is of type \"" + str(type(element)) + \
                    "\" which can not be written: [" + repr(element) + "]. Please do fix it in " + \
                    "htmlizer.py/sanitize_and_htmlize_blog_content()"
                self.logging.critical(message)
                raise HtmlizerException(message)
            else:
                try:
                    htmlcontent += unicode(element)
                except:
                    self.logging.critical("Error in entry")
                    self.logging.critical("Element type: " + str(type(element)))
                    raise

        assert(type(htmlcontent) == unicode)
        return htmlcontent

    def _replace_tag_placeholders(self, tags, template_string):
        """
        Takes the list of user-tags and the template definition for tags
        and returns their concatenated string.

        @param tags: list of strings containing all tags of an entry
        @param template_string: string with placeholders instead of tag
        @param return: string with replaced placeholders
        """

        assert(type(tags) == list)
        assert(template_string)

        result = u''

        for tag in tags:
            result += template_string.replace('#TAGNAME#', tag)

        return result

    def _replace_general_article_placeholders(self, entry, template):
        """
        General article placeholders are:
        - #TITLE#
        - #ABOUT-BLOG#
        - #BLOGNAME#
        - #ARTICLE-ID#: the (manually set) ID from the PROPERTIES drawer
        - #ARTICLE-YEAR#: four digit year of the article (folder path)
        - #ARTICLE-MONTH#: two digit month of the article (folder path)
        - #ARTICLE-DAY#: two digit day of the article (folder path)
        - #ARTICLE-PUBLISHED-HTML-DATETIME#: time-stamp of publishing in HTML date-time format
        - #ARTICLE-PUBLISHED-HUMAN-READABLE#: time-stamp of publishing in
        - #COMMON-SIDEBAR#: the side-bar which is shared on all pages

        This method replaces all placeholders from above with their
        blog article content.

        @param entry: blog entry data
        @param template: string with placeholders instead of content data
        @param return: template with replaced placeholders
        """

        content = template

        content = content.replace('#ARTICLE-TITLE#', self.sanitize_external_links(self.sanitize_html_characters(entry['title'])))
        content = content.replace('#ABOUT-BLOG#', self.sanitize_external_links(self.sanitize_html_characters(self.about_blog)))
        content = content.replace('#BLOGNAME#', self.sanitize_external_links(self.sanitize_html_characters(self.blogname)))

        oldesttimestamp, year, month, day, hours, minutes = self._get_oldest_timestamp_for_entry(entry)
        iso_timestamp = '-'.join([year, month, day]) + 'T' + hours + ':' + minutes

        content = content.replace('#ARTICLE-ID#', entry['id'])
        content = content.replace('#ARTICLE-YEAR#', year)
        content = content.replace('#ARTICLE-MONTH#', month)
        content = content.replace('#ARTICLE-DAY#', day)
        content = content.replace('#ARTICLE-PUBLISHED-HTML-DATETIME#', iso_timestamp + config.TIME_ZONE_ADDON)
        content = content.replace('#ARTICLE-PUBLISHED-HUMAN-READABLE#', iso_timestamp)
        content = content.replace('#COMMON-SIDEBAR#', self.template_definition_by_name('common-sidebar'))

        return content

    def _target_path_for_id_with_targetdir(self, entryid):
        """
        Returnes a directory path for a given blog ID such as:
        PERSISTENT: "TARGETDIR/ID" from the oldest finished time-stamp.
        TAGS: "TARGETDIR/tags/ID" from the oldest finished time-stamp.
        TEMPORAL: "TARGETDIR/2013/02/12/ID" from the oldest finished time-stamp.

        @param entryid: ID of a blog entry
        @param return: the resulting path as os.path string
        """

        return os.path.join(self.targetdir, self._target_path_for_id_without_targetdir(entryid))

    def _get_entry_folder_name_from_entryid(self, entryid):
        """
        Takes the entry ID as string, removes optionally ISO datestamp,
        and returns a string that can be securely used as folder name.
        """

        folder = secure_filename(entryid)

        if self.DATESTAMP_REGEX.match(folder[0:10]):
        ## folder contains any date-stamp in ISO format -> get rid of it (it's in the path anyway)
            folder = folder[11:]

        return folder

    def _target_path_for_id_without_targetdir(self, entryid):
        """
        Returnes a directory path for a given blog ID such as:
        PERSISTENT: "ID" from the oldest finished time-stamp.
        TAGS: "tags/ID" from the oldest finished time-stamp.
        TEMPORAL: "2013/02/12/ID" from the oldest finished time-stamp.

        @param entryid: ID of a blog entry
        @param return: the resulting path as os.path string
        """

        entry = self.blog_data_with_id(entryid)
        folder = self._get_entry_folder_name_from_entryid(entryid)

        if entry['category'] == config.TAGS:
            ## TAGS: url is like "/tags/mytag/"
            return os.path.join("tags", folder)

        if entry['category'] == config.PERSISTENT:
            ## PERSISTENT: url is like "/my-id/"
            return os.path.join(folder)

        if entry['category'] == config.TEMPORAL:
            ## TEMPORAL: url is like "/2014/03/30/my-id/"

            oldesttimestamp, year, month, day, hours, minutes = self._get_oldest_timestamp_for_entry(entry)
            return os.path.join(year, month, day, folder)

    def _get_newest_timestamp_for_entry(self, entry):
        """
        Reads data of entry and returns datetime object of the newest
        time-stamp of the finished-timestamp-history.

        Example result: datetime(2013, 8, 29, 19, 40)

        Implicit assumptions:
        - newest: no blog article is from before 1970-01-01

        @param entry: data of a blog entry
        @param return: datetime object of its oldest time-stamp within finished-timestamp-history
        @param return: year: four digit year as string
        @param return: month: two digit month as string
        @param return: day: two digit day as string
        @param return: hours: two digit hours as string
        @param return: minutes: two digit minutes as string
        """

        return self.__get_oldest_or_newest_timestamp_for_entry(entry, "NEWEST")

    def _get_oldest_timestamp_for_entry(self, entry):
        """
        Reads data of entry and returns datetime object of the oldest
        time-stamp of the finished-timestamp-history.

        Example result: datetime(2013, 8, 29, 19, 40)

        Implicit assumptions:
        - no blog article is from the future (comparison to now)

        @param entry: data of a blog entry
        @param return: datetime object of its oldest time-stamp within finished-timestamp-history
        @param return: year: four digit year as string
        @param return: month: two digit month as string
        @param return: day: two digit day as string
        @param return: hours: two digit hours as string
        @param return: minutes: two digit minutes as string
        """

        return self.__get_oldest_or_newest_timestamp_for_entry(entry, "OLDEST")

    def __get_oldest_or_newest_timestamp_for_entry(self, entry, search_for):
        """
        Reads data of entry and returns datetime object of the oldest or newest
        time-stamp of the finished-timestamp-history.

        Example result: datetime(2013, 8, 29, 19, 40)

        Implicit assumptions:
        - oldest: no blog article is from the future (comparison to now)
        - newest: no blog article is from before 1970-01-01

        @param entry: data of a blog entry
        @param search_for: string "OLDEST" or "NEWEST"
        @param return: datetime object of its oldest time-stamp within finished-timestamp-history
        @param return: year: four digit year as string
        @param return: month: two digit month as string
        @param return: day: two digit day as string
        @param return: hours: two digit hours as string
        @param return: minutes: two digit minutes as string
        """

        assert(entry)
        assert(type(entry) == dict)
        assert('finished-timestamp-history' in entry.keys())
        assert(search_for == "OLDEST" or search_for == "NEWEST")

        returntimestamp = False
        if search_for == "OLDEST":
            oldesttimestamp = datetime.now()
            for timestamp in entry['finished-timestamp-history']:
                if timestamp < oldesttimestamp:
                    oldesttimestamp = timestamp
            returntimestamp = oldesttimestamp
        elif search_for == "NEWEST":
            newesttimestamp = datetime(1970, 1, 1)
            for timestamp in entry['finished-timestamp-history']:
                if timestamp > newesttimestamp:
                    newesttimestamp = timestamp
            returntimestamp = newesttimestamp

        return returntimestamp, str(returntimestamp.year).zfill(2), str(returntimestamp.month).zfill(2), \
            str(returntimestamp.day).zfill(2), \
            str(returntimestamp.hour).zfill(2), str(returntimestamp.minute).zfill(2)

    def _create_target_path_for_id_with_targetdir(self, entryid):
        """
        Creates a folder hierarchy for a given blog ID such as: TARGETDIR/2013/02/12/ID

        @param entryid: ID of a blog entry
        @param return: path that was created
        """

        self.logging.debug("_create_target_path_for_id_with_targetdir(%s) called" % entryid)

        assert(os.path.isdir(self.targetdir))
        idpath = self._target_path_for_id_with_targetdir(entryid)

        try:
            self.logging.debug("creating path: \"%s\"" % idpath)
            os.makedirs(idpath)
        except OSError:
            ## thrown, if it exists (no problem) or can not be created -> check!
            if os.path.isdir(idpath):
                self.logging.debug("path [%s] already existed" % idpath)
            else:
                message = "path [" + idpath + "] could not be created. Please check and fix before next run."
                self.logging.critical(message)
                raise HtmlizerException(message)

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

        ## examples:
        ## self.template_definitions[0][1] -> u'article-header'
        ## self.template_definitions[0][2] -> [u'  <!DOCTYPE html>', u'  <html xmlns="http...']
        try:
            return '\n'.join([x[2:][0] for x in self.template_definitions if x[1] == name][0])
        except IndexError:
            message = "template_definition_by_name(\"" + str(name) + \
                      "\") could not find its definition within template_definitions"
            self.logging.critical(message)
            raise HtmlizerException(message)

    def blog_data_with_id(self, entryid):
        """
        Returns the blog_data entry whose id matches entryid.

        @param entryid: ID of a blog entry
        @param return: blog_data element
        """

#        try:#FIXXME
        matching_elements = [x for x in self.blog_data if entryid == x['id']]
#        except TypeError:
#            import pdb; pdb.set_trace()

        if len(matching_elements) == 1:
            return matching_elements[0]
        else:
            message = "blog_data_with_id(\"" + entryid + \
                "\") did not find exactly one result (as expected): [" + str(matching_elements) + \
                "]. Maybe you mistyped an internal link id (or there are multiple blog entries sharing IDs)?"
            self.logging.error(message)
            raise HtmlizerException(message)  # FIXXME: maybe an Exception is too harsh here? (error-recovery?)


#    def __filter_org_entry_for_blog_entries(self):
#        """
#        Return True if current entry from "self.__entry_data" is a valid and
#        complete blog article and thus can be added to the blog data.
#
#        @param return: True if OK or False if not OK (and entry has to be skipped)
#        """



# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
