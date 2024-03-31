# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2022-01-03 09:43:11 vk>

import config
import re
from os import path
import codecs  # open, close with Unicode
import logging
import datetime
from orgformat import *

# NOTE: pdb hides private variables as well. Please use:
# data = self._OrgParser__entry_data ; data['content']


class OrgParserException(Exception):
    """
    Exception for all kind of self-raised parsing errors
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class OrgParser(object):
    """
    Class for parsing Org-mode formatted files.

    Please note that this parser is a rather dumb one which parses
    only a sub-set of valid Org-mode syntax. If you are interested in
    more general parsers, you might take a look at
    http://orgmode.org/worg/org-tools/ instead.

    """

    LINE_SEPARATION_CHAR_WITHIN_PARAGRAPH = ' '

    # Finite State Machine: defining the states
    # NOTE: value of numbers are irrelevant - just make sure they are distinct
    SEARCHING_BLOG_HEADER = 'searching_blog_header'
    BLOG_HEADER = 'blog_header'
    ENTRY_CONTENT = 'entry_content'
    DRAWER_PROP = 'drawer_prop'
    DRAWER_LOGBOOK = 'drawer_logbook'
    IGNORED_DRAWER = 'ignored_drawer'
    BLOCK = 'block'
    LIST = 'list'
    TABLE = 'table'
    COLON_BLOCK = 'colon_block'
    SKIPPING_NOEXPORT_HEADING = 'skipping_noexport_heading'

    # asterisk(s), whitespace, word(s), optional followed by optional tags:
    HEADING_REGEX = re.compile(
        r'^(\*+|\#\+TITLE:)\s+((' + config.BLOG_FINISHED_STATE + r')\s+)?(.*?)(\s+(:\S+:)+)?\s*$')
        # r'^(\*+)\s+((' + config.BLOG_FINISHED_STATE + r')\s+)?(.*?)(\s+(:\S+:)+)?\s*$')
    # REGEX.match(string).group(INDEX)
    HEADING_STARS_IDX = 1
    HEADING_STATE_IDX = 3
    HEADING_TITLE_IDX = 4
    # components(HEADING_TAGS_IDX)[1:-1].split(':') -> array of tags
    HEADING_TAGS_IDX = 6

    DRAWER_REGEX = re.compile(r'^:[A-Z]+:$')

    CREATED_REGEX = re.compile(
        r'^:CREATED:\s+' +
        OrgFormat.SINGLE_ORGMODE_TIMESTAMP,
        re.IGNORECASE)
    CREATED_TIMESTAMP_IDX = 1

    LOG_REGEX = re.compile(
        r'^- State\s+"' +
        config.BLOG_FINISHED_STATE +
        r'"\s+from\s+("\S*"\s+)?([\[{].*[\]}])$',
        re.IGNORECASE)
    LOG_TIMESTAMP_IDX = 2

    SUPPORTED_BLOCK_TYPES_UPPERCASE = [
        'SRC',
        'EXPORT',
        'EXAMPLE',
        'VERSE',
        'QUOTE',
        'CENTER',
        'HTML',
        'ASCII',
        'LATEX']
    # Note: for 'EXPORT' look into block_type_export_backend which holds:
    # (HTML|LATEX)
    SUPPORTED_EXPORT_BLOCK_BACKENDS = ['HTML', 'LATEX']

    BLOCK_REGEX = re.compile(
        r'^#\+BEGIN_(' +
        r'|'.join(SUPPORTED_BLOCK_TYPES_UPPERCASE) +
        r')(\s+(.*))?$',
        re.IGNORECASE)
    BLOCK_TYPE_IDX = 1
    BLOCK_LANGUAGE_IDX = 3

    # matching five dashes (or more) which resembles an horizontal rule:
    # http://orgmode.org/org.html#Horizontal-rules
    HR_REGEX = re.compile(r'^-{5,}\s*$')

    # matching list items
    LIST_ITEM_REGEX = re.compile(
        r'^(\s*)([\\+\\*-]|(\d+[\.\\)])) (\[.\])?(.+)$',
        re.IGNORECASE)
    # >>> re.match(r'^(\s*)([\\+\\*-]|(\d+[\.\\)])) (\[.\])?(.+)$', u"  - [-] foo bar").groups()
    # (u'  ', u'-', None, u'[-]', u' foo bar')
    # >>> re.match(r'^(\s*)([\\+\\*-]|(\d+[\.\\)])) (\[.\])?(.+)$', u"  - [ ] foo bar").groups()
    # (u'  ', u'-', None, u'[ ]', u' foo bar')
    # >>> re.match(r'^(\s*)([\\+\\*-]|(\d+[\.\\)])) (\[.\])?(.+)$', u"  + [X] foo bar").groups()
    # (u'  ', u'+', None, u'[X]', u' foo bar')
    # >>> re.match(r'^(\s*)([\\+\\*-]|(\d+[\.\\)])) (\[.\])?(.+)$', u"  * foo bar").groups()
    # (u'  ', u'*', None, None, u'foo bar')
    # >>> re.match(r'^(\s*)([\\+\\*-]|(\d+[\.\\)])) (\[.\])?(.+)$', u"  23. [-] foo bar").groups()
    # (u'  ', u'23.', u'23.', u'[-]', u' foo bar')
    # >>> re.match(r'^(\s*)([\\+\\*-]|(\d+[\.\\)])) (\[.\])?(.+)$', u"  42) foo bar").groups()
    # (u'  ', u'42)', u'42)', None, u'foo bar')

    # example: '#+ATTR_HTML: :alt An alternative description image :title This is my title! :align right :width 300'
    # results in: FIXXME
    ATTR_HTML_REGEX = re.compile(r':([\w-]+)\s+([^:]+)')

    # re.match(r'^\[\[tsfile:(.+\.(png|jpg|jpeg|svg|gif))+(\]\[(.+))?\]\]$', '[[tsfile:2014-01-29 foo bar.PNG][foo bar]]', re.IGNORECASE).groups()
    #   ('2014-01-29 foo bar.PNG', 'PNG', '][foo bar', 'foo bar')
    # re.match(r'^\[\[tsfile:(.+\.(png|jpg|jpeg|svg|gif))+(\]\[(.+))?\]\]$', '[[tsfile:2014-01-29 foo bar.PNG]]', re.IGNORECASE).groups()
    #   ('2014-01-29 foo bar.PNG', 'PNG', None, None)
    CUST_LINK_IMAGE_REGEX = re.compile(r'^\[\[tsfile:([^\]]+\.(png|jpg|jpeg|svg|gif))+(\]\[(.+))?\]\]$')
    CUST_LINK_IMAGE_FILENAME_IDX = 1
    CUST_LINK_IMAGE_DESCRIPTION_IDX = 4
    
    __filename = ''

    # for description please visit: lazyblog.org > Notes > Representation of
    # blog data
    __blog_data = []
    # __blog_data: contains a list with elements of type __entry_data

    __entry_data = {}  # dict of currently parsed blog entry data: gets "filled"
    # while parsing the entry

    
    # set checking for link definitions to strict: any re-definition will raise
    # a critical error
    global LINKDEFS_STRICT_CHECKING
    LINKDEFS_STRICT_CHECKING = False
    
    def __init__(self, filename):
        """
        This function handles the communication with the parser object and returns the blog data.

        @param filename: string containing one file name
        """

        assert filename.__class__ == str
        assert path.isfile(filename)
        self.__filename = filename
        self.__blog_data = []
        self.__entry_data = {}

        # create logger (see
        # http://docs.python.org/2/howto/logging-cookbook.html)
        self.logging = logging.getLogger('lazyblorg.OrgParser')

    def __check_if_entry_is_OK(self, check_only_title=False):
        """
        Return True if current entry from "self.__entry_data" is a valid and
        complete blog article and thus can be added to the blog data.

        @param check_only_title: if True, check only title, level, and tags
        @param return: True if OK or False if not OK (and entry has to be skipped)
        """

        self.logging.debug(
            "OrgParser: check_entry_data: checking current entry ...")
        errors = 0

        if 'level' not in list(self.__entry_data.keys()):
            self.logging.error("Heading does not contain a heading level")
            errors += 1

        if 'title' not in list(self.__entry_data.keys()):
            self.logging.error("Heading does not contain a title")
            errors += 1

        if not check_only_title:

            if 'id' not in list(self.__entry_data.keys()):
                self.logging.error(
                    "Heading does not contain any ID within PROPERTY drawer")
                errors += 1
            else:
                self.logging.debug(
                    "OrgParser: checking id [%s]" %
                    self.__entry_data['id'])

            if 'latestupdateTS' not in list(self.__entry_data.keys()):
                self.logging.error(
                    "Heading does not contain a latest update timestamp")
                errors += 1
            else:
                if not type(self.__entry_data['latestupdateTS'] == datetime.datetime):
                    self.logging.error(
                        "Latest update timestamp is not of type datetime.datetime")
                    errors += 1

            if 'firstpublishTS' not in list(self.__entry_data.keys()):
                self.logging.error(
                    "Heading does not contain a first published timestamp")
                errors += 1
            else:
                if not type(self.__entry_data['firstpublishTS'] == datetime.datetime):
                    self.logging.error(
                        "First published timestamp is not of type datetime.datetime")
                    errors += 1

            if 'created' not in list(self.__entry_data.keys()):
                self.logging.error(
                    "Heading does not contain a timestamp for created")
                errors += 1

            if 'content' in list(self.__entry_data.keys()):
                if len(self.__entry_data['content']) < 1:
                    self.logging.error(
                        "Heading does not contain a filled content")
                    errors += 1
            else:
                self.logging.error("Heading does not contain a content")
                errors += 1

        if errors > 0:
            self.logging.error("check_entry_data: " + str(errors) +
                               " not matching criteria found for heading \"" +
                               self.__entry_data['title'] + "\" in file \"" +
                               self.__filename + "\". I ignore this entry.")
            return False
        else:
            self.logging.debug(
                "OrgParser: check_entry_data: current entry has been checked positively for being added to the blog data")
            return True

    def __handle_heading_and_check_if_it_is_blog_heading(
            self, stars, title, tags):
        """
        Handles a heading line of a blog entry.

        Returns False if heading does not fulfill some lazyblorg requirements:
        - no TAG_FOR_BLOG_ENTRY
        - has NOEXPORT tag

        Following blog data entry fields are being set:
        - title
        - level
        - lbtags
        - usertags

        @param stars: string containing the heading asterisks
        @param title: string containing description of heading line
        @param tags: string containing raw tags like ":tag1:tag2:"
        @param blog_data: data representation of the blog data parsed so far
        @param return: True if it is a blog heading; false if not
        """

        assert stars.__class__ == str
        assert title.__class__ == str

        if not tags:
            # not even the TAG_FOR_BLOG_ENTRY -> no blog article!
            return False

        assert tags.__class__ == str

        self.__entry_data['title'] = title
        self.__entry_data['level'] = len(stars)
        self.__entry_data['lbtags'] = []
        self.__entry_data['usertags'] = []

        # ignore headings with noexport tag:
        if ":NOEXPORT:" in tags.upper():
            return False

        # ignore headings with no TAG_FOR_BLOG_ENTRY
        if not ":" + config.TAG_FOR_BLOG_ENTRY + ":" in tags.lower():
            return False

        rawtags = tags[1:-1].replace('::', ':').split(':')
        for rawtag in rawtags:
            # separate lbtags from usertags:
            if rawtag.lower() == config.TAG_FOR_TAG_ENTRY or rawtag.lower() == config.TAG_FOR_PERSISTENT_ENTRY or \
               rawtag.lower() == config.TAG_FOR_TEMPLATES_ENTRY or rawtag.lower() == config.TAG_FOR_BLOG_ENTRY:
                # FIXXME: probably omit config.TAG_FOR_BLOG_ENTRY here?
                # FIXXME: at least make sure that it does not get added to
                # usertags!
                self.__entry_data['lbtags'].append(rawtag.lower())
            else:
                self.__entry_data['usertags'].append(rawtag)

        self.logging.debug(
            "OrgParser: heading: level[%s] title[%s] usertags[%s]" %
            (str(
                self.__entry_data['level']), self.__entry_data['title'], str(
                self.__entry_data['usertags'])))

        return self.__check_if_entry_is_OK(check_only_title=True)

    def __handle_blog_end(self, line, rawcontent):
        """
        Handles the end of the current blog entry.

        @param line: string containing current parsed line
        @param rawcontent: string containing the raw Org-mode source of the current blog entry
        @param return: ID of next state
        """

        self.logging.debug("OrgParser: end of blog entry; checking entry ...")
        if self.__check_if_entry_is_OK():

            # debug with: self._OrgParser__entry_data['usertags']
            # debug with: self._OrgParser__blog_data

            # FIXXME: adding as list entry

            if config.TAG_FOR_TEMPLATES_ENTRY in self.__entry_data['lbtags']:
                self.logging.debug(
                    "OrgParser: check OK; appending blog category TEMPLATES ...")
                self.__entry_data['category'] = config.TEMPLATES
            elif config.TAG_FOR_TAG_ENTRY in self.__entry_data['lbtags']:
                self.logging.debug(
                    "OrgParser: check OK; appending blog category TAGS ...")
                self.__entry_data['category'] = config.TAGS
            elif config.TAG_FOR_PERSISTENT_ENTRY in self.__entry_data['lbtags']:
                self.logging.debug(
                    "OrgParser: check OK; appending to blog category PERSISTENT ...")
                self.__entry_data['category'] = config.PERSISTENT
            else:
                self.logging.debug(
                    "OrgParser: check OK; appending to blog category TEMPORAL ...")
                self.__entry_data['category'] = config.TEMPORAL

            # adding the Org-mode source:
            self.__entry_data['rawcontent'] = rawcontent

            # debug with: self._OrgParser__entry_data
            self.__blog_data.append(self.__entry_data)

        self.__entry_data = {}  # empty current entry data
        # Pdb-debugging with, e.g., self._OrgParser__entry_data['content']

        # is newly found heading a new blog entry?
        heading_components = self.HEADING_REGEX.match(line)
        if heading_components and heading_components.group(
                self.HEADING_STATE_IDX) == config.BLOG_FINISHED_STATE:
            self.logging.debug(
                "OrgParser: found heading (directly after previous blog entry)")

            if self.__handle_heading_and_check_if_it_is_blog_heading(
                heading_components.group(
                    self.HEADING_STARS_IDX), heading_components.group(
                    self.HEADING_TITLE_IDX), heading_components.group(
                    self.HEADING_TAGS_IDX)):
                return self.BLOG_HEADER
            else:
                self.__entry_data = {}  # empty the current entry data for the upcoming entry
                return self.SEARCHING_BLOG_HEADER

        else:
            return self.SEARCHING_BLOG_HEADER

    def _get_list_indentation_number(self, list_item):
        """
        Returns the number of characters of the indentation of a list item.

        @param list_item: string holding the list item to check
        @param return: integer holding the indentation level. 0 means no list.
        """

        assert(type(list_item) == str)

        list_item_components = self.LIST_ITEM_REGEX.match(list_item)
        if list_item_components:
            # return length of leading spaces, length of bullet length, plus 1
            # for space at end:
            return len(list_item_components.group(1)) + \
                len(list_item_components.group(2)) + 1
        else:
            # list_item has no bullet point - might be follow-up line of an item:
            # return number of leading spaces:
            return len(list_item) - len(list_item.lstrip(' '))

    def check_link_definition_against_dictionary(self, linkdefs, tag, url):
        # Check if the tag is already defined in linkdefs
        if tag in linkdefs:
            linkdef = linkdefs[tag]
            if LINKDEFS_STRICT_CHECKING:
                message=(f"OrgParser: Aborting because tag "
                         f"value for {tag} is re-defined and strict checking "
                         f"is enabled. \nNew assignment: {url}\nPrevious "
                         f"assignment: {linkdef}")
                self.logging.critical(message)
                raise OrgParserException(message)
            else:
                self.logging.debug(f"OrgParser: Warning! Tag {tag} "
                                   "already defined in url dictionary.")
                
            # Compare the existing value to the new value
            if linkdef != url:
                message=(f"OrgParser: Aborting because tag "
                         f"value for {tag} re-defined differently from the "
                         f"previous value. \nNew assignment: {url}\nPrevious "
                         f"assignment: {linkdef}")
                self.logging.critical(message)
                raise OrgParserException(message)

    def parse_orgmode_file(self):
        """
        Parses the Org-mode file.

        @param return: array containing parsed Org-mode data
        @param return: integer with number of lines parsed
        """

        self.logging.debug(
            "OrgParser: doing file \"%s\" ..." %
            self.__filename)
        stats_parsed_org_lines = 0

        # finite state machine:
        # SEARCHING_BLOG_HEADER | BLOG_HEADER | ENTRY_CONTENT | ...
        # ... DRAWER_PROP | DRAWER_LOGBOOK | BLOCK | LIST | TABLE | COLON_BLOCK | ..
        # ... SKIPPING_NOEXPORT_HEADING
        state = self.SEARCHING_BLOG_HEADER

        # type of last/current block found
        block_type = None  # one of: SUPPORTED_BLOCK_TYPES_UPPERCASE
        block_type_export_backend = None  # one of SUPPORTED_EXPORT_BLOCK_BACKENDS

        # name of the previous element with a name defined; emptied with any empty line
        # example: "#+NAME: foo bar" -> previous_name = u'foo bar'
        previous_name = ''

        # contains content of previous line
        # NOTE: only valid as long a state does not use "continue" in the previous
        # parsing step without "previous_line = line"
        previous_line = ''

        # contains the previous caption line; emptied with any empty line
        # example:
        # #+CAPTION: A black cat stalking a spider
        # previous_caption = u'A black cat stalking a spider'
        previous_caption = ''

        # contains the content of the previous ATTR_HTML lines; emptied with any empty line
        # example:
        # #+ATTR_HTML: :alt cat/spider image :title Action! :align right :width 300
        # attr_html_list = {'alt': "cat/spider", 'title': "Action!", 'align': "right" , 'width': "300"}
        attr_html_dict = {}

        # if skipping a heading within an entry, this variable holds
        # the level of heading of the noexport-heading:
        noexport_level = False

        # collect the lines of the raw Org-mode entry (without
        # noexport-headings):
        rawcontent = ""
        ignore_line_for_rawcontent = True
        line = ''

        for rawline in codecs.open(self.__filename, 'r', encoding='utf-8'):

            if not ignore_line_for_rawcontent:
                # first blog header is lost if file starts directly with it: is
                # fixed below
                rawcontent += line + '\n'
            ignore_line_for_rawcontent = False

            line = rawline.rstrip()  # remove trailing whitespace

            # Create a 'linkdefs' dictionary entry for link definitions
            if line.upper().startswith('#+LINK:'):
                link_definition = line[7:].strip()
                tag, url = link_definition.split(None, 1)
                url = url.strip('"')

                # Ensure 'linkdefs' key exists in __entry_data and initialize if it doesn't
                linkdefs = self.__entry_data.setdefault('linkdefs', {})

                # check if link definitions are consistent
                self.check_link_definition_against_dictionary(linkdefs,
                                                              tag,
                                                              url)

                linkdefs[tag]=url
                self.logging.debug(
                    f"OrgParser: define url dictionary tag {tag} for URL {url}")
                previous_line = line
            
            if not state == self.SEARCHING_BLOG_HEADER:  ## limit the output to interesting lines
                self.logging.debug(
                    "OrgParser: ------------------------------- %s" %
                    state)
                self.logging.debug(
                    "OrgParser: %s ###### line: \"%s\"" %
                    (state, line))
            stats_parsed_org_lines += 1  # increment statistical counter variable

            list_item_components = self.LIST_ITEM_REGEX.match(line)

            if state == self.SKIPPING_NOEXPORT_HEADING:

                # ignore until end of blog entry  OR
                # ignore until next heading on same level  OR
                # ignore until next heading on higher level
                components = self.HEADING_REGEX.match(line)

                # next heading: if level same or higher: set status to
                # self.ENTRY_CONTENT
                if components:
                    if len(
                        components.group(
                            self.HEADING_STARS_IDX)) <= noexport_level:
                        state = self.ENTRY_CONTENT
                        # keep current line and continue parsing normally
                    else:
                        # ignore heading because it is a sub-heading of the
                        # noexport heading
                        ignore_line_for_rawcontent = True
                        continue
                else:
                    # ignore line because it is no heading at all
                    ignore_line_for_rawcontent = True
                    continue

            if state == self.SEARCHING_BLOG_HEADER:

                # search for header line of a blog entry -> BLOG_HEADER

                components = self.HEADING_REGEX.match(line)

                # NOTE: this following section is a pre-filter that
                # is looking for blog-like headings. All other
                # headings are ignored by this parser. If you want to
                # use my parser as a general Org-mode parser, you
                # have to modify at least this part.

                if components and components.group(
                        self.HEADING_STATE_IDX) == config.BLOG_FINISHED_STATE:

                    if self.__handle_heading_and_check_if_it_is_blog_heading(
                        components.group(
                            self.HEADING_STARS_IDX), components.group(
                            self.HEADING_TITLE_IDX), components.group(
                            self.HEADING_TAGS_IDX)):
                        state = self.BLOG_HEADER
                        previous_line = line
                        if ignore_line_for_rawcontent:
                            # if it is first line, save current heading to
                            # rawcontent:
                            # fixes: first blog header is lost if file starts
                            # directly with it
                            rawcontent += line + '\n'
                        continue
                    else:
                        self.__entry_data = {}  # empty current entry data
                        previous_line = line
                        ignore_line_for_rawcontent = True
                        continue

                else:
                    ## self.logging.debug(
                    ##     "OrgParser: line is not of any interest, skipping.")
                    ignore_line_for_rawcontent = True
                    previous_line = line
                    continue

            elif state == self.BLOG_HEADER:

                # after header found: search for drawers (DRAWER_*) until content -> ENTRY_CONTENT
                # NOTE: yes, content between header and drawers is
                # ignored/lost.

                drawer_matches = self.DRAWER_REGEX.match(line)
                if drawer_matches:
                    if line.upper() == ':PROPERTIES:':
                        self.logging.debug("OrgParser: found PROPERTIES drawer")
                        state = self.DRAWER_PROP
                        previous_line = line
                        continue
                    elif line.upper() == ':LOGBOOK:':
                        self.logging.debug("OrgParser: found LOGBOOK drawer")
                        state = self.DRAWER_LOGBOOK
                        previous_line = line
                        continue
                    else:
                        ## DRAWER_REGEX is matching, not handled by pevious ifs: parse this drawer but ignore it

                        ## Note: as long as there is no ignored drawer
                        ## before PROPERTIES or LOGBOOK, this is dead
                        ## code because usually, this is only matched
                        ## when being in self.ENTRY_CONTENT status and
                        ## not self.BLOG_HEADER like here. I keep it
                        ## here just in case when there is a LINKS
                        ## drawer (or similar) before any
                        ## PROPERTIES/LOGBOOK drawer.

                        self.logging.debug("OrgParser: found a drawer to ignore")
                        state = self.IGNORED_DRAWER
                        ignore_line_for_rawcontent = True
                        continue

            elif state == self.ENTRY_CONTENT:

                # default/main state: parse entry content and look out for
                # content that has got its own state

                if 'content' not in list(self.__entry_data.keys()):
                    # append empty content list to __entry_data
                    self.__entry_data['content'] = []

                heading_components = self.HEADING_REGEX.match(line)
                hr_components = self.HR_REGEX.match(line)
                cust_link_image_components = self.CUST_LINK_IMAGE_REGEX.match(line)
                drawer_matches = self.DRAWER_REGEX.match(line)

                if line.upper() == ':PROPERTIES:':
                    self.logging.debug("OrgParser: found PROPERTIES drawer")
                    state = self.DRAWER_PROP
                    previous_line = line
                    continue

                elif line.upper() == ':LOGBOOK:':
                    self.logging.debug("OrgParser: found LOGBOOK drawer")
                    state = self.DRAWER_LOGBOOK
                    previous_line = line
                    continue

                elif drawer_matches:
                    self.logging.debug("OrgParser: found a drawer to ignore")
                    state = self.IGNORED_DRAWER
                    ignore_line_for_rawcontent = True
                    continue

                elif hr_components:
                    self.__entry_data['content'].append(['hr'])
                    previous_line = line
                    continue

                elif line == '':
                    self.logging.debug("OrgParser: found empty line")
                    # clear things that are only valid until empty line after element
                    previous_name = ''
                    previous_caption = ''
                    attr_html_dict = {}
                    # if len(self.__entry_data['content']) > 1:
                    #    if not self.__entry_data['content'][-1] == u'\n':
                    #        ## append newline to content (only if previous content is not a newline)
                    #        self.__entry_data['content'].append(u'\n')
                    previous_line = line
                    continue

                elif line.upper().startswith('#+NAME: '):
                    previous_name = line[8:].strip()
                    self.logging.debug(
                        "OrgParser: found #+NAME: [%s]" %
                        previous_name)
                    previous_line = line
                    continue

                elif line.upper().startswith('#+BEGIN_'):

                    block_components = self.BLOCK_REGEX.match(line)
                    if not block_components:
                        raise OrgParserException(
                            'I found a line beginning with ' +
                            '\"#+BEGIN_\" that was not matched by BLOCK_REGEX which ' +
                            'is quite a pity. line: ' +
                            str(line))
                    block_type = str(
                        block_components.group(
                            self.BLOCK_TYPE_IDX)).upper()

                    self.logging.debug(
                        "OrgParser: found block signature for " + block_type)

                    # NOTE: block_type LATEX and HTML are obsolete with Org-mode v9: "#+BEGIN_(HTML|LATEX)"
                    #       Got changed to "#+BEGIN_EXPORT (html|latex)"
                    # However, I keep handling both of them here for a while.
                    if block_type in self.SUPPORTED_BLOCK_TYPES_UPPERCASE:

                        # handling of EXPORT block (new with Org-mode 9: see
                        # above)
                        if block_type == 'EXPORT':
                            block_type_export_backend = str(
                                block_components.group(self.BLOCK_LANGUAGE_IDX)).upper()
                            if block_type_export_backend not in self.SUPPORTED_EXPORT_BLOCK_BACKENDS:
                                raise OrgParserException(
                                    'I found an EXPORT block \"' +
                                    str(line) +
                                    '\" which has a non supported backend parameter (currently' +
                                    ' supported here: ' +
                                    ', '.join(
                                        self.SUPPORTED_EXPORT_BLOCK_BACKENDS) +
                                    '). Please fix it.')
                            else:
                                self.logging.debug(
                                    "OrgParser: found EXPORT block signature for " +
                                    block_type_export_backend)
                            if previous_name == '':
                                self.__entry_data['content'].append(
                                    [block_type_export_backend.lower() + '-block', False, []])
                            else:
                                self.logging.debug(
                                    "OrgParser: this block is a named one: [%s]" %
                                    previous_name)
                                self.__entry_data['content'].append(
                                    [block_type_export_backend.lower() + '-block', previous_name, []])
                        else:
                            if previous_name == '':
                                self.__entry_data['content'].append(
                                    [block_type.lower() + '-block', False, []])
                            else:
                                self.logging.debug(
                                    "OrgParser: this block is a named one: [%s]" %
                                    previous_name)
                                self.__entry_data['content'].append(
                                    [block_type.lower() + '-block', previous_name, []])
                    else:
                        # if BLOCK_REGEX is in sync with the if-statement
                        # above, this should never be reached!
                        raise OrgParserException(
                            'I found a block type \"' +
                            str(line) +
                            '\" that is not known. Please do not confuse me and fix it.')
                    state = self.BLOCK
                    previous_line = line
                    continue

                elif line.startswith(': '):

                    self.logging.debug("OrgParser: found COLON_BLOCK")
                    state = self.COLON_BLOCK
                    self.__entry_data['content'].append(
                        ['colon-block', False, [line]])
                    previous_line = line

                elif line.startswith('# '):

                    # http://orgmode.org/manual/Comment-lines.html
                    self.logging.debug(
                        "OrgParser: found comment line, ignoring it")
                    continue

                elif line.startswith('|'):

                    self.logging.debug("OrgParser: found TABLE")
                    state = self.TABLE
                    if previous_name == '':
                        self.__entry_data['content'].append(
                            ['table', False, [line]])
                    else:
                        self.__entry_data['content'].append(
                            ['table', previous_name, [line]])
                    previous_line = line

                elif line.upper().startswith('#+CAPTION: '):
                    previous_caption = line[11:].strip()

                elif line.upper().startswith('#+ATTR_HTML: '):
                    matches = re.findall(self.ATTR_HTML_REGEX, line)
                    if matches:
                        # lower-case the keys and remove trailing spaces from the parameters
                        matches = [(x.lower(), y.strip()) for x, y in matches]
                        for match in matches:
                            key = match[0]
                            value = match[1]
                            attr_html_dict[key] = value

                elif cust_link_image_components:
                    # parses lines like: [[tsfile:2014-01-29 foo bar.png]]
                    # parses lines like: [[tsfile:2014-01-29 foo bar.png][foo bar]]
                    filename = cust_link_image_components.group(self.CUST_LINK_IMAGE_FILENAME_IDX)
                    description = cust_link_image_components.group(self.CUST_LINK_IMAGE_DESCRIPTION_IDX)
                    self.logging.debug(
                        "OrgParser: adding a customized image link file[%s], description[%s], caption[%s], attr[%s]" %
                        (str(filename), str(description), str(previous_caption), str(attr_html_dict)))
                    if description and description.lower().startswith('https://'):
                        # if description is an URL and linked-image-width is not 'none', this is a contradiction (since both would result in an img href link)
                        if 'linked-image-width' in attr_html_dict.keys() and attr_html_dict['linked-image-width'].lower() != 'none':
                            message = 'image with URL as description ("' + description + \
                                '"; which will result in a href link) used an linked-image-width parameter value which is not none ("' + \
                                str(attr_html_dict['linked-image-width']) + '") which would also result in a href link. Please do remove one of them.'
                            self.logging.critical(message)
                            raise OrgParserException(message)
                    self.__entry_data['content'].append(['cust_link_image', filename, description, previous_caption, attr_html_dict])

                elif heading_components:
                    self.logging.debug("OrgParser: found new heading")
                    level = len(
                        heading_components.group(
                            self.HEADING_STARS_IDX))

                    if heading_components.group(self.HEADING_TAGS_IDX):
                        # there are tags
                        if "NOEXPORT" in heading_components.group(
                                self.HEADING_TAGS_IDX).upper():
                            self.logging.debug(
                                "OrgParser: new heading has NOEXPORT tag, skipping.")
                            state = self.SKIPPING_NOEXPORT_HEADING
                            noexport_level = level
                            previous_line = line  # maybe this is not needed
                            ignore_line_for_rawcontent = True
                            continue

                    if level <= self.__entry_data['level']:
                        # level is same or higher as main heading of blog
                        # entry: end of blog entry
                        state = self.__handle_blog_end(line, rawcontent)
                        rawcontent = ""
                        previous_line = line
                        ignore_line_for_rawcontent = True
                        continue
                    else:
                        # sub-heading of entry
                        title = heading_components.group(
                            self.HEADING_TITLE_IDX)
                        self.logging.debug(
                            "OrgParser: inserting new sub-heading")
                        self.__entry_data['content'].append(
                            ['heading', {'level': level, 'title': title}])

                elif list_item_components:

                    self.logging.debug("OrgParser: found LIST_ITEM")
                    state = self.LIST
                    try:
                        if len(self.__entry_data['content']) > 0 and self.__entry_data['content'][-1][0] == 'list':
                            # append to the previous list:
                            # previous line was empty
                            self.__entry_data['content'][-1][-1].append('\n')
                            self.__entry_data['content'][-1][-1].append(line)
                        else:
                            # create a new list:
                            self.__entry_data['content'].append(['list', [line]])
                    except IndexError:
                        self.logging.error('internal error while processing list item in line [%s]' % line)
                        raise
                    previous_line = line

                # FIXXME: add more elif line == ELEMENT

                else:
                    if len(self.__entry_data['content']) > 0:
                        if previous_line != '' and self.__entry_data[
                                'content'][-1][0] == 'par':
                            # concatenate this line with previous if it is
                            # still generic content within a paragraph
                            self.logging.debug(
                                "OrgParser: adding line as generic content to current paragraph")
                            self.__entry_data['content'][-1][1] += \
                                self.LINE_SEPARATION_CHAR_WITHIN_PARAGRAPH + line.strip()
                            previous_line = line
                            continue

                    self.logging.debug(
                        "OrgParser: adding line as new generic content paragraph")
                    self.__entry_data['content'].append(['par', line])
                    previous_line = line
                    continue

            elif state == self.DRAWER_PROP:

                # parse properties for ID and CREATED and return to
                # ENTRY_CONTENT

                if line.upper() == ':END:':
                    self.logging.debug("OrgParser: end of drawer")
                    state = self.ENTRY_CONTENT
                    previous_line = line
                    continue

                if 'id' in list(self.__entry_data.keys()) and 'created' in list(self.__entry_data.keys()):
                    # if all properties already found, ignore rest of
                    # PROPERTIES and all other PROPERTIES (of sub-headings)
                    self.logging.debug(
                        "OrgParser: ignoring PROPERTIES since I already got my ID and CREATED")
                    previous_line = line
                    # OK, here I omit some unimportant properties others might
                    # want to see
                    ignore_line_for_rawcontent = True
                    continue

                if line.upper().startswith(':ID:'):
                    self.__entry_data['id'] = line[4:].strip().replace(' ', '')

                if line.upper().startswith(':CREATED:'):
                    try:
                        datetimestamp = OrgFormat.orgmode_timestamp_to_datetime(
                            self.CREATED_REGEX.match(line).group(self.CREATED_TIMESTAMP_IDX)
                        )
                        self.__entry_data['created'] = datetimestamp
                    except Exception as inst:
                        self.logging.error(
                            "%s ... in line \"%s\"" %
                            (str(inst), line))
                        self.logging.error(
                            "Probably malformed time-stamp entry.")
                        raise

                else:
                    previous_line = line
                    continue

            elif state == self.DRAWER_LOGBOOK:

                # parse logbook entries for state changes to
                # config.BLOG_FINISHED_STATE and return to ENTRY_CONTENT

                if line.upper() == ':END:':
                    self.logging.debug("OrgParser: end of drawer")
                    state = self.ENTRY_CONTENT
                    previous_line = line
                    continue

                components = self.LOG_REGEX.match(line)
                if components:

                    # extract time-stamp as datetime
                    datetimestamp = OrgFormat.orgmode_timestamp_to_datetime(
                        components.group(self.LOG_TIMESTAMP_IDX))

                    # add to finished-timestamp-history
                    if 'finished-timestamp-history' in list(self.__entry_data.keys()):
                        self.__entry_data[
                            'finished-timestamp-history'].append(datetimestamp)
                    else:
                        self.__entry_data[
                            'finished-timestamp-history'] = [datetimestamp]

                    # (over)write latestupdateTS of blogentry if
                    # current datetimestamp is newer:
                    if 'latestupdateTS' in list(self.__entry_data.keys()):
                        if datetimestamp > self.__entry_data['latestupdateTS']:
                            self.__entry_data['latestupdateTS'] = datetimestamp
                    else:
                        self.__entry_data['latestupdateTS'] = datetimestamp

                    # (over)write firstpublishTS of blogentry if
                    # current datetimestamp is older:
                    if 'firstpublishTS' in list(self.__entry_data.keys()):
                        if datetimestamp < self.__entry_data['firstpublishTS']:
                            self.__entry_data['firstpublishTS'] = datetimestamp
                    else:
                        self.__entry_data['firstpublishTS'] = datetimestamp

                previous_line = line
                continue

            elif state == self.IGNORED_DRAWER:

                # parse ignored drawer, omit in rawcontent

                if line.upper() == ':END:':
                    self.logging.debug("OrgParser: end of drawer")
                    state = self.ENTRY_CONTENT
                    ignore_line_for_rawcontent = True
                    continue
                else:
                    ignore_line_for_rawcontent = True
                    continue

            elif state == self.BLOCK:

                # parses general blocks and return to ENTRY_CONTENT

                if not block_type:
                    raise OrgParserException(
                        'I was in state \"BLOCK\" with no block_type. Not good, I\'m confused!')

                if line.upper() == '#+END_' + block_type:

                    state = self.ENTRY_CONTENT
                    previous_line = line
                    block_type = None
                    block_type_export_backend = None
                    continue
                else:
                    if block_type in self.SUPPORTED_BLOCK_TYPES_UPPERCASE:
                        # append to the last element of content (which is a list from the current block) to
                        # its last element (which contains the list of the
                        # block content):
                        self.__entry_data['content'][-1][-1].append(line)
                    else:
                        # if BLOCK_REGEX is in sync with the if-statement
                        # above, this should never be reached!
                        raise OrgParserException(
                            'I found a block type \"' +
                            str(line) +
                            '\" that is not known. Please do not confuse me and fix it.')

            elif state == self.LIST:

                # parses simple lists and return to ENTRY_CONTENT

                # >>> re.match(r'^(\s*)([\\+\\*-]|(\d+[\.\\)])) (\[.\])?(.+)$', u"  - [-] foo bar").groups()
                # (u'  ', u'-', None, u'[-]', u' foo bar')

                if line == '':
                    # list is over now: (if it is only an empty line in between
                    # two list items, catch this in entry content state)
                    state = self.ENTRY_CONTENT
                    previous_line = line
                    continue
                elif list_item_components:
                    # append to the last element of content (which is a list from the current block) to
                    # its last element (which contains the list of the block
                    # content):
                    self.__entry_data['content'][-1][-1].append(line)
                elif self._get_list_indentation_number(line) == self._get_list_indentation_number(previous_line):
                    self.__entry_data['content'][-1][-1].append(line)
                else:
                    raise OrgParserException(
                        'In state LIST, current line \"' +
                        str(line) +
                        '\" did not look like list item.\n' +
                        'So far, a list has to be ended with an empty line.' +
                        ' Please do not confuse me and fix it.')

            elif state == self.TABLE:

                # parses table data and return to ENTRY_CONTENT

                if line == '':
                    # table is over now:
                    state = self.ENTRY_CONTENT
                    previous_line = line
                    continue
                elif line.upper().startswith('#+TBLFM:'):
                    # table formulas are omitted in output
                    continue
                elif line.startswith('|'):
                    # append to the last element of content (which is a list from the current block) to
                    # its last element (which contains the list of the block
                    # content):
                    self.__entry_data['content'][-1][-1].append(line)
                else:
                    # if in state TABLE, each line has to be either empty,
                    # TBLFM or pipe character:
                    raise OrgParserException(
                        'In state TABLE, current line \"' +
                        str(line) +
                        '\" did not start with either \"|\", \"#+TBLFM:\", or empty line.' +
                        ' Please do not confuse me and fix it.')

            elif state == self.COLON_BLOCK:

                # parses sections started with a colon and return to
                # ENTRY_CONTENT
                if line.startswith(':'):
                    self.__entry_data['content'][-1][-1].append(line)
                else:
                    if line != '':
                        # FIXXME: I feel ashamed but without goto I am probably
                        # not able to handle this
                        raise OrgParserException(
                            'Sorry, this parser currently needs an empty line after ' +
                            'a colon-block. Found following line instead: \"' +
                            str(line) +
                            '\"')
                    state = self.ENTRY_CONTENT
                    previous_line = line
                    continue

            else:
                raise OrgParserException(
                    "unknown FSM state \"%s\"" %
                    str(state))

            previous_line = line

        if state != self.SEARCHING_BLOG_HEADER:
            # in case file ends while parsing an blog entry (no following
            # heading is finishing current entry):
            self.logging.debug(
                "OrgParser: finished file \"%s\" while parsing blog entry. Finishing it." %
                self.__filename)
            self.__handle_blog_end("", rawcontent)

        self.logging.debug("OrgParser: finished file \"%s\"" % self.__filename)
        # debug:   data = self._OrgParser__entry_data ; data['content']
        # self._OrgParser__blog_data
        # self._OrgParser__entry_data
        # self._OrgParser__filename
        return self.__blog_data, stats_parsed_org_lines


# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
