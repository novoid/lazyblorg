# -*- coding: utf-8 -*-
# Time-stamp: <2013-08-20 18:09:00 vk>

import re
import sys
import logging
from hashlib import md5  ## generating checksums
#import pdb

class Utils(object):
    """
    Class for providing misc utility methods.
    """

    def __init__(self):

        pass

    @staticmethod
    def error_exit(logging, errorcode, text):
        """
        Exits with return value of errorcode and prints to stderr.
    
        @param logging: handler for logging output
        @param errorcode: integer that will be reported as return value.
        @param text: string with descriptive error message.
        """
    
        sys.stdout.flush()
        logging.error(text)
    
        sys.exit(errorcode)


    @staticmethod
    def initialize_logging(verbose, quiet):
        """Log handling and configuration"""
    
        if verbose:
            FORMAT = "%(levelname)-8s %(asctime)-15s %(message)s"
            logging.basicConfig(level=logging.DEBUG, format=FORMAT)
        elif quiet:
            FORMAT = "%(levelname)-8s %(message)s"
            logging.basicConfig(level=logging.ERROR, format=FORMAT)
        else:
            FORMAT = "%(levelname)-8s %(message)s"
            logging.basicConfig(level=logging.INFO, format=FORMAT)

        return logging


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
                logging.error()
                Utils.error_exit(logging, 6, "We got a duplicate ID in blogdata: \"" + \
                                     str(entry['id']) + "\". Please correct it and re-run this tool.")
            else:
                metadata[entry['id']] = {'created': entry['created'], 
                                         'timestamp': entry['timestamp'], 
                                         'checksum': checksum}
            
        return metadata

# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
