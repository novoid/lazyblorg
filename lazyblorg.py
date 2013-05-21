#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2013-05-21 15:51:43 vk>

## TODO:
## * fix parts marked with «FIXXME»

## ===================================================================== ##
##  You might not want to modify anything below this line if you do not  ##
##  know, what you are doing :-)                                         ##
## ===================================================================== ##

import re
import os
import json
import logging
import datetime
import sys
import codecs
from optparse import OptionParser
from lib.utils import *
from lib.orgparser import *

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
MENTIONS_REGEX = re.compile(r'', re.M)

TIME_REGEX = re.compile('^(\w+) (\w+) (\d+) (\d\d):(\d\d):(\d\d) \+\d+ (\d\d\d\d)$')

MONTHS = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05',
          'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09',
          'Oct': '10', 'Nov': '11', 'Dec': '12'}

parser = OptionParser(usage=USAGE)

parser.add_option("--targetdir", dest="targetdir",
                  help="directory where the HTML files will be written to")

parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  help="enable verbose mode")

parser.add_option("-q", "--quiet", dest="quiet", action="store_true",
                  help="enable quiet mode")

parser.add_option("--version", dest="version", action="store_true",
                  help="display version and exit")

(options, args) = parser.parse_args()


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

    logging.debug("extracting list of Org-mode files ...")
    logging.debug("len(args) [%s]" % str(len(args)))
    if len(args) < 1:
        Utils.error_exit(logging, 4, "Please add at least one Org-mode file name as argument")

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

    logging.debug("successfully finished.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:

        logging.info("Received KeyboardInterrupt")

## END OF FILE #################################################################

#end
