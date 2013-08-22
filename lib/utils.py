# -*- coding: utf-8 -*-
# Time-stamp: <2013-08-22 14:36:11 vk>

import sys
import logging
from hashlib import md5  ## generating checksums
import time  ## for generating Org-mode timestamps
from orgformat import *
#import pdb


class Utils(object):
    """
    Class for providing misc utility methods.
    """

    def __init__(self):

        pass

    @staticmethod
    def error_exit(errorcode):
        """
        Exits with return value of errorcode and prints to stderr.

        @param errorcode: integer that will be reported as return value.
        """

        logger = logging.getLogger('lazyblorg.Utils.error_exit')
        logger.debug("exiting with error code %s" % str(errorcode))

        sys.stdout.flush()
        sys.exit(errorcode)

    @staticmethod
    def error_exit_with_userlog(logfilename, errorcode, message):
        """
        Exits with return value of errorcode, prints to stderr,
        creates an entry in the user log file.

        @param logfilename: file name of the user log file
        @param errorcode: integer that will be reported as return value.
        @param message: error message
        """

        logger = logging.getLogger('lazyblorg.Utils.error_exit_with_userlog')
        logger.critical(message)
        Utils.append_logfile_entry(logfilename, 'critical', message)
        Utils.error_exit(errorcode)

    @staticmethod
    def initialize_logging(identifier, verbose, quiet):
        """Log handling and configuration"""

        logger = logging.getLogger(identifier)

        # create console handler and set level to debug
        ch = logging.StreamHandler()

        FORMAT = None
        if verbose:
            FORMAT = "%(levelname)-8s %(asctime)-15s %(message)s"
            ch.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        elif quiet:
            FORMAT = "%(levelname)-8s %(message)s"
            ch.setLevel(logging.ERROR)
            logger.setLevel(logging.ERROR)
        else:
            FORMAT = "%(levelname)-8s %(message)s"
            ch.setLevel(logging.INFO)
            logger.setLevel(logging.INFO)

        # create formatter
        formatter = logging.Formatter(FORMAT)

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

        ## omit double output (default handler and my own handler):
        logger.propagate = False

        ## # "application" code
        ## logger.debug("debug message")
        ## logger.info("info message")
        ## logger.warn("warn message")
        ## logger.error("error message")
        ## logger.critical("critical message")

        logger.debug("logging initialized")

        return logger

    @staticmethod
    def append_logfile_entry(filename, level, message):
        """Appends messages to the given log file."""

        logger = logging.getLogger('lazyblorg.Utils.append_logfile_entry')
        logger.debug("appending to Org-mode log-file %s" % (filename))

        with open(filename, 'a') as outputhandle:
            datetimestamp = OrgFormat.datetime(time.localtime())
    ## add daily repeating that user gets it on agenda also on following days:
            datetimestamp = datetimestamp[:-1] + ' +1d>'

            outputhandle.write(u"\n** " +
                               datetimestamp +
                               " lazyblorg " + level.upper() + ": " +
                               message +
                               "\n")

    @staticmethod
    def __generate_checksum_for_blog_entry(title, tags, finished_timestamp_history, content):
        """

        Creates a hash value which should be unique to the most
        important identifiers of content of a single blog entry.

        @param title: string of the blog entry title
        @param tags: list of the blog entry tags as strings
        @param finished_timestamp_history: list of datestamps containing times of changing status to finished state
        @param content: array of arrays containing the content of the blog entry
        @param return: hexadecimal value of the hash
        """

        return md5(str([title, tags, finished_timestamp_history, content])).hexdigest()

    @staticmethod
    def generate_metadata_from_blogdata(blogdata):
        """

        Parses blogdata list and extracts ID, CREATED time-stamp, most
        current time-stamp, and generates a check-sum for the
        entry. The result is written in a dict.

        @param blogdata: array of entries as described in
        "dev/lazyblorg.org > Notes > Representation of blog data"
        @param return: array containing a dict with entries like: {
        <ID>: {created: <timestamp>, timestamp: <timestamp>, checksum:
        <checksum>}, ...}
        """

        metadata = {}

        for entry in blogdata:

            checksum = Utils.__generate_checksum_for_blog_entry(entry['title'],
                                                                entry['tags'],
                                                                entry['finished-timestamp-history'],
                                                                entry['content'])

            if entry['id'] in metadata.keys():
                logging.error("We got a duplicate ID in blogdata: \"" +
                              str(entry['id']) + "\". Please correct it and re-run this tool.")
                Utils.error_exit(30)
            else:
                metadata[entry['id']] = {'created': entry['created'],
                                         'timestamp': entry['timestamp'],
                                         'checksum': checksum}

        return metadata

# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
