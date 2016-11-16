#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2016-11-16 21:54:03 vk>

# TODO:
# * fix parts marked with «FIXXME»

## ===================================================================== ##
##  You might not want to modify anything below this line if you do not  ##
##  know, what you are doing :-)                                         ##
## ===================================================================== ##

import config  # lazyblorg-global settings
import os
import logging
from datetime import datetime
from sys import exit, argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from lib.utils import *
from lib.orgparser import *
from lib.htmlizer import *
import pickle  # for serializing and storing objects into files
from time import time  # for measuring execution time


PROG_VERSION_NUMBER = u"0.2"
PROG_VERSION_DATE = u"2014-02-01"
INVOCATION_TIME = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


EPILOG = u"\n\
  :copyright:  (c) 2013 and following by Karl Voit <tools@Karl-Voit.at>\n\
  :license:    GPL v3 or any later version\n\
  :URL:        https://github.com/novoid/lazyblorg\n\
  :bugreports: via github (preferred) or <tools@Karl-Voit.at>\n\
  :version:    " + PROG_VERSION_NUMBER + " from " + PROG_VERSION_DATE + "\n"


class Lazyblorg(object):
    """
    Central lazyblorg Class with main algorithm and methods
    """

    options = None
    list_of_orgfiles = []
    logging = None

    blog_data = []
    metadata = []  # meta-data of the current run of lazyblorg
    previous_metadata = None  # meta-data of the previous run of lazyblorg
    template_definitions = None  # list of definitions of templates
    # dict(year) of list(month) of list(day) of lists(entries) of IDs
    entries_timeline_by_published = None

    def __init__(self, options, logging):

        self.options = options
        self.logging = logging

        self.list_of_orgfiles = []
        self.blog_data = []
        self.metadata = []  # meta-data of the current run of lazyblorg
        self.previous_metadata = None  # meta-data of the previous run of lazyblorg
        self.template_definitions = None

    def determine_changes(self):
        """

        Parses input Org-mode files, reads in previous meta-data file,
        and determines which articles changed in which way.

        @param return: generate: list of IDs of articles in blog_data/metadata that should be build
        @param return: marked_for_feed: list of IDs of articles in blog_data/metadata that are modified/new
        @param return: increment_version: list of IDs of articles in blog_data/metadata that got a new version
        """

        options = self.options
        stats_parsed_org_files, stats_parsed_org_lines = 0, 0

        logging.debug("iterate over files ...")
        for filename in options.orgfiles:
            new_org_lines = 0
            try:
                file_blog_data, new_org_lines = self._parse_orgmode_file(
                    filename)  # parsing one Org-mode file
            except OrgParserException as message:
                verbose_message = "Parsing error in file \"" + filename + \
                    "\" which is not good. Therefore, I stop here and hope you " + \
                    "can fix the issue in the Org-mode file. Reason: " + message.value
                Utils.error_exit_with_userlog(
                    options.logfilename, 20, verbose_message)
            else:
                self.blog_data += file_blog_data
                stats_parsed_org_files += 1
                stats_parsed_org_lines += new_org_lines

        # dump blogdata for debugging purpose ...
        if options.verbose:
            with open('lazyblorg_dump_of_blogdata_from_last_verbose_run.pk', 'wb') as output:
                # always use ASCII format: easier to debug from outside
                pickle.dump(self.blog_data, output, 0)

        # FIXXME: debug with: [x['id'] for x in self.blog_data]

        # generate persistent data which is used to compare this status
        # with the status of the next invocation:
        self.metadata, self.entries_timeline_by_published = Utils.generate_metadata_from_blogdata(
            self.blog_data)

        # create path to new metadatafile if it does not exist:
        if not os.path.isdir(os.path.dirname(options.new_metadatafilename)):
            logging.debug(
                "path of new_metadatafilename \"" +
                options.new_metadatafilename +
                "\" does not exist. Creating ...")
            os.makedirs(os.path.dirname(options.new_metadatafilename))

        # write this status to the persistent data file:
        with open(options.new_metadatafilename, 'wb') as output:
            pickle.dump([self.metadata,
                         self.entries_timeline_by_published],
                        output,
                        config.PICKLE_FORMAT)

        # load old metadata from file
        if os.path.isfile(options.previous_metadatafilename):
            logging.debug(
                "reading old \"" +
                options.previous_metadatafilename +
                "\" ...")
            with open(options.previous_metadatafilename, 'rb') as input:
                [self.previous_metadata,
                 self.entries_timeline_by_published] = pickle.load(input)

        # extract HTML templates and store in class var
        self.template_definitions = self._generate_template_definitions_from_template_data()

        # run comparing algorithm (last metadata, current metadata)
        generate, marked_for_feed, increment_version = self._compare_blogdata_to_metadata()

        return generate, marked_for_feed, increment_version, stats_parsed_org_files, stats_parsed_org_lines

    def OLD_parse_HTML_output_template_and_generate_template_definitions(self):
        """

        Parse the template Org-mode file which contains the HTML
        definitions and store it into class variable
        template_definitions.

        @param return: True if success
        """

        template_data = self._parse_HTML_output_template(
            self.options.templatefilename)

        self.template_definitions = self._generate_template_definitions_from_template_data(
            template_data)

        return True

    def generate_output(self, generate, marked_for_feed, increment_version):
        """

        Generates the htmlized output pages and the RSS/ATOM feeds.

        @param generate: list of IDs of articles in blog_data/metadata that should be build
        @param marked_for_feed: list of IDs of articles in blog_data/metadata that are modified/new
        @param increment_version: list of IDs of articles in blog_data/metadata that got a new version
        @param return:
        """

        htmlizer = Htmlizer(
            self.template_definitions,
            config.TAG_FOR_BLOG_ENTRY,
            self.options.targetdir,
            self.blog_data,
            self.metadata,
            self.entries_timeline_by_published,
            generate,
            increment_version,
            self.options.autotag_language)

        # FIXXME: try except HtmlizerException?
        return htmlizer.run()  # FIXXME: return value?

    def _parse_orgmode_file(self, filename):
        """
        This function handles the communication with the parser object and returns the blog data.

        @param filename: string containing one file name
        @param return: array containing parsed Org-mode data
        """

        if os.path.isdir(filename):
            self.logging.warning(
                "Skipping directory \"%s\" because this tool only parses files." %
                filename)
            return
        elif not os.path.isfile(filename):
            self.logging.warning(
                "Skipping \"%s\" because this tool only parses existing files. :-)" %
                filename)
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

        self.logging.debug(
            'checking for basic template definitions in parsed data ...')

        # extract template_data from blog_data:
        template_data = [x for x in self.blog_data if x['id'] ==
                         'lazyblorg-templates' and x['title'] == u'Templates']

        if not template_data:
            message = "Sorry, no suitable template data could be parsed from the Org-mode files. " + \
                "Please check if it meets all criteria as described in the original template " + \
                "file \"blog-format.org\"."
            Utils.error_exit_with_userlog(
                self.options.logfilename, 40, message)

        html_definitions = [x for x in template_data[0]['content']
                            if x[0] == 'html-block']

        found_elements = [x[1] for x in html_definitions]

        # for documentation about the implemented elements: see
        # id:implemented-org-elements in dev/lazyblorg.org
        for element in [
            u'common-sidebar',
            u'article-header',
            u'article-footer',
            u'article-header-begin',
            u'article-tags-begin',
            u'article-usertag',
            u'article-autotag',
            u'article-tags-end',
            u'article-header-end',
            u'article-end',
            u'section-begin',
            u'paragraph',
            u'ul-begin',
            u'ul-item',
            u'ul-end',
            u'pre-begin',
            u'pre-end',
            u'entrypage-header',
            u'article-preview-header',
            u'article-preview-begin',
            u'article-preview-tags-begin',
            u'article-preview-usertag',
            u'article-preview-autotag',
            u'article-preview-tags-end',
            u'article-preview-more',
            u'article-preview-end',
                u'entrypage-footer']:
            if element not in found_elements:
                message = "Sorry, no definition for element \"" + element + "\" could be found within " + \
                    "the template definition file. " + "Please check if you mistyped its name or similar."
                Utils.error_exit_with_userlog(
                    self.options.logfilename, 42, message)

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

        2) new ID found -> generate, mark_for_feed

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
        timestamp -> normal update -> generate, mark_for_feed,
        increment_version

        The format of the metadata is described in dev/lazyblorg.org >
        Notes > Internal format of meta-data.

        @param return: generate: a list of metadata-entries that should be generated
        @param return: marked_for_feed: a list of metadata-entries that are candidates to be propagated using RSS feeds
        @param return: increment_version: a list of metadata-entries that can be marked with an increased update number
        """

        self.logging.debug("compare_blog_metadata() called ...")

        generate = []
        marked_for_feed = []
        increment_version = []
        metadata = self.metadata
        previous_metadata = self.previous_metadata

        if previous_metadata is None:
            self.logging.info(
                "no previous metadata found: must be the first run of lazyblorg with this configuration")

        for entry in metadata:  # ignore blog entries that have been gone since last run

            # debug output current entry and its meta-data:
            # FIXXME: had to disable the following lines because of:
            #   str([x[1] for x in sorted(entry.items(), key=lambda t: t[0])]))
            #     AttributeError: 'unicode' object has no attribute 'items'
            # self.logging.debug(" processing entry [" + str(repr(entry)) +
            #                   "]   <--------------\nwith [checksum, created, timestamp]:\n  md " +
            # str([x[1] for x in sorted(entry.items(), key=lambda t: t[0])]))
            if previous_metadata is not None:
                if entry in previous_metadata.keys():
                    self.logging.debug(
                        "\nprev " + str([x[1] for x in sorted(previous_metadata[entry].items(), key=lambda t: t[0])]))
                else:
                    self.logging.debug(
                        "no previous metadata found for this entry")

            if previous_metadata is None:
                self.logging.debug(
                    "case 2: brand-new entry (first run of lazyblorg)")
                generate.append(entry)
                marked_for_feed.append(entry)
                continue

            if entry not in previous_metadata.keys():
                self.logging.debug(
                    "case 2: brand-new entry (lazyblorg was run previously)")
                generate.append(entry)
                marked_for_feed.append(entry)
                continue

            elif 'created' not in metadata[entry].keys():
                self.logging.debug(
                    "case 3: \"created\" missing -> WARN, ignore")
                message = "entry [" + entry + \
                    "] is missing its CREATED property. Will be ignored, until you fix it."
                Utils.append_logfile_entry(
                    self.options.logfilename, 'warn', message)
                self.logging.warn(message)
                continue

            elif metadata[entry]['created'] != previous_metadata[entry]['created']:
                self.logging.debug(
                    "case 4: \"created\" differs -> WARN, ignore")
                message = "CREATED property of entry [" + entry + "] has changed which should never happen. " + \
                    "Entry will be ignored this run. Will be created next run if CREATED will not change any more."
                Utils.append_logfile_entry(
                    self.options.logfilename, 'warn', message)
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
                self.logging.debug(
                    "case 8: normal update -> generate, mark_for_feed, increment_version")
                generate.append(entry)
                marked_for_feed.append(entry)
                increment_version.append(entry)
                continue

            else:
                # warn (should never be reached)
                message = "compare_blog_metadata() is confused with entry [" + entry + "] which " + \
                    "reached an undefined situation when comparing meta-data. You can re-run. " + \
                    "If this warning re-appears, please use \"--verbose\" and check entry."
                Utils.append_logfile_entry(
                    self.options.logfilename, 'warn', message)
                self.logging.warn(message)

        return generate, marked_for_feed, increment_version


if __name__ == "__main__":

    mydescription = u"An Org-mode to HTML-blog system for very lazy people. Please refer to \n" + \
        "https://github.com/novoid/lazyblorg for more information."

    parser = ArgumentParser(prog=argv[0],
                            # keep line breaks in EPILOG and such
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog=EPILOG,
                            description=mydescription)

    parser.add_argument(
        "--orgfiles",
        dest="orgfiles",
        nargs='+',
        metavar='ORGFILE',
        required=True,
        help="One or more Org-mode files which contains all blog articles (and possible other stuff).")

    parser.add_argument(
        "--targetdir",
        dest="targetdir",
        metavar='DIR',
        required=True,
        help="Path where the HTML files will be written to. " +
        "On first run, this should be an empty directory.")

    parser.add_argument(
        "--previous-metadata",
        dest="previous_metadatafilename",
        metavar='FILE',
        required=True,
        help="Path to a file where persistent meta-data of the previous blog run " +
        "was written to. It will be read and used for comparison to the current run, the current situation." +
        "Therefore, this file can be missing in the first run.")

    parser.add_argument(
        "--new-metadata",
        dest="new_metadatafilename",
        metavar='FILE',
        required=True,
        help="Path to a file where persistent meta-data of the blog entries of the current run " +
        "is written to.")

    parser.add_argument(
        "--logfile",
        dest="logfilename",
        metavar='ORGFILE',
        required=True,
        help="Path to a file where warnings (inactive time-stamps) and errors " +
        "(active time-stamps) are being appended in Org-mode format. " +
        "It is highly recommended, that you add this file to your agenda list.")

    parser.add_argument(
        "--autotag-language",
        dest="autotag_language",
        action="store_true",
        help="Enable guessing of the language of a blog entry and using this as an auto-tag.")

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Enable verbose mode which is quite chatty - be warned.")

    parser.add_argument(
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        help="Enable quiet mode: only warnings and errors will be reported.")

    parser.add_argument("--version", dest="version", action="store_true",
                        help="Display version and exit.")

    options = parser.parse_args()

    logging = Utils.initialize_logging(
        "lazyblorg", options.verbose, options.quiet)

    try:

        if options.version:
            print os.path.basename(argv[0]) + " version " + PROG_VERSION_NUMBER + \
                " from " + PROG_VERSION_DATE
            exit(0)

        # checking parameters ...

        # if not options.logfilename:
        ##    logging.critical("Please give me a file to write to with option \"--logfile\".")
        # Utils.error_exit(5)

        if not os.path.isfile(options.logfilename):
            logging.debug(
                "log file \"" +
                options.logfilename +
                "\" is not found. Initializing with heading ...")
            with codecs.open(options.logfilename, 'w', encoding='utf-8') as outputhandle:
                outputhandle.write(
                    u"## -*- coding: utf-8 -*-\n" +
                    "## This file is best viewed with GNU Emacs Org-mode: http://orgmode.org/\n" +
                    "* Warnings and Error messages from lazyblorg     :lazyblorg:log:\n\n" +
                    "Messages gets appended to this file. Please remove fixed issues manually.\n\n")
                outputhandle.flush()

        if options.verbose and options.quiet:
            logging.error("Options \"--verbose\" and \"--quiet\" found. " +
                          "This does not make any sense, you silly fool :-)")
            Utils.error_exit(1)

        if not os.path.isdir(options.targetdir):
            logging.critical(
                "Target directory \"" +
                options.targetdir +
                "\" is not a directory. Aborting.")
            Utils.error_exit(3)

        if not os.path.isfile(options.previous_metadatafilename):
            logging.warn(
                "Blog data file \"" +
                options.previous_metadatafilename +
                "\" is not found. Assuming first run!")

        logging.debug("extracting list of Org-mode files ...")
        logging.debug("len(orgfiles) [%s]" % str(len(options.orgfiles)))
        if len(options.orgfiles) < 1:
            logging.critical(
                "Please add at least one Org-mode file name as argument")
            Utils.error_exit(6)

        # print file names if less than 10:
        if len(options.orgfiles) < 10:
            logging.debug("%s filenames found: [%s]" % (
                str(len(options.orgfiles)), '], ['.join(options.orgfiles)))
        else:
            logging.debug("%s filenames found")

        # main algorithm:

        time_before_parsing = time()
        lazyblorg = Lazyblorg(options, logging)
        # FIXXME: encapsulate following lines in lazyblorg.run() ?
        # lazyblorg.parse_HTML_output_template_and_generate_template_definitions()
        generate, marked_for_feed, increment_version, stats_parsed_org_files, stats_parsed_org_lines = lazyblorg.determine_changes()
        time_after_parsing = time()
        stats_generated_total, stats_generated_temporal, \
            stats_generated_persistent, stats_generated_tags = lazyblorg.generate_output(
                generate, marked_for_feed, increment_version)
        time_after_htmlizing = time()

        logging.info(
            "Parsed " +
            str(stats_parsed_org_files) +
            " Org-mode files with " +
            str(stats_parsed_org_lines) +
            " lines (in %.2f seconds)" %
            (time_after_parsing -
             time_before_parsing))
        logging.info(
            "Generated " +
            str(stats_generated_total) +
            " articles: " +
            str(stats_generated_persistent) +
            " persistent, " +
            str(stats_generated_temporal) +
            " temporal, " +
            str(stats_generated_tags) +
            " tag" +
            ", 1 entry page (in %.2f seconds)" %
            (time_after_htmlizing -
             time_after_parsing))

        logging.debug("-------------> cleaning up the stage ...")

        logging.debug("successfully finished.")

    except KeyboardInterrupt:

        logging.info("Received KeyboardInterrupt")

## END OF FILE ###########################################################
# Local Variables:
# DISABLEDmode: flyspell
# DISABLEDeval: (ispell-change-dictionary "en_US")
# End:
