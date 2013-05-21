# -*- coding: utf-8 -*-
# Time-stamp: <2013-05-20 17:52:44 vk>

import re
import sys
import logging
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

# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
