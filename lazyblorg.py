#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2013-08-20 18:06:41 vk>

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
import pickle ## for serializing and storing objects into files

## debugging:   for setting a breakpoint:  pdb.set_trace()
#import pdb

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
                  help="directory where the HTML files will be written to")

parser.add_option("--metadata", dest="metadatafilename",
                  help="path to a file where persistent meta-data of the blog entries " +
                  "is written to. Next run, it will be read and used for comparison to current situation.")

parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  help="enable verbose mode")

parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
                  help="enable quiet mode")

parser.add_option("--version", dest="version", action="store_true",
                  help="display version and exit")

(options, args) = parser.parse_args()


## format of the storage file
## pickle offers, e.g., 0 (ASCII; human-readable) or pickle.HIGHEST_PROTOCOL (binary; more efficient)
#PICKLE_FORMAT = pickle.HIGHEST_PROTOCOL
PICKLE_FORMAT = 0


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

    parser = OrgParser(filename, logging)

    return parser.parse_orgmode_file()


def main():
    """Main function"""

    if options.version:
        print os.path.basename(sys.argv[0]) + " version " + PROG_VERSION_NUMBER + \
            " from " + PROG_VERSION_DATE
        sys.exit(0)

    logging = Utils.initialize_logging(options.verbose, options.quiet)

    if options.verbose and options.quiet:
        Utils.error_exit(logging, 1, "Options \"--verbose\" and \"--quiet\" found. " +
                         "This does not make any sense, you silly fool :-)")

    if not options.targetdir:
        Utils.error_exit(logging, 2, "Please give me a folder to write to with option \"--targetdir\".")

    if not os.path.isdir(options.targetdir):
        Utils.error_exit(logging, 3, "Target directory \"%s\" is not a directory. Aborting." % options.targetdir)

    if not options.metadatafilename:
        Utils.error_exit(logging, 4, "Please give me a file to write to with option \"--metadata\".")

    if not os.path.isfile(options.metadatafilename):
        logging.warning("Blog data file \"%s\" is not found. Assuming first run!" % options.metadatafilename)

    logging.debug("extracting list of Org-mode files ...")
    logging.debug("len(args) [%s]" % str(len(args)))
    if len(args) < 1:
        Utils.error_exit(logging, 5, "Please add at least one Org-mode file name as argument")

    files = args

    ## print file names if less than 10:
    if len(files) < 10:
        logging.debug("%s filenames found: [%s]" % (str(len(files)), '], ['.join(files)))
    else:
        logging.debug("%s filenames found")

    blog_data = []

    logging.debug("iterate over files ...")
    for filename in files:
        blog_data.extend(handle_file(filename))

    if options.verbose:
        ## dump blogdata for debugging purpose:
        with open('lazyblorg_dump_of_blogdata_from_last_verbose_run.pk', 'wb') as output:
            pickle.dump(blog_data, output, 0)  ## always use ASCII format

    metadata = Utils.generate_metadata_from_blogdata(blog_data)

    with open(options.metadatafilename, 'wb') as output:
        pickle.dump(metadata, output, PICKLE_FORMAT)

    logging.debug("successfully finished.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:

        logging.info("Received KeyboardInterrupt")

## END OF FILE #################################################################

#end
