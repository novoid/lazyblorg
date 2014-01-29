#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2014-01-29 20:39:37 vk>

## TODO:
## * fix parts marked with «FIXXME»

## ===================================================================== ##
##  You might not want to modify anything below this line if you do not  ##
##  know, what you are doing :-)                                         ##
## ===================================================================== ##

import os
import logging
import datetime
import sys
import argparse  ## command line arguments
from lib.utils import *
from lib.orgparser import *
from lib.htmlizer import *
import pickle  ## for serializing and storing objects into files

## debugging:   for setting a breakpoint:
#pdb.set_trace()## FIXXME
import pdb

PROG_VERSION_NUMBER = u"0.1"
PROG_VERSION_DATE = u"2013-08-27"
INVOCATION_TIME = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

## the prefix is added to the blog entry path such as: TARGETPATH/BLOG_PREFIX/2013/12/31/blog-id/
## set either to a string which is a valid folder name or set it to ''
BLOG_PREFIX = u'blog'

## this Org-mode tag marks blog entries:
## FIXXME: also defined as TAG_FOR_BLOG_ENTY in OrgParser!
BLOG_TAG = u'blog'

EPILOG = u"\n\
:copyright: (c) 2013 by Karl Voit <tools@Karl-Voit.at>\n\
:license: GPL v3 or any later version\n\
:URL: https://github.com/novoid/lazyblorg\n\
:bugreports: via github or <tools@Karl-Voit.at>\n\
:version: " + PROG_VERSION_NUMBER + " from " + PROG_VERSION_DATE + "\n"


