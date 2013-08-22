#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2013-08-22 14:30:10 vk>

## TODO:
## * fix parts marked with «FIXXME»

## ===================================================================== ##
##  You might not want to modify anything below this line if you do not  ##
##  know, what you are doing :-)                                         ##
## ===================================================================== ##

import re
import os
import logging
import datetime
import sys
from optparse import OptionParser
from lib.utils import *
from lib.orgparser import *
import pickle  ## for serializing and storing objects into files

## debugging:   for setting a breakpoint:  pdb.set_trace()## FIXXME
import pdb

PROG_VERSION_NUMBER = u"0.1"
PROG_VERSION_DATE = u"2013-05-20"
INVOCATION_TIME = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

USAGE = u"\n\
    " + sys.argv[0] + u" [<options>] FIXXME\n\
\n\
FIXXME\n\
\n\
Example usage:\n\
  " + sys.argv[0] + u" FIXXME\n\
      ... FIXXME\n\
\n\
For all command line options, please call: " + sys.argv[0] + u" --help\n\
\n\
\n\
:copyright: (c) 2013 by Karl Voit <tools@Karl-Voit.at>\n\
:license: GPL v3 or any later version\n\
:URL: https://github.com/novoid/lazyblorg\n\
:bugreports: via github or <tools@Karl-Voit.at>\n\
:version: " + PROG_VERSION_NUMBER + " from " + PROG_VERSION_DATE + "\n"


## file names containing tags matches following regular expression
## FIXXME or delete
MENTIONS_REGEX = re.compile(r'', re.M)

## regular expression of FIXXME
## FIXXME or delete!
## examples: FIXXME
TIME_REGEX = re.compile('^(\w+) (\w+) (\d+) (\d\d):(\d\d):(\d\d) \+\d+ (\d\d\d\d)$')

## dictionary of months
MONTHS = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05',
          'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09',
          'Oct': '10', 'Nov': '11', 'Dec': '12'}

parser = OptionParser(usage=USAGE)

parser.add_option("--targetdir", dest="targetdir",
                  help="path where the HTML files will be written to")

parser.add_option("--metadata", dest="metadatafilename",
                  help="path to a file where persistent meta-data of the blog entries " +
                  "is written to. Next run, it will be read and used for comparison to current situation.")

parser.add_option("--template", dest="templatefilename",
                  help="path to a file which holds the output template definitions.")

parser.add_option("--logfile", dest="logfilename",
                  help="path to a file where warnings (inactive time-stamps) and errors " +
                  "(active time-stamps) are being appended in Org-mode format.")

parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  help="enable verbose mode which is quite chatty")

parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
                  help="enable quiet mode")

parser.add_option("--version", dest="version", action="store_true",
                  help="display version and exit")

(options, args) = parser.parse_args()


## format of the storage file
## pickle offers, e.g., 0 (ASCII; human-readable) or pickle.HIGHEST_PROTOCOL (binary; more efficient)
#PICKLE_FORMAT = pickle.HIGHEST_PROTOCOL
PICKLE_FORMAT = 0


def check_parameters(options):

    if not options.logfilename:
        logging.critical("Please give me a file to write to with option \"--logfile\".")
        Utils.error_exit(5)

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

    if not options.targetdir:
        logging.critical("Please give me a folder to write to with option \"--targetdir\".")
        Utils.error_exit(2)

    if not os.path.isdir(options.targetdir):
        logging.critical("Target directory \"" + options.targetdir + "\" is not a directory. Aborting.")
        Utils.error_exit(3)

    if not options.metadatafilename:
        logging.critical("Please give me a file to write to with option \"--metadata\".")
        Utils.error_exit(4)

    if not os.path.isfile(options.templatefilename):
        logging.warn("Blog data file \"" + options.templatefilename + "\" is not found. Assuming first run!")

    if not options.templatefilename:
        logging.critical("Please give me a file which holds the template definitions with option \"--template\".")
        Utils.error_exit(7)

    if not os.path.isfile(options.metadatafilename):
        logging.warn("Blog data file \"" + options.metadatafilename + "\" is not found. Assuming first run!")

    logging.debug("extracting list of Org-mode files ...")
    logging.debug("len(args) [%s]" % str(len(args)))
    if len(args) < 1:
        logging.critical("Please add at least one Org-mode file name as argument")
        Utils.error_exit(6)


def handle_file(filename):
    """
    This function handles the communication with the parser object and returns the blog data.

    @param filename: string containing one file name
    @param return: array containing parsed Org-mode data
    """

    if os.path.isdir(filename):
        logging.warning("Skipping directory \"%s\" because this tool only parses files." % filename)
        return
    elif not os.path.isfile(filename):
        logging.warning("Skipping non-file \"%s\" because this tool only parses files." % filename)
        return

    parser = OrgParser(filename)

    return parser.parse_orgmode_file()


