# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2014-03-02 17:56:31 vk>

import logging
import os
import werkzeug.utils  ## for sanitizing path components
import datetime
import re  ## RegEx: for parsing/sanitizing
import codecs
#from lib.utils import *

## debugging:   for setting a breakpoint:  pdb.set_trace()
## NOTE: pdb hides private variables as well. Please use:   data = self._OrgParser__entry_data ; data['content']
import pdb
                #pdb.set_trace()## FIXXME

### FIXXXME: differ according to category (persistent, tags, temporal, templates)

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

    logging = None  ## instance of logger

    template_definitions = None  ## list of lists ['description', 'content'] with content being the HTML templates
    targetdir = None  ## string of the base directory of the blog
    blog_data = None  ## internal representation of the complete blog content
    generate = None  ## list of IDs which blog entries should be generated
    increment_version = None  ## list of IDs which blog entries gets an update
    blogname = None  ## string which is the base directory after targetdirectory
    blog_tag = None  ## string that marks blog entries (as Org-mode tag)
    about_blog = None  ## string containing a short description of the blog

    ## this tag (withing tag list of article) determines if an article
    ## is a permanent blog page (tag is found) or a time-oriented
    ## (normal) blog-entry (this tag is missing).
    PERMANENT_ENTRY_TAG = 'permanent'

    ## categories of blog entries:
    ## FIXXME: also defined in multiple other files
    TAGS = 'TAGS'
    PERSISTENT = 'PERSISTENT'
    TEMPORAL = 'TEMPORAL'
    TEMPLATES = 'TEMPLATES'

    ## this gets added to the time in order to describe time zone of the blog:
    TIME_ZONE_ADDON = '+02:00'

    ## show this many article teasers on entry page
    NUMBER_OF_TEASER_ARTICLES = 10

    ## find external links such as [[http(s)://foo.com][bar]]:
    EXT_URL_WITH_DESCRIPTION_REGEX = re.compile(u'\[\[(http[^ ]+?)\]\[(.+?)\]\]', flags = re.U)

    ## find external links such as [[foo]]:
    EXT_URL_WITHOUT_DESCRIPTION_REGEX = re.compile(u'\[\[(.+?)\]\]', flags = re.U)

    ## find external links such as http(s)://foo.bar
    EXT_URL_LINK_REGEX = re.compile(u'([^"<>\[])(http(s)?:\/\/\S+)', flags = re.U)

    ## find '&amp;' in an active URL and fix it to '&':
    FIX_AMPERSAND_URL_REGEX = re.compile(u'(href="http(s)?://\S+?)&amp;(\S+?")', flags = re.U)

    ## find *bold text*:
    BOLD_REGEX = re.compile(u'\*([^*]+)\*', flags = re.U)

    ## find ~teletype or source text~:
    TELETYPE_REGEX = re.compile(u'~([^~]+)~', flags = re.U)

    ## any ISO date-stamp of format YYYY-MM-DD:
    DATESTAMP_REGEX = re.compile('([12]\d\d\d)-([012345]\d)-([012345]\d)', flags = re.U)

    def __init__(self, template_definitions, blogname, blog_tag, about_blog, targetdir, blog_data,
                 generate, increment_version):
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

         ## create logger (see http://docs.python.org/2/howto/logging-cookbook.html)
        self.logging = logging.getLogger('lazyblorg.htmlizer')

        self.logging.debug("Htmlizer initiated with %s templ.def., %s blog_data, %s generate, %s increment" %
                           (str(len(template_definitions)), str(len(blog_data)), str(len(generate)),
                            str(len(increment_version))))

    def run(self):
        """
        Basic method that creates all the output.
        """

        for entry in self.blog_data:

            ## example entry:
            ## {'level': 2,
            ## 'timestamp': datetime.datetime(2013, 2, 14, 19, 2),
            ## 'tags': [u'blog', u'mytest', u'programming'],
            ## 'created': datetime.datetime(2013, 2, 12, 10, 58),
            ## 'finished-timestamp-history': [datetime.datetime(2013, 2, 14, 19, 2)],
            ## 'title': u'This is an example blog entry',
            ## 'id': u'2013-02-12-lazyblorg-example-entry',
            ## 'content': [['par', u'foo...'], [...]]
            ##  }

            entry = self.sanitize_and_htmlize_blog_content(entry)

            filename = htmlcontent = None

            if entry['category'] == self.TAGS:
                self.logging.debug("entry \"%s\" is a tag page" % entry['id'])
                self.logging.warn("generating tag pages not implemented yet")
                ## FIXXME: maybe: remove self.TAGS from list of tags?
                pass  ## FIXXME: generate tag blog entry

            elif entry['category'] == self.PERSISTENT:
                self.logging.debug("entry \"%s\" is a persistent page" % entry['id'])
                self.logging.warn("generating persistent pages not implemented yet")
                ## FIXXME: maybe: remove self.PERSISTENT from list of tags?
                pass  ## FIXXME: generate persistent blog entry

            elif entry['category'] == self.TEMPORAL:
                #pdb.set_trace()## FIXXME
                self.logging.debug("entry \"%s\" is an ordinary time-oriented blog entry" % entry['id'])
                htmlfilename, orgfilename, htmlcontent = self._create_time_oriented_blog_article(entry)

            elif entry['category'] == self.TEMPLATES:
                self.logging.debug("entry \"%s\" is the/a HTML template definition. Ignoring." % entry['id'])

            else:
                message = "entry [" + entry['id'] + "] has an unknown category [" + \
                    repr(entry['category']) + "]. Please check and fix before next run."
                self.logging.critical(message)
                raise HtmlizerException(message)

            if entry['category'] == self.TAGS or entry['category'] == self.PERSISTENT or entry['category'] == self.TEMPORAL:
                self.write_htmlcontent_to_file(htmlfilename, htmlcontent)
                self.write_orgcontent_to_file(orgfilename, entry['rawcontent'])
                
        entry_list_by_newest_timestamp = self.generate_entry_list_by_newest_timestamp()
        self.generate_entry_page(entry_list_by_newest_timestamp)

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
                'url':self._target_path_for_id_without_targetdir_and_prefixdir(entry['id']),
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

        for listentry in entry_list_by_newest_timestamp[0:self.NUMBER_OF_TEASER_ARTICLES]:

            entry = self.blog_data_with_id(listentry['id'])

            if entry['category'] == 'TEMPORAL':

                content = self.template_definition_by_name('article-preview-begin')
                assert('htmlteaser-equals-content' in entry.keys())

                if not entry['htmlteaser-equals-content']:
                    ## there is more in the article than in the teaser alone:
                    content += self.template_definition_by_name('article-preview-more')

                content += self.template_definition_by_name('article-preview-end')

                ## replacing keywords:
                
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
                content = content.replace('#ARTICLE-PUBLISHED-HTML-DATETIME#', iso_timestamp + self.TIME_ZONE_ADDON)
                content = content.replace('#ARTICLE-PUBLISHED-HUMAN-READABLE#', iso_timestamp)

                if entry['htmlteaser-equals-content']:
                    content = content.replace('#ARTICLE-TEASER#', '\n'.join(entry['content']))
                else:
                    content = content.replace('#ARTICLE-TEASER#', '\n'.join(entry['htmlteaser']))

                htmlcontent += content
                
            elif entry['category'] == 'PERSISTENT':
                pass ## FIXXME: implement!

            elif entry['category'] == 'TAGS':
                pass ## FIXXME: implement!

        ## add footer:
        htmlcontent += self.template_definition_by_name('entrypage-footer')
        
        htmlcontent = htmlcontent.replace('#ABOUT-BLOG#', self.sanitize_external_links(self.sanitize_html_characters(self.about_blog)))
        htmlcontent = htmlcontent.replace('#BLOGNAME#', self.sanitize_external_links(self.sanitize_html_characters(self.blogname)))
        self.write_htmlcontent_to_file(entry_page_filename, htmlcontent)
            
        return
        
    def write_htmlcontent_to_file(self, filename, htmlcontent):
        """
        Creates the file and writes the content of htmlcontent into it.

        @param filename: the name of the file to write to including path
        @param htmlcontent: the (UTF-8) string of the HTML content
        @param return: True if success
        """

        if filename and htmlcontent:
            with codecs.open(filename, 'wb', encoding='utf-8') as output:
                try:
                    output.write(htmlcontent)
                except:
                    self.logging.critical("Error when writing file: " + str(filename))
                    raise
                    return False
            return True
        else:
            self.logging.critical("No filename (" + str(filename) + ") or htmlcontent when writing file: " + str(filename))
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
                    return False
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

        teaser_finished = False  ## teaser is finished on first sub-heading or <hr>-element
        
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
                result = self.sanitize_external_links(result)
                result = self.htmlize_simple_text_formatting(result)
                result = self.fix_ampersands_in_url(result)
                template = self.template_definition_by_name('paragraph')
                result = template.replace('#PAR-CONTENT#', result)

            elif entry['content'][index][0] == 'hr':

                if not teaser_finished:
                    entry['htmlteaser'] = entry['content'][:index]
                    teaser_finished = True

                result="<div class=\"orgmode-hr\" />" ## FIXXME: <hr> is hardcoded here; add to templates?

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
                    content = self.sanitize_external_links(content)
                    content = self.htmlize_simple_text_formatting(result)
                    content = self.fix_ampersands_in_url(content)
                    content += self.template_definition_by_name('ul-item').replace('#CONTENT#', content)
                    result += content

                result += self.template_definition_by_name('ul-end')

            elif entry['content'][index][0] == 'html-block':

                ## example:
                ## ['html-block', u'my-HTML-example name', [u'    foo', u'bar', u'  <foo />', u'<a href="bar">baz</a>']]

                #import pdb; pdb.set_trace()
                if not entry['content'][index][1]:
                    ## if html-block has no name -> insert as raw HTML
                    result = '\n'.join(entry['content'][index][2])
                else:
                    ## if html-block has a name -> insert as html-source-code-example
                    result = self.template_definition_by_name('html-begin')
                    result = result.replace('#NAME#', entry['content'][index][1])
                    result += self.sanitize_html_characters(\
                        '\n'.join(entry['content'][index][2])).replace(' ', '&nbsp;').replace('\n', '<br />\n')
                    result += self.template_definition_by_name('html-end')

            elif entry['content'][index][0] == 'verse-block' or entry['content'][index][0] == 'example-block':

                ## example:
                ## ['verse-block', False, [u'first line', u'second line']]
                ## ['example-block', False, [u'first line', u'second line']]
                result = None

                result = self.template_definition_by_name('named-pre-begin')
                if entry['content'][index][1]:
                    result = self.template_definition_by_name('named-pre-begin')
                    result = result.replace('#NAME#', entry['content'][index][1])
                else:
                    result = self.template_definition_by_name('pre-begin')
                mycontent = '\n'.join(entry['content'][index][2])
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
                result += self.template_definition_by_name('blockquote-end')

            elif entry['content'][index][0] == 'src-block':

                ## example:
                ## ['src-block', False, [u'first line', u'second line']]

                ## FIXXME: replace pre with suitable source code environment!

                result = self.template_definition_by_name('html-begin')
                ## FIXXME: implement name for src blocks:
                #if entry['content'][index][1]:
                #    result = result.replace('#NAME#', entry['content'][index][1])
                result += self.sanitize_html_characters(\
                                                        '\n'.join(entry['content'][index][2])).replace(' ', '&nbsp;').replace('\n', '<br />\n')
                result += self.template_definition_by_name('html-end')

            else:
                message = "htmlizer.py/sanitize_and_htmlize_blog_content(): content element [" + str(entry['content'][index][0]) + \
                    "] of ID " + str(entry['id']) + " is not recognized (yet?)."
                self.logging.critical(message)
                raise HtmlizerException(message)

            ## replace element in entry with the result string:
            entry['content'][index] = result

        ## in case no sub-heading or <hr>-element was found: everything is the teaser:
        if not teaser_finished:
            entry['htmlteaser-equals-content'] = True
        else:
            entry['htmlteaser-equals-content'] = False

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

    def _create_time_oriented_blog_article(self, entry):
        """
        Creates a (normal) time-oriented blog article (in contrast to a permanent blog article).

        @param entry: blog entry data
        @param return: htmlfilename: string containing the file name of the HTML file
        @param return: orgfilename: string containing the file name of the Org-mode raw content file
        @param return: htmlcontent: the HTML content of the entry
        """

        path = self._create_target_path_for_id_with_targetdir_and_prefixdir(entry['id'])

        htmlfilename = os.path.join(path, "index.html")
        orgfilename = os.path.join(path, "source.org.txt")

        htmlcontent = u''

        ## replace-loop of all relevant strings and placeholder-strings
        ## article-header       | TITLE, ABOUT-BLOG, BLOGNAME, ARTICLE-(YEAR,MONTH,DAY,PUB*)     |
        ## article-header-begin | TITLE, ABOUT-BLOG, BLOGNAME, ARTICLE-(YEAR,MONTH,DAY,PUB*)     |
        ## article-tags-begin   | TITLE, ABOUT-BLOG, BLOGNAME, ARTICLE-(YEAR,MONTH,DAY,PUB*)     |
        ## article-tag          | TAGNAME                                                        |
        ## article-tags-end     | TITLE, ABOUT-BLOG, BLOGNAME, ARTICLE-(YEAR,MONTH,DAY,PUB*)     |
        ## article-header-end   | TITLE, ABOUT-BLOG, BLOGNAME, ARTICLE-(YEAR,MONTH,DAY,PUB*)     |
        ## content              | *                                                              |
        ## article-end          | TITLE, ABOUT-BLOG, BLOGNAME, ARTICLE-(YEAR,MONTH,DAY,PUB*)     |
        ## article-footer       | TITLE, ABOUT-BLOG, BLOGNAME, ARTICLE-(ID,YEAR,MONTH,DAY,PUB*)  |

        content = u''

        for articlepart in ['article-header', 'article-header-begin', 'article-tags-begin']:
            content += self.template_definition_by_name(articlepart)
        htmlcontent += self._replace_general_article_placeholders(entry, content)

        content = self._replace_tag_placeholders(entry['tags'], self.template_definition_by_name('article-tag'))
        htmlcontent += content

        content = u''
        for articlepart in ['article-tags-end', 'article-header-end']:
            content += self.template_definition_by_name(articlepart)
        htmlcontent += self._replace_general_article_placeholders(entry, content)

        for element in entry['content']:
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
                    self.logging.critical("Error in entry: " + str(entry['id']))
                    self.logging.critical("Element type: " + str(type(element)))
                    raise

        content = u''
        for articlepart in ['article-end', 'article-footer']:
            content += self.template_definition_by_name(articlepart)
        htmlcontent += self._replace_general_article_placeholders(entry, content)

        return htmlfilename, orgfilename, htmlcontent

    def _replace_tag_placeholders(self, tags, template_string):
        """
        Takes the list of tags and the template definition for tags
        and returns their concatenated string.

        The tag "blog" will be suppressed.

        @param tags: list of strings containing all tags of an entry
        @param template_string: string with placeholders instead of tag
        @param return: string with replaced placeholders
        """

        assert(type(tags) == list)
        assert(template_string)

        result = u''

        for tag in tags:
            if tag == self.blog_tag:
                continue
            else:
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
        - #ARTICLE-PUBLISHED-HTML-DATETIME#: time-stamp of publishing in HTML
          date-time format
        - #ARTICLE-PUBLISHED-HUMAN-READABLE#: time-stamp of publishing in

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
        content = content.replace('#ARTICLE-PUBLISHED-HTML-DATETIME#', iso_timestamp + self.TIME_ZONE_ADDON)
        content = content.replace('#ARTICLE-PUBLISHED-HUMAN-READABLE#', iso_timestamp)

        return content

    def _target_path_for_id_with_targetdir_and_prefixdir(self, entryid):
        """
        Returnes a directory path for a given blog ID such as:
        PERSISTENT: FIXXME
        TAGS: FIXXME
        TEMPORAL: "TARGETDIR/blog/2013/02/12/ID" from the oldest finished
        time-stamp.

        @param entryid: ID of a blog entry
        @param return: the resulting path as os.path string
        """

        entry = self.blog_data_with_id(entryid)

        if entry['category'] == self.TAGS:
            return ## FIXXME: implement!
        
        if entry['category'] == self.PERSISTENT:
            return ## FIXXME: implement!
        
        if entry['category'] == self.TEMPORAL:
            return os.path.join(self.targetdir, self._target_path_for_id_without_targetdir_and_prefixdir(entryid))

    def _target_path_for_id_without_targetdir_and_prefixdir(self, entryid):
        """
        Returnes a directory path for a given blog ID such as:
        PERSISTENT: FIXXME
        TAGS: FIXXME
        TEMPORAL: "2013/02/12/ID" from the oldest finished time-stamp.

        @param entryid: ID of a blog entry
        @param return: the resulting path as os.path string
        """

        entry = self.blog_data_with_id(entryid)

        if entry['category'] == self.TAGS:
            return ## FIXXME: implement!
        
        if entry['category'] == self.PERSISTENT:
            return ## FIXXME: implement!
        
        if entry['category'] == self.TEMPORAL:

            oldesttimestamp, year, month, day, hours, minutes = self._get_oldest_timestamp_for_entry(entry)

            folder = werkzeug.utils.secure_filename(entryid)

            if self.DATESTAMP_REGEX.match(folder[0:10]):
            ## folder contains any date-stamp in ISO format -> get rid of it (it's in the path anyway)
                folder = folder[11:]

            return os.path.join(year, month, day, folder)

    def _get_newest_timestamp_for_entry(self, entry):
        """
        Reads data of entry and returns datetime object of the newest
        time-stamp of the finished-timestamp-history.

        Example result: datetime.datetime(2013, 8, 29, 19, 40)

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

        Example result: datetime.datetime(2013, 8, 29, 19, 40)

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

        Example result: datetime.datetime(2013, 8, 29, 19, 40)

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
        assert(search_for == "OLDEST" or search_for == "NEWEST")
        assert('finished-timestamp-history' in entry.keys())

        returntimestamp = False
        if search_for == "OLDEST":
            oldesttimestamp = datetime.datetime.now()
            for timestamp in entry['finished-timestamp-history']:
                if timestamp < oldesttimestamp:
                    oldesttimestamp = timestamp
            returntimestamp = oldesttimestamp
        elif search_for == "NEWEST":
            newesttimestamp = datetime.datetime(1970,1,1)
            for timestamp in entry['finished-timestamp-history']:
                if timestamp > newesttimestamp:
                    newesttimestamp = timestamp
            returntimestamp = newesttimestamp
                
        return returntimestamp, str(returntimestamp.year).zfill(2), str(returntimestamp.month).zfill(2), \
            str(returntimestamp.day).zfill(2), \
            str(returntimestamp.hour).zfill(2), str(returntimestamp.minute).zfill(2)

    def _create_target_path_for_id_with_targetdir_and_prefixdir(self, entryid):
        """
        Creates a folder hierarchy for a given blog ID such as: TARGETDIR/blog/2013/02/12/ID

        @param entryid: ID of a blog entry
        @param return: path that was created
        """

        self.logging.debug("_create_target_path_for_id_with_targetdir_and_prefixdir(%s) called" % entryid)

        assert(os.path.isdir(self.targetdir))
        idpath = self._target_path_for_id_with_targetdir_and_prefixdir(entryid)

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
        return '\n'.join([x[2:][0] for x in self.template_definitions if x[1] == name][0])

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
                "\") did not find exactly one result (as expected): [" + str(matching_elements) + "]"
            self.logging.error(message)
            raise HtmlizerException(message)  ## FIXXME: maybe an Exception is too harsh here? (error-recovery?)


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
