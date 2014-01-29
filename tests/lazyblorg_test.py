#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2014-01-29 21:40:37 vk>

import argparse  ## command line arguments
import unittest
from lazyblorg import Lazyblorg
from lib.utils import *
from lib.orgparser import *
import pickle ## for serializing and storing objects into files
from os import remove

## debugging:   for setting a breakpoint:  pdb.set_trace()## FIXXME
import pdb

class TestLazyblorg(unittest.TestCase):

    ## FIXXME: (Note) These test are *not* exhaustive unit tests. They only
    ##         show the usage of the methods. Please add "mean" test cases and
    ##         borderline cases!

    logging = None


    def setUp(self):
        verbose = False
        quiet = False
        self.logging = Utils.initialize_logging("lazyblorg", verbose, quiet)


    def tearDown(self):
        pass


    def test_parse_HTML_output_template_and_generate_template_definitions(self):

        ## FIXXME: implement!
        pass


    def test_determine_changes(self):

        ## Checks on the situation before first iteration:

        ## manually written Org-mode file; has to be placed in "../testdata/basic_blog_update_test/"
        template_file = "../templates/blog-format.org"
        org_testfile_firstrun = "../testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.org"
        metadata_firstrun_output = "../testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.pk"
        metadata_secondrun_input = "../testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.pk_temp"
        log_firstrun = "../testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.log"
        org_testfile_secondrun = "../testdata/basic_blog_update_test/basic_blog_update_test_-_second_run.org"

        ## might be left over from a failed previous run:
        if os.path.isfile(metadata_secondrun_input):
            remove(metadata_secondrun_input)

        ## might be left over from a failed previous run:
        if os.path.isfile(log_firstrun):
            remove(log_firstrun)

        self.assertTrue(os.path.isfile(template_file))  ## check, if test input file is found
        self.assertTrue(os.path.isfile(org_testfile_firstrun))  ## check, if test input file is found
        self.assertTrue(os.path.isfile(org_testfile_secondrun))  ## check, if test input file is found
        
        ## should not be found yet because test will generate them:
        self.assertFalse(os.path.isfile(metadata_firstrun_output))

        ## Building the call parameters:

        first_parser = argparse.ArgumentParser()
        first_parser.add_argument("--orgfiles", dest="orgfiles", nargs='+')
        first_parser.add_argument("--targetdir", dest="targetdir")
        first_parser.add_argument("--metadata", dest="metadatafilename")
        first_parser.add_argument("--logfile", dest="logfilename")
        first_parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")

        myoptions = "--orgfiles " + org_testfile_firstrun + " " + template_file + \
            " --targetdir ../testdata/basic_blog_update_test/2del-results/ --metadata " + \
            metadata_firstrun_output + \
            " --logfile " + log_firstrun# + " --verbose"

        options = first_parser.parse_args(myoptions.split())

        ## Invoking lazyblorg first interation:

        first_lazyblorg = Lazyblorg(options, self.logging)
        generate, marked_for_RSS, increment_version = first_lazyblorg.determine_changes()

        ## Checking results:

        generate_sorted = sorted(generate)
        marked_for_RSS_sorted = sorted(marked_for_RSS)
        ##increment_version_sorted = sorted(increment_version)

        self.assertTrue(increment_version == [])
        self.assertTrue(generate_sorted == marked_for_RSS_sorted)
        self.assertTrue(generate_sorted == [u'case4', u'case5', u'case6', u'case7', u'case8', u'lazyblorg-templates'])

        ## Checks on the situation before second iteration:

        self.assertTrue(os.path.isfile(org_testfile_secondrun))  ## check, if test input file is found
        self.assertTrue(os.path.isfile(metadata_secondrun_input))

        ## Building the call parameters:

        second_parser = argparse.ArgumentParser()
        second_parser.add_argument("--orgfiles", dest="orgfiles", nargs='+')
        second_parser.add_argument("--targetdir", dest="targetdir")
        second_parser.add_argument("--metadata", dest="metadatafilename")
        second_parser.add_argument("--logfile", dest="logfilename")
        second_parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")

        myoptions = "--orgfiles " + org_testfile_secondrun + " " + template_file + \
            " --targetdir ../testdata/basic_blog_update_test/2del-results/ --metadata " + \
            metadata_secondrun_input + \
            " --logfile " + log_firstrun# + " --verbose"

        options = second_parser.parse_args(myoptions.split())

        ## Invoking lazyblorg first interation:

        second_lazyblorg = Lazyblorg(options, self.logging)
        generate, marked_for_RSS, increment_version = second_lazyblorg.determine_changes()

        ## Checking results:

        generate_sorted = sorted(generate)
        marked_for_RSS_sorted = sorted(marked_for_RSS)
        increment_version_sorted = sorted(increment_version)

        self.assertTrue(increment_version_sorted == [u'case8'])
        self.assertTrue(marked_for_RSS_sorted == [u'case1', u'case8'])
        self.assertTrue(generate_sorted == [u'case1', u'case5', u'case6', u'case7', u'case8', u'lazyblorg-templates'])

        remove(metadata_secondrun_input)
        if os.path.isfile(metadata_secondrun_input + '_temp'):
            remove(metadata_secondrun_input + '_temp')
        if os.path.isfile(log_firstrun):
            remove(log_firstrun)
        
        return


## END OF FILE #################################################################
# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