class Lazyblorg(object):
    """
    Central lazyblorg Class with main algorithm and methods
    """

    ## format of the storage file
    ## pickle offers, e.g., 0 (ASCII; human-readable) or pickle.HIGHEST_PROTOCOL (binary; more efficient)
    #PICKLE_FORMAT = pickle.HIGHEST_PROTOCOL
    PICKLE_FORMAT = 0

    options = None
    list_of_orgfiles = []
    logging = None

    blog_data = []
    metadata = []  ## meta-data of the current run of lazyblorg
    previous_metadata = None  ## meta-data of the previous run of lazyblorg
    template_definitions = None  ## list of definitions of templates

    ## categories of blog entries:
    ## FIXXME: also defined in: OrgParser utils.py htmlizer
    TAGS = 'TAGS'
    PERSISTENT = 'PERSISTENT'
    TEMPORAL = 'TEMPORAL'
    TEMPLATES = 'TEMPLATES'

    def __init__(self, options, logging):

        self.options = options
        self.logging = logging

        self.list_of_orgfiles = []
        self.blog_data = []
        self.metadata = []  ## meta-data of the current run of lazyblorg
        self.previous_metadata = None  ## meta-data of the previous run of lazyblorg
        self.template_definitions = None

    def determine_changes(self):
        """

        Parses input Org-mode files, reads in previous meta-data file,
        and determines which articles changed in which way.

        @param return: generate: list of IDs of articles in blog_data/metadata that should be build
        @param return: marked_for_RSS: list of IDs of articles in blog_data/metadata that are modified/new
        @param return: increment_version: list of IDs of articles in blog_data/metadata that got a new version
        """

        options = self.options

        logging.debug("iterate over files ...")
        for filename in options.orgfiles:
            try:
                file_blog_data = self._parse_orgmode_file(filename)  ## parsing one Org-mode file
            except OrgParserException as message:
                verbose_message = "Parsing error in file \"" + filename + \
                    "\" which is not good. Therefore, I stop here and hope you " + \
                    "can fix the issue in the Org-mode file. Reason: " + message.value
                Utils.error_exit_with_userlog(options.logfilename, 20, verbose_message)
            else:
                #pdb.set_trace()## FIXXME
                self.blog_data += file_blog_data

        ## dump blogdata for debugging purpose ...
        if options.verbose:
            with open('lazyblorg_dump_of_blogdata_from_last_verbose_run.pk', 'wb') as output:
                pickle.dump(self.blog_data, output, 0)  ## always use ASCII format: easier to debug from outside

        #pdb.set_trace()## FIXXME
        ## FIXXME: debug with: [x['id'] for x in self.blog_data]
        
        ## generate persistent data which is used to compare this status
        ## with the status of the next invocation:
        self.metadata = Utils.generate_metadata_from_blogdata(self.blog_data)

        ## write this status to the persistent data file:
        with open(options.metadatafilename + '_temp', 'wb') as output:
            pickle.dump(self.metadata, output, self.PICKLE_FORMAT)

        ## load old metadata from file
        if os.path.isfile(options.metadatafilename):
            logging.debug("reading old \"" + options.metadatafilename + "\" ...")
            with open(options.metadatafilename, 'rb') as input:
                self.previous_metadata = pickle.load(input)

        ## extract HTML templates and store in class var
        self.template_definitions = self._generate_template_definitions_from_template_data()

        ## run comparing algorithm (last metadata, current metadata)
        generate, marked_for_RSS, increment_version = self._compare_blogdata_to_metadata()

        return generate, marked_for_RSS, increment_version

    def OLD_parse_HTML_output_template_and_generate_template_definitions(self):
        """

        Parse the template Org-mode file which contains the HTML
        definitions and store it into class variable
        template_definitions.

        @param return: True if success
        """

        template_data = self._parse_HTML_output_template(self.options.templatefilename)

        self.template_definitions = self._generate_template_definitions_from_template_data(template_data)

        return True

    def generate_output(self, generate, marked_for_RSS, increment_version):
        """

        FIXXME

        @param generate: list of IDs of articles in blog_data/metadata that should be build
        @param marked_for_RSS: list of IDs of articles in blog_data/metadata that are modified/new
        @param increment_version: list of IDs of articles in blog_data/metadata that got a new version
        @param return:
        """

        htmlizer = Htmlizer(self.template_definitions, BLOG_PREFIX, BLOG_TAG, self.options.aboutblog,
                            self.options.targetdir, self.blog_data, generate, increment_version)

        ## FIXXME: try except HtmlizerException?
        htmlizer.run()  ## FIXXME: return value?

        ## FIXXME: generate pages
        ## (metadata, blog_data, template_definitions, options.tagetdir)

        ## FIXXME: generate new RSS feed

    def _parse_orgmode_file(self, filename):
        """
        This function handles the communication with the parser object and returns the blog data.

        @param filename: string containing one file name
        @param return: array containing parsed Org-mode data
        """

        if os.path.isdir(filename):
            self.logging.warning("Skipping directory \"%s\" because this tool only parses files." % filename)
            return
        elif not os.path.isfile(filename):
            self.logging.warning("Skipping non-file \"%s\" because this tool only parses files." % filename)
            return

        self.logging.info("Parsing \"%s\" ..." % filename)
        parser = OrgParser(filename)

        return parser.parse_orgmode_file()

    def OLD_parse_HTML_output_template(self, filename):
        """
        This function parses an Org-mode file which holds the definitions of the output format.

        @param filename: string containing one file name of the definition file
        @param return: dict containing parsed template definitions
        """

        template_parser = OrgParser(filename)

        return template_parser.parse_orgmode_file()

    def _generate_template_definitions_from_template_data(self):
        """
        This function checks for (only) basic format definitions and exits
        if something important is missing.

        @param return: list of HTML definitions as Org-mode HTML block list-elements
        """

        self.logging.debug('checking for basic template definitions in parsed data ...')

        ## extract template_data from blog_data:
        template_data = [x for x in self.blog_data \
                             if x['id']=='lazyblorg-templates' and x['title'] == u'Templates']
        #pdb.set_trace()## FIXXME

        if not template_data:
            message = "Sorry, no suitable template data could be parsed from the Org-mode files. " + \
                "Please check if it meets all criteria as described in the original template " + \
                "file \"blog-format.org\"."
            Utils.error_exit_with_userlog(self.options.logfilename, 40, message)

        html_definitions = [x for x in template_data[0]['content'] \
                                if x[0] == 'html-block']

        found_elements = [x[1] for x in html_definitions]

        ## for documentation about the implemented elements: see id:implemented-org-elements in dev/lazyblorg.org
        for element in [u'article-header', u'article-footer', u'article-header-begin', u'article-tags-begin',
                        u'article-tag', u'article-tags-end', u'article-header-end', u'article-end',
                        u'section-begin', u'paragraph', u'a-href',
                        u'ul-begin', u'ul-item', u'ul-end', u'pre-begin', u'pre-end']:
            if not element in found_elements:
                message = "Sorry, no definition for element \"" + element + "\" could be found within " + \
                    "the template definition file. " + \
                    "Please check if you mistyped its name or similar."
                Utils.error_exit_with_userlog(self.options.logfilename, 42, message)

        return html_definitions

    def _compare_blogdata_to_metadata(self):
        """
        In this function, the previous status (previous_metadata) is
        compared to the status from the current parsing result
        (metadata). It implements "Decision algorithm for generating
        entries" as described in dev/lazyblorg.org.

        The algorithm distinguishes between eight cases:

        1) no ID found -> is not possible here any more since metadata
        (dict) contains only entries with IDs -> should be done in parser:
        WARN, ignore

        2) new ID found -> generate, mark_for_RSS

        3) CREATED not found -> WARN, ignore

        4) CREATED found but differs from previous run (should not change)
        -> WARN, ignore

        5) and 6) known and matching previous run: ID, CREATED, checksum
        -> not changed (case 5/6 only differs in status of last timestamp)
        -> generate

        (FIXXME: in future, case 5 and 6 should result in "ignore". But
        for this, I have to switch from "delete everything and re-generate
        everything on every run" to "delete and re-generate only necessary
        entries/pages")

        7) known and matching: ID, CREATED, last timestamp; differs:
        checksum -> silent update -> generate

        8) known and matching: ID, CREATED; differs: checksum, last
        timestamp -> normal update -> generate, mark_for_RSS,
        increment_version

        The format of the metadata is described in dev/lazyblorg.org >
        Notes > Internal format of meta-data.

        @param return: generate: a list of metadata-entries that should be generated
        @param return: marked_for_RSS: a list of metadata-entries that are candidates to be propagated using RSS feeds
        @param return: increment_version: a list of metadata-entries that can be marked with an increased update number
        """

        self.logging.debug("compare_blog_metadata() called ...")

        generate = []
        marked_for_RSS = []
        increment_version = []
        metadata = self.metadata
        previous_metadata = self.previous_metadata

        if previous_metadata is None:
            self.logging.info("no previous metadata found: must be the first run of lazyblorg with this configuration")

        for entry in metadata:  ## ignore blog entries that have been gone since last run

            ## debug output current entry and its meta-data:
            self.logging.debug(" processing entry [" + str(repr(entry)) +
                               "]   <--------------\nwith [checksum, created, timestamp]:\n  md " +
                               str([x[1] for x in sorted(metadata[entry].items(), key=lambda t: t[0])]))
            if previous_metadata is not None:
                if entry in previous_metadata.keys():
                    self.logging.debug("\nprev " +
                                       str([x[1] for x in sorted(previous_metadata[entry].items(), key=lambda t: t[0])]))
                else:
                    self.logging.debug("no previous metadata found for this entry")

            if previous_metadata is None:
                self.logging.debug("case 2: brand-new entry (first run of lazyblorg)")
                generate.append(entry)
                marked_for_RSS.append(entry)
                continue

            if entry not in previous_metadata.keys():
                self.logging.debug("case 2: brand-new entry (lazyblorg was run previously)")
                generate.append(entry)
                marked_for_RSS.append(entry)
                continue

            elif 'created' not in metadata[entry].keys():
                self.logging.debug("case 3: \"created\" missing -> WARN, ignore")
                message = "entry [" + entry + "] is missing its CREATED property. Will be ignored, until you fix it."
                Utils.append_logfile_entry(self.options.logfilename, 'warn', message)
                self.logging.warn(message)
                continue

            elif metadata[entry]['created'] != previous_metadata[entry]['created']:
                self.logging.debug("case 4: \"created\" differs -> WARN, ignore")
                message = "CREATED property of entry [" + entry + "] has changed which should never happen. " + \
                    "Entry will be ignored this run. Will be created next run if CREATED will not change any more."
                Utils.append_logfile_entry(self.options.logfilename, 'warn', message)
                self.logging.warn(message)
                continue

            elif metadata[entry]['created'] == previous_metadata[entry]['created'] and \
                    metadata[entry]['checksum'] == previous_metadata[entry]['checksum']:
                self.logging.debug("case 5 or 6: old entry -> generate")
                generate.append(entry)
                continue

            elif metadata[entry]['created'] == previous_metadata[entry]['created'] and \
                    metadata[entry]['timestamp'] == previous_metadata[entry]['timestamp'] and \
                    metadata[entry]['checksum'] != previous_metadata[entry]['checksum']:
                self.logging.debug("case 7: silent update -> generate")
                generate.append(entry)
                continue

            elif metadata[entry]['created'] == previous_metadata[entry]['created'] and \
                    metadata[entry]['timestamp'] != previous_metadata[entry]['timestamp'] and \
                    metadata[entry]['checksum'] != previous_metadata[entry]['checksum']:
                self.logging.debug("case 8: normal update -> generate, mark_for_RSS, increment_version")
                generate.append(entry)
                marked_for_RSS.append(entry)
                increment_version.append(entry)
                continue

            else:
                ## warn (should never be reached)
                message = "compare_blog_metadata() is confused with entry [" + entry + "] which " + \
                    "reached an undefined situation when comparing meta-data. You can re-run. " + \
                    "If this warning re-appears, please use \"--verbose\" and check entry."
                Utils.append_logfile_entry(self.options.logfilename, 'warn', message)
                self.logging.warn(message)

        return generate, marked_for_RSS, increment_version


