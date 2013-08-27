# -*- coding: utf-8 -*-
# Time-stamp: <2013-08-27 21:11:20 vk>

import logging

## debugging:   for setting a breakpoint:  pdb.set_trace()
## NOTE: pdb hides private variables as well. Please use:   data = self._OrgParser__entry_data ; data['content']
import pdb
                #pdb.set_trace()## FIXXME


class Htmlizer(object):
    """
    Class for generating HTML output of lazyblorg
    """

    logging = None  ## instance of logger

    template_definitions = None  ## list of lists ['description', 'content'] with content being the HTML templates
    blog_data = None  ## internal representation of the complete blog content
    generate = None  ## list of IDs which blog entries should be generated
    increment_version = None  ## list of IDs which blog entries gets an update

    def __init__(self, template_definitions, blog_data, generate, increment_version):
        """
        This function FIXXME

        @param template_definitions: list of lists ['description', 'content'] with content being the HTML templates
        @param blog_data: internal representation of the complete blog content
        @param generate: list of IDs which blog entries should be generated
        @param increment_version: list of IDs which blog entries gets an update
        """

        ## initialize class variables
        self.template_definitions = template_definitions
        self.blog_data = blog_data
        self.generate = generate
        self.increment_version = increment_version

         ## create logger (see http://docs.python.org/2/howto/logging-cookbook.html)
        self.logging = logging.getLogger('lazyblorg.htmlizer')

        self.logging.debug("Htmlizer initiated with %s templ.def., %s blog_data, %s generate, %s increment" % 
                           (str(len(template_definitions)), str(len(blog_data)), str(len(generate)), 
                            str(len(increment_version))))

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