def parse_HTML_output_template(filename):
    """
    This function parses an Org-mode file which holds the definitions of the output format.

    @param filename: string containing one file name of the definition file
    @param return: dict containing parsed template definitions
    """

    template_parser = OrgParser(filename)

    return template_parser.parse_orgmode_file()


def check_and_filter_template_definitions(all_template_data):
    """
    This function checks for (only) basic format definitions and exits
    if something important is missing.

    @param all_template_data: list which contains the format data of the template
    @param return: list of HTML definitions as Org-mode HTML block list-elements
    """

    logging.debug('checking for basic template definitions in parsed data ...')

    if not all_template_data:
        message = "Sorry, no suitable data could be parsed from the template definition file. " + \
            "Please check if it meets all criteria as described in the original template " + \
            "file \"blog-format.org\"."
        Utils.error_exit_with_userlog(options.logfilename, 40, message)

    matching_title_template_data = [entry for entry in all_template_data if entry['title'] == u'Templates']

    if not matching_title_template_data:
        message = "Sorry, no suitable data within heading \"Templates\" could be found in " + \
            "the template definition file. " + \
            "Please check if you mistyped its name."
        Utils.error_exit_with_userlog(options.logfilename, 41, message)

    html_definitions = [x for x in matching_title_template_data[0]['content'] if x[0] == 'html-block']

    found_elements = [x[1] for x in html_definitions]

    for element in [u'header', u'footer', u'article-header-begin', u'tags-begin',
                    u'tag', u'tags-end', u'article-header-end', u'article-end',
                    u'section-begin', u'section-end', u'paragraph', u'a-href',
                    u'ul-begin', u'ul-item', u'ul-end', u'pre-begin', u'pre-end']:
        if not element in found_elements:
            message = "Sorry, no definition for element \"" + element + "\" could be found within " + \
                "the template definition file. " + \
                "Please check if you mistyped its name or similar."
            Utils.error_exit_with_userlog(options.logfilename, 42, message)

    return html_definitions


def main():
    """Main function"""

    if options.version:
        print os.path.basename(sys.argv[0]) + " version " + PROG_VERSION_NUMBER + \
            " from " + PROG_VERSION_DATE
        sys.exit(0)

    logging = Utils.initialize_logging("lazyblorg", options.verbose, options.quiet)

    ## checking parameters ...

    check_parameters(options)

    files = args

    ## print file names if less than 10:
    if len(files) < 10:
        logging.debug("%s filenames found: [%s]" % (str(len(files)), '], ['.join(files)))
    else:
        logging.debug("%s filenames found")

    ## start processing Org-mode files ...

    blog_data = []

    logging.debug("iterate over files ...")
    for filename in files:
        try:
            file_blog_data = handle_file(filename)  ## parsing one Org-mode file
        except OrgParserException as message:
            verbose_message = "Parsing error in file \"" + filename + \
                "\" which is not good. Therefore, I stop here and hope you " + \
                "can fix the issue in the Org-mode file. Reason: " + message.value
            Utils.error_exit_with_userlog(options.logfilename, 20, verbose_message)
        else:
            blog_data.extend(file_blog_data)

    ## dump blogdata for debugging purpose ...
    if options.verbose:
        with open('lazyblorg_dump_of_blogdata_from_last_verbose_run.pk', 'wb') as output:
            pickle.dump(blog_data, output, 0)  ## always use ASCII format: easier to debug from outside

    ## generate persistent data which is used to compare this status
    ## with the status of the next invocation:
    metadata = Utils.generate_metadata_from_blogdata(blog_data)

    ## write this status to the persistent data file:
    with open(options.metadatafilename + '_temp', 'wb') as output:
        pickle.dump(metadata, output, PICKLE_FORMAT)

    template_data = parse_HTML_output_template(options.templatefilename)

    template_definitions = check_and_filter_template_definitions(template_data)

    ## load old metadata from file
    previous_metadata = None
    if os.path.isfile(options.metadatafilename):
        logging.debug("reading old \"" + options.metadatafilename + "\" ...")
        with open(options.metadatafilename, 'rb') as input:
            previous_metadata = pickle.load(input)

    ## FIXXME: run comparing algorithm (last metadata, current metadata) and generate pages
    ## (previous_metadata, metadata, blog_data, options.tagetdir)

    ## FIXXME: generate new RSS feed

    ## remove old options.metadatafilename
    if os.path.isfile(options.metadatafilename):
        logging.debug("deleting old \"" + options.metadatafilename + "\" ...")
        os.remove(options.metadatafilename)

          ## rename options.metadatafilename + '_temp' -> options.metadatafilename
        logging.debug("removing temporary \"" + options.metadatafilename + "_temp\" to \"" +
                      options.metadatafilename + "\" ...")
        os.rename(options.metadatafilename + '_temp', options.metadatafilename)

    logging.debug("successfully finished.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:

        logging.info("Received KeyboardInterrupt")

## END OF FILE #################################################################

#end
