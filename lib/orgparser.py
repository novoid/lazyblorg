# -*- coding: utf-8 -*-
# Time-stamp: <2013-08-20 15:28:04 vk>

import re
import os
import codecs
from orgformat import *

## debugging:   for setting a breakpoint:  pdb.set_trace()
## NOTE: pdb hides private variables as well. Please use:   data = self._OrgParser__entry_data ; data['content']
import pdb
                #pdb.set_trace()## FIXXME


class OrgmodeParseException(Exception):
    """
    Own exception for parsing errors
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class OrgParser(object):
    """
    Class for parsing Org-mode formatted files
    """

    ## string of the state which defines a blog entry to be published
    BLOG_FINISHED_STATE = u'DONE'

    LINE_SEPARATION_CHAR_WITHIN_PARAGRAPH = u' '

    ## Finite State Machine: defining the states
    ## NOTE: value of numbers are irrelevant - just make sure they are distinct
    SEARCHING_BLOG_HEADER = 'searching_blog_header'
    BLOG_HEADER = 'blog_header'
    ENTRY_CONTENT = 'entry_content'
    DRAWER_PROP = 'drawer_prop'
    DRAWER_LOGBOOK = 'drawer_logbook'
    BLOCK = 'block'
    LIST = 'list'
    TABLE = 'table'
    COLON_BLOCK = 'colon_block'

    ## asterisk(s), whitespace, word(s), optional followed by optional tags:
    HEADING_REGEX = re.compile('^(\*+)\s+((' + BLOG_FINISHED_STATE + ')\s+)?(.*?)(\s+(:\S+:)+)?\s*$')
    ## REGEX.match(string).group(INDEX)
    HEADING_STARS_IDX = 1
    HEADING_STATE_IDX = 3
    HEADING_TITLE_IDX = 4
    HEADING_TAGS_IDX = 6  ## components(HEADING_TAGS_IDX)[1:-1].split(':') -> array of tags

    LOG_REGEX = re.compile('^- State\s+"' + BLOG_FINISHED_STATE + '"\s+from\s+"\S*"\s+([\[{].*[\]}])$')
    LOG_TIMESTAMP_IDX = 1

    logging = None

    __filename = u''

    ## for description please visit: lazyblog.org > Notes > Representation of blog data
    __blog_data = []   ## list of all parsed entries of __filename: contains a list with elements of type __entry_data
    __entry_data = {}  ## dict of current blog entry data: gets "filled" while parsing the entry

    def __init__(self, filename, logging):
        """
        This function handles the communication with the parser object and returns the blog data.

        @param filename: string containing one file name
        """

        assert filename.__class__ == str or filename.__class__ == unicode
        assert os.path.isfile(filename)

        self.__filename = filename
        self.logging = logging

    def __check_entry_data(self):
        """
        Checks if current entry (self.__entry_data) is valid and
        complete and thus can be added to the blog output.

        @param return: True if OK or False if not OK (and entry has to be skipped)
        """

        self.logging.debug("check_entry_data: checking current entry ...")
        errors = 0

        if not 'id' in self.__entry_data.keys():
            self.logging.error("Heading does not contain any ID within PROPERTY drawer")
            errors += 1

        if not 'level' in self.__entry_data.keys():
            self.logging.error("Heading does not contain a heading level")
            errors += 1

        if not 'title' in self.__entry_data.keys():
            self.logging.error("Heading does not contain a title")
            errors += 1

        if not 'timestamp' in self.__entry_data.keys():
            self.logging.error("Heading does not contain a timestamp")
            errors += 1

        if 'content' in self.__entry_data.keys():
            if len(self.__entry_data['content']) < 1:
                self.logging.error("Heading does not contain a filled content")
                errors += 1
        else:
            self.logging.error("Heading does not contain a content")
            errors += 1

        if not 'tags' in self.__entry_data.keys():
            self.logging.info("Heading does not contain tags but this is probably OK: \"%s\"" %
                              self.__entry_data['title'])
            errors += 1

        if errors > 0:
            self.logging.error("check_entry_data: %s errors were found for heading \"%s\" in file \"%s\"" %
                               (str(errors), self.__entry_data['title'], self.__filename))
            return False
        else:
            self.logging.debug("check_entry_data: current entry has been checked positively for being added to the blog data")
            #pdb.set_trace()## FIXXME:   data = self._OrgParser__entry_data ; data['content']
            return True

    def __handle_blog_heading(self, stars, title, tags):
        """
        Handles a heading line of a blog entry.

        @param stars: string containing the heading asterisks
        @param title: string containing description of heading line
        @param tags: string containing raw tags like ":tag1:tag2:"
        @param blog_data: data representation of the blog data parsed so far
        @param return: FIXXME
        """

        assert stars.__class__ == str or stars.__class__ == unicode
        assert title.__class__ == str or title.__class__ == unicode
        assert tags.__class__ == str or tags.__class__ == unicode

        self.__entry_data['title'] = title
        self.__entry_data['tags'] = tags[1:-1].split(':')
        self.__entry_data['level'] = len(stars)

        self.logging.debug("OrgParser: heading: level[%s] title[%s] tags%s" %
                           (str(self.__entry_data['level']),
                            self.__entry_data['title'],
                            str(self.__entry_data['tags'])))

    def __handle_blog_end(self, line):
        """
        Handles the end of the current blog entry.

        @param line: string containing current parsed line
        @param return: ID of next state
        """

        self.logging.debug("end of blog entry; checking entry ...")
        if self.__check_entry_data():
            self.__blog_data.append(self.__entry_data)

        self.__entry_data = {}  ## empty current entry data

        ## is newly found heading a new blog entry?
        heading_components = self.HEADING_REGEX.match(line)
        if heading_components and heading_components.group(self.HEADING_STATE_IDX) == self.BLOG_FINISHED_STATE:
            self.logging.debug("OrgParser: found heading (directly after previous blog entry)")

            self.__handle_blog_heading(heading_components.group(self.HEADING_STARS_IDX),
                                       heading_components.group(self.HEADING_TITLE_IDX),
                                       heading_components.group(self.HEADING_TAGS_IDX))
            return self.BLOG_HEADER

        else:
            return self.SEARCHING_BLOG_HEADER

    def parse_orgmode_file(self):
        """
        Parses the Org-mode file.

        @param return: array containing parsed Org-mode data
        """

        self.logging.debug("OrgParser: doing file \"%s\" ..." % self.__filename)

        ## finite state machine:
        ## SEARCHING_BLOG_HEADER | BLOG_HEADER | ENTRY_CONTENT | ...
        ## ... DRAWER_PROP | DRAWER_LOGBOOK | BLOCK | LIST | TABLE | COLON_BLOCK
        state = self.SEARCHING_BLOG_HEADER

        ## contains content of previous line
        ## NOTE: only valid as long a state does not use "next" in the previous parsing step.
        previous_line = False

        for rawline in codecs.open(self.__filename, 'r', encoding='utf-8'):

            line = rawline.rstrip()  ## remove trailing whitespace

            self.logging.debug("OrgParser: ------------------------------- %s" % state)
            self.logging.debug("OrgParser: %s ###### line: \"%s\"" % (state, line))

            if state == self.SEARCHING_BLOG_HEADER:

                ## search for header line of a blog entry -> BLOG_HEADER

                components = self.HEADING_REGEX.match(line)

                if components and components.group(self.HEADING_STATE_IDX) == self.BLOG_FINISHED_STATE:

                    self.__handle_blog_heading(components.group(self.HEADING_STARS_IDX),
                                               components.group(self.HEADING_TITLE_IDX),
                                               components.group(self.HEADING_TAGS_IDX))
                    state = self.BLOG_HEADER
                    previous_line = line
                    continue

                else:
                    self.logging.debug("OrgParser: line is not of any interest, skipping.")
                    previous_line = line
                    continue

            elif state == self.BLOG_HEADER:

                ## after header found: search for drawers (DRAWER_*) until content -> ENTRY_CONTENT
                ## NOTE: yes, content between header and drawers is ignored/lost.

                if line == ':PROPERTIES:':
                    self.logging.debug("found PROPERTIES drawer")
                    state = self.DRAWER_PROP
                    previous_line = line
                    continue
                elif line == ':LOGBOOK:':
                    self.logging.debug("found LOGBOOK drawer")
                    state = self.DRAWER_LOGBOOK
                    previous_line = line
                    continue

            elif state == self.ENTRY_CONTENT:

                ## default/main state: parse entry content and look out for content that has got its own state

                if not 'content' in self.__entry_data.keys():
                    ## append empty content list to __entry_data
                    self.__entry_data['content'] = []

                heading_components = self.HEADING_REGEX.match(line)

                if line == ':PROPERTIES:':
                    self.logging.debug("found PROPERTIES drawer")
                    state = self.DRAWER_PROP
                    previous_line = line
                    continue

                elif line == ':LOGBOOK:':
                    self.logging.debug("found LOGBOOK drawer")
                    state = self.DRAWER_LOGBOOK
                    previous_line = line
                    continue

                elif line == u'':
                    self.logging.debug("found empty line")
                    previous_line = line
                    #if len(self.__entry_data['content']) > 1:
                    #    if not self.__entry_data['content'][-1] == u'\n':
                    #        ## append newline to content (only if previous content is not a newline)
                    #        self.__entry_data['content'].append(u'\n')
                    continue

                elif heading_components:
                    self.logging.debug("found new heading")
                    level = len(heading_components.group(self.HEADING_STARS_IDX))

                    if level <= self.__entry_data['level']:
                        ## level is same or higher as main heading of blog entry: end of blog entry
                        state = self.__handle_blog_end(line)
                        previous_line = line
                        continue
                    else:
                        ## sub-heading of entry
                        title = heading_components.group(self.HEADING_TITLE_IDX)
                        self.logging.debug("inserting new sub-heading")
                        self.__entry_data['content'].append(['heading',
                                                             {'level': level, 'title': title}])

                ## FIXXME: add more elif line == ELEMENT

                else:
                    if len(self.__entry_data['content']) > 0:
                        if previous_line != u'' and self.__entry_data['content'][-1][0] == 'par':
                            ## concatenate this line with previous if it is still generic content within a paragraph
                            self.logging.debug("adding line as generic content to current paragraph")
                            self.__entry_data['content'][-1][1] += \
                                self.LINE_SEPARATION_CHAR_WITHIN_PARAGRAPH + line.strip()
                            previous_line = line
                            continue

                    self.logging.debug("adding line as new generic content paragraph")
                    self.__entry_data['content'].append(['par', line])
                    previous_line = line
                    continue

            elif state == self.DRAWER_PROP:

                ## parse properties for ID and return to ENTRY_CONTENT

                if line == ':END:':
                    self.logging.debug("end of drawer")
                    state = self.ENTRY_CONTENT
                    previous_line = line
                    continue

                if 'id' in self.__entry_data.keys():
                    ## if ID already found, ignore rest of PROPERTIES and all other PROPERTIES (of sub-headings)
                    logging.debug("ignoring PROPERTIES since I already got my ID")
                    previous_line = line
                    continue

                if line.startswith(':ID:'):
                    self.__entry_data['id'] = line[4:].strip().replace(u' ', '')

                else:
                    previous_line = line
                    continue

            elif state == self.DRAWER_LOGBOOK:

                ## parse logbook entries for state changes to self.BLOG_FINISHED_STATE and return to ENTRY_CONTENT

                if line == ':END:':
                    self.logging.debug("end of drawer")
                    state = self.ENTRY_CONTENT
                    previous_line = line
                    continue

                components = self.LOG_REGEX.match(line)
                if components:

                    ## extract time-stamp as datetime and add to finished-timestamp-history
                    datetimestamp = OrgFormat.orgmode_timestamp_to_datetime(components.group(self.LOG_TIMESTAMP_IDX))
                    if 'finished-timestamp-history' in self.__entry_data.keys():
                        self.__entry_data['finished-timestamp-history'].append(datetimestamp)
                    else:
                        self.__entry_data['finished-timestamp-history'] = [datetimestamp]

                    ## (over)write timestamp of blogentry if current datetimestamp is newest
                    if 'timestamp' in self.__entry_data.keys():
                        if datetimestamp > self.__entry_data['timestamp']:
                            self.__entry_data['timestamp'] = datetimestamp
                    else:
                        self.__entry_data['timestamp'] = datetimestamp

                previous_line = line
                continue

            elif state == self.BLOCK:

                ## parses general blocks and return to ENTRY_CONTENT

                ## FIXXME
                pass

            elif state == self.LIST:

                ## parses simple lists and return to ENTRY_CONTENT

                ## FIXXME
                pass

            elif state == self.TABLE:

                ## parses table data and return to ENTRY_CONTENT

                ## FIXXME
                pass

            elif state == self.COLON_BLOCK:

                ## parses sections started with a colon and return to ENTRY_CONTENT

                ## FIXXME
                pass

            else:
                self.logging.error("OrgParser: unknows FSM state \"%s\"" % str(state))

            previous_line = line

        self.logging.debug("OrgParser: finished file \"%s\"" % self.__filename)
        return self.__blog_data


# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
