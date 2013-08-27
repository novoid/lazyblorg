# -*- coding: utf-8 -*-
# Time-stamp: <2013-08-27 12:32:07 vk>

import sys
import logging
from hashlib import md5  ## generating checksums
import time  ## for generating Org-mode timestamps
from orgformat import *
import pdb


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
                assert('created' in entry.keys())
                assert('timestamp' in entry.keys())
                metadata[entry['id']] = {'created': entry['created'],
                                         'timestamp': entry['timestamp'],
                                         'checksum': checksum}

        return metadata

    @staticmethod
    def list_of_dicts_are_equal(list1, list2, ignoreorder=False):
        """

        Dicts in Python are not sorted. So there is no simple
        comparison of dicts. This method compares two list containing
        dicts entry by entry.

        @param list1: a list containing dicts with key/value-pairs
        @param list2: a list containing dicts with key/value-pairs
        @param ignoreorder: consider two lists with different order but same content as equal
        @param return: True (if list1 equals list2) or False (otherwise)
        """

        logger = logging.getLogger('lazyblorg.Utils.list_of_dicts_are_equal')
        logger.debug("list_of_dicts_are_equal called")

        assert type(list1) == list
        assert type(list2) == list

        if len(list1) > 0:
            assert type(list1[0]) == dict
        if len(list2) > 0:
            assert type(list2[0]) == dict

        if len(list1) != len(list2):
            ## quick check: if length differs, they are definitely different
            return False

        comparisonlist1 = list1
        comparisonlist2 = list2
        if ignoreorder:
            comparisonlist1 = sorted(list1)
            comparisonlist2 = sorted(list2)
        
        for entry in range(len(comparisonlist1)):
            ## do the hard way: comparing content
            if not comparisonlist1[entry] == comparisonlist2[entry]:
                return False

        return True

    @staticmethod
    def __UNFINISHED_datastructs_are_equal(data1, data2, ignoreorder=False):
        """

        Comparing data structures is easy. However, if the order of
        lists is not important, there is no simple comparison. This
        method compares two data structures containing numbers, lists,
        or dicts entry by entry. Any parameter of type 'None' returns
        False.

        data1 or data2 could be of type: number, string, unicode,
        list, or dict

        NOTE: this method does NOT work properly yet. However, I do
        not need it this time. Please refer to tests/utils_test.py for
        test cases that show what is working or not.

        @param data1: first data structure to compare
        @param data2: second data structure to compare
        @param ignoreorder: consider two items with different order but same content as equal
        @param return: True (if data1 equals data2) or False (otherwise)
        """

        if not ignoreorder:
            return data1 == data2

        #pdb.set_trace()## FIXXME

        if data1 == None or data2 == None:
            ## both arguments should exist
            return False

        elif type(data1) != type(data2):
            return False

        elif type(data1) in [int, float, long, complex, str, unicode]:
            return data1 == data2

        elif type(data1) == dict:

            ##return Utils.dicts_are_equal(data1, data2, ignoreorder)
            ## -> if dicts contain lists, this does not compare the list content!

            ## check for trivial cases:
            if len(data1.keys()) != len(data2.keys()):
                return False
            if len(data1.keys()) == 0:
                return True

            ## FIXXME: sorting the dict might be unnecessary since: {3:4, 'b':2} == {'b':2, 3:4}
            ## dicts don't keep the order (unless using Ordered....)
            sorted1 = sorted(data1.items(), key=lambda t: t[0])
            sorted2 = sorted(data2.items(), key=lambda t: t[0])
            if sorted1 == sorted2:
                ## if this is true, we do not have to walk through the content
                return True
            else:
                ## sorted1/2 are lists of tuples now. Compare them:
                Utils.datastructs_are_equal(sorted1, sorted2, ignoreorder)

        
        elif type(data1) == list:

            ## check for trivial cases:
            if len(data1) != len(data2):
                return False
            if len(data1) == 0:
                return True

            sorted1 = sorted(data1)
            sorted2 = sorted(data2)
            if sorted1 == sorted2:
                ## if this is true, we do not have to walk through the content
                return True
            else:
                for element in range(len(sorted1)):
                    Utils.datastructs_are_equal(sorted1[element], sorted2[element], ignoreorder)

        else:
            logger = logging.getLogger('lazyblorg.Utils.datastructs_are_equal')
            logger.error("datastructs_are_equal() does not support parameters of type \"%s\" yet." % type(data1))
            return False
        

# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