if __name__ == "__main__":

    mydescription = u"An Org-mode to HTML-blog system for very lazy people. Please refer to \n" + \
        "https://github.com/novoid/lazyblorg for more information."

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter,  ## keep line breaks in EPILOG and such
                                     epilog=EPILOG,
                                     description=mydescription)

    parser.add_argument("--orgfiles", dest="orgfiles", nargs='+', metavar='ORGFILE', required=True,
                        help="One or more Org-mode files which contains all blog articles (and possible other stuff).")

    parser.add_argument("--aboutblog", dest="aboutblog", metavar='STRING', required=True,
                        help="A short description about the blog. " +
                        "E.g., \"... where knowledge is defined!\".")

    parser.add_argument("--targetdir", dest="targetdir", metavar='DIR', required=True,
                        help="Path where the HTML files will be written to. " +
                        "On first run, this should be an empty directory.")

    parser.add_argument("--metadata", dest="metadatafilename", metavar='FILE', required=True,
                        help="Path to a file where persistent meta-data of the blog entries " +
                        "is written to. Next run, it will be read and used for comparison to current situation." +
                        "Therefore, this file can be missing in the first run.")

    parser.add_argument("--logfile", dest="logfilename", metavar='ORGFILE', required=True,
                        help="Path to a file where warnings (inactive time-stamps) and errors " +
                        "(active time-stamps) are being appended in Org-mode format. " +
                        "It is highly recommended, that you add this file to your agenda list.")

    parser.add_argument("-v", "--verbose", dest="verbose", action="store_true",
                        help="Enable verbose mode which is quite chatty - be warned.")

    parser.add_argument("-q", "--quiet", dest="quiet", action="store_true",
                        help="Enable quiet mode: only warnings and errors will be reported.")

    parser.add_argument("--version", dest="version", action="store_true",
                        help="Display version and exit.")

    options = parser.parse_args()

    logging = Utils.initialize_logging("lazyblorg", options.verbose, options.quiet)

    try:

        if options.version:
            print os.path.basename(sys.argv[0]) + " version " + PROG_VERSION_NUMBER + \
                " from " + PROG_VERSION_DATE
            sys.exit(0)

        ## checking parameters ...

        ##if not options.logfilename:
        ##    logging.critical("Please give me a file to write to with option \"--logfile\".")
        ##    Utils.error_exit(5)

        if not os.path.isfile(options.logfilename):
            logging.debug("log file \"" + options.logfilename + "\" is not found. Initializing with heading ...")

        with open(options.logfilename, 'a') as outputhandle:
            outputhandle.write(u"## -*- coding: utf-8 -*-\n" +
                               "## This file is best viewed with GNU Emacs Org-mode: http://orgmode.org/\n" +
                               "* Warnings and Error messages from lazyblorg     :lazyblorg:log:\n\n" +
                               "Messages gets appended to this file. Please remove fixed issues manually.\n")
            outputhandle.flush()

        if options.verbose and options.quiet:
            logging.error("Options \"--verbose\" and \"--quiet\" found. " +
                          "This does not make any sense, you silly fool :-)")
            Utils.error_exit(1)

        ##if not options.targetdir:
        ##    logging.critical("Please give me a folder to write to with option \"--targetdir\".")
        ##    Utils.error_exit(2)

        if not os.path.isdir(options.targetdir):
            logging.critical("Target directory \"" + options.targetdir + "\" is not a directory. Aborting.")
            Utils.error_exit(3)

        ##if not options.metadatafilename:
        ##    logging.critical("Please give me a file to write to with option \"--metadata\".")
        ##    Utils.error_exit(4)

        if not os.path.isfile(options.metadatafilename):
            logging.warn("Blog data file \"" + options.metadatafilename + "\" is not found. Assuming first run!")

        logging.debug("extracting list of Org-mode files ...")
        logging.debug("len(orgfiles) [%s]" % str(len(options.orgfiles)))
        if len(options.orgfiles) < 1:
            logging.critical("Please add at least one Org-mode file name as argument")
            Utils.error_exit(6)

        ## print file names if less than 10:
        if len(options.orgfiles) < 10:
            logging.debug("%s filenames found: [%s]" % (str(len(options.orgfiles)), '], ['.join(options.orgfiles)))
        else:
            logging.debug("%s filenames found")

        ## main algorithm:
        lazyblorg = Lazyblorg(options, logging)
        ## FIXXME: encapsulate following lines in lazyblorg.run() ?
        #lazyblorg.parse_HTML_output_template_and_generate_template_definitions()
        generate, marked_for_RSS, increment_version = lazyblorg.determine_changes()
        lazyblorg.generate_output(generate, marked_for_RSS, increment_version)

        logging.debug("-------------> cleaning up the stage ...")

        ## remove old options.metadatafilename
        if os.path.isfile(options.metadatafilename):
            logging.debug("deleting old \"" + options.metadatafilename + "\" ...")
            os.remove(options.metadatafilename)

        ## rename options.metadatafilename + '_temp' -> options.metadatafilename
        logging.debug("removing temporary \"" + options.metadatafilename + "_temp\" to \"" +
                      options.metadatafilename + "\" ...")
        os.rename(options.metadatafilename + '_temp', options.metadatafilename)

        logging.debug("successfully finished.")

    except KeyboardInterrupt:

        logging.info("Received KeyboardInterrupt")

## END OF FILE #################################################################
# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
