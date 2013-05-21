# -*- coding: utf-8 -*-
# Time-stamp: <2013-05-21 16:02:47 vk>

import re
import os
import codecs

## debugging:   for setting a breakpoint:  pdb.set_trace()
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

    ## asterisk(s), whitespace, word(s), optional followed by tags:
    HEADING_REGEX = re.compile('^(\*+)\s+((' + BLOG_FINISHED_STATE + ')\s+)?(.*?)(\s+(:\S+:)+)?\s*$')
    ## REGEX.match(string).group(INDEX)
    HEADING_STARS_IDX = 1
    HEADING_STATE_IDX = 3
    HEADING_NAME_IDX = 4
    HEADING_TAGS_IDX = 6  ## components(HEADING_TAGS_IDX)[1:-1].split(':') -> array of tags

    logging = None

    __filename = u''

    ## for description please visit: lazyblog.org > Notes > Representation of blog data
    __blog_data = []  ## list of all parsed entries of __filename
    __entry_data = {} ## dict of current entry of __blog_data being written to

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

        if not self.__entry_data['id']:
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

        pass
        #FIXXME


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
        previous_line = u''

        for rawline in codecs.open(self.__filename, 'r', encoding='utf-8'):

            line = rawline.rstrip()  ## remove trailing whitespace

            #self.logging.debug("OrgParser: ------------------------------- %s" % state)
            self.logging.debug("OrgParser: %s ###### line: \"%s\"" % (state, line))
            
            if state == self.SEARCHING_BLOG_HEADER:

                ## search for header line of a blog entry -> BLOG_HEADER

                components = self.HEADING_REGEX.match(line)

                #pdb.set_trace()## FIXXME

                if components and components.group(self.HEADING_STATE_IDX) == self.BLOG_FINISHED_STATE:

                    self.__handle_blog_heading(components.group(self.HEADING_STARS_IDX), 
                                               components.group(self.HEADING_NAME_IDX), 
                                               components.group(self.HEADING_TAGS_IDX))
                    state = self.BLOG_HEADER
                    next

                else:
                    self.logging.debug("OrgParser: line is not of any interest, skipping.")
                    next
                    
                ## FIXXME

            elif state == self.BLOG_HEADER:

                ## after header found: search for drawers (DRAWER_*) until content -> ENTRY_CONTENT
                ## NOTE: yes, content between header and drawers is ignored/lost.

                if line == ':PROPERTIES:':
                    self.logging.debug("found PROPERTIES drawer")
                    state = self.DRAWER_PROP
                    next
                elif line == ':LOGBOOK:':
                    self.logging.debug("found LOGBOOK drawer")
                    state = self.DRAWER_LOGBOOK
                    next

            elif state == self.ENTRY_CONTENT:

                ## default/main state: parse entry content and look out for content that has got its own state

                components = self.HEADING_REGEX.match(line)

                if line == ':PROPERTIES:':
                    self.logging.debug("found PROPERTIES drawer")
                    state = self.DRAWER_PROP
                    next
                elif line == ':LOGBOOK:':
                    self.logging.debug("found LOGBOOK drawer")
                    state = self.DRAWER_LOGBOOK
                    next
                elif components:
                    self.logging.debug("found new heading")

                    level = len(components.group(self.HEADING_STARS_IDX))

                    if True: ## FIXXME: replace with "if entry_level <= level"
                        ## level is same or higher as main heading of blog entry: end of blog entry
                        pass
                        # FIXXME

                        self.logging.debug("end of blog entry; checking entry ...")
                        if self.__check_entry_data():
                            self.__blog_data.append(self.__entry_data)
                        
                        self.__entry_data = {}  ## empty current entry data

                        ## is newly found heading a new blog entry?
                        components = self.HEADING_REGEX.match(line)
                        if components and components.group(self.HEADING_STATE_IDX) == self.BLOG_FINISHED_STATE:
                            self.logging.debug("OrgParser: found heading (directly after previous blog entry)")

                            self.__handle_blog_heading(components.group(self.HEADING_STARS_IDX), 
                                                       components.group(self.HEADING_NAME_IDX), 
                                                       components.group(self.HEADING_TAGS_IDX))
                            state = self.BLOG_HEADER
                            next

                        else:
                           state = self.SEARCHING_BLOG_HEADER
                           next

                    elif False: ## FIXXME: replace with "if entry_level < level"
                        ## sub-heading of entry

                        name = components.group(HEADING_NAME_IDX)
                        tags = components.group(HEADING_TAGS_IDX)
                        self.logging.debug("found new sub-heading")
                        
                        # FIXXME

                ## FIXXME
                pass

            elif state == self.DRAWER_PROP:

                ## parse properties and return to ENTRY_CONTENT

                if line.startswith(':ID:'):
                    id = line[4:].strip().replace(u' ','')

                    self.__entry_data['id'] = id
                    
                elif line == ':END:':
                    self.logging.debug("end of drawer")
                    state = self.ENTRY_CONTENT
                    next

                ## FIXXME

            elif state == self.DRAWER_LOGBOOK:

                ## parse logbook entries and return to ENTRY_CONTENT

                if line == ':END:':
                    self.logging.debug("end of drawer")
                    state = self.ENTRY_CONTENT
                    next

                ## FIXXME
                pass

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
