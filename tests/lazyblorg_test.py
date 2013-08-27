#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2013-08-27 12:00:33 vk>

import argparse  ## command line arguments
import unittest
from lazyblorg import Lazyblorg
from lib.utils import *
from lib.orgparser import *
import pickle ## for serializing and storing objects into files
#from os import remove

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

        ## manually written Org-mode file; has to be placed in "../testdata/basic_blog_update_test/"
        org_testfile_firstrun = "../testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.org"
        metadata_firstrun_output = "../testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.pk"
        metadata_secondrun_input = "../testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.pk_temp"
        log_firstrun = "../testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.log"
        org_testfile_secondrun = "../testdata/basic_blog_update_test/basic_blog_update_test_-_second_run.org"
        template_file = "../templates/blog-format.org"
        #testfile_temp_output = "simple_org_-_lastrun.pk"
        #testfile_temp_reference = "simple_org_-_reference.pk"

        self.assertTrue(os.path.isfile(org_testfile_firstrun))  ## check, if test input file is found
        self.assertTrue(os.path.isfile(org_testfile_secondrun))  ## check, if test input file is found
        self.assertTrue(os.path.isfile(template_file))
        
        ## should not be found because test will generate them:
        self.assertFalse(os.path.isfile(metadata_firstrun_output))
        self.assertFalse(os.path.isfile(metadata_secondrun_input))
        self.assertFalse(os.path.isfile(log_firstrun))

        parser = argparse.ArgumentParser()
        parser.add_argument("--orgfiles", dest="orgfiles", nargs='+')
        parser.add_argument("--targetdir", dest="targetdir")
        parser.add_argument("--metadata", dest="metadatafilename")
        parser.add_argument("--template", dest="templatefilename")
        parser.add_argument("--logfile", dest="logfilename")
        parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")

        myoptions = "--orgfiles " + org_testfile_firstrun + \
            " --targetdir ../testdata/basic_blog_update_test/2del-results/ --metadata " + \
            metadata_firstrun_output + " --template " + template_file + \
            " --logfile " + log_firstrun# + " --verbose"

        options = parser.parse_args(myoptions.split())

        lazyblorg = Lazyblorg(options, self.logging)

        generate, marked_for_RSS, increment_version = lazyblorg.determine_changes()

        generate_sorted = sorted(generate)
        marked_for_RSS_sorted = sorted(marked_for_RSS)
        ##increment_version_sorted = sorted(increment_version)

        self.assertTrue(increment_version == [])
        self.assertTrue(generate_sorted == marked_for_RSS_sorted)
        self.assertTrue(generate_sorted == [u'case4', u'case5', u'case6', u'case7', u'case8'])

        ## FIXXME: second run!
        
        #pdb.set_trace()## FIXXME
        return

        PICKLE_FORMAT = 0

        ## make sure that no old output file is found:
        if os.path.isfile(testfile_temp_output):
            remove(testfile_temp_output)
            
        blog_data = []  ## initialize the empty list
        parser = OrgParser(testfile_org)

        ## parse the example Org-mode file:
        blog_data.extend(parser.parse_orgmode_file())

        ## write data to dump file:
        with open(testfile_temp_output, 'wb') as output:
            pickle.dump(blog_data, output, PICKLE_FORMAT)

        ## check, if dump file was created:
        self.assertTrue(os.path.isfile(testfile_temp_output))

        reference_blog_data = None

        ## read reference data from file:
        with open(testfile_temp_reference, 'r') as fileinput:
            reference_blog_data = pickle.load(fileinput)

        ## a more fine-grained diff (only) on the first element in blog_data:
        for x in range(len(blog_data[0]['content'])): 
            if blog_data[0]['content'][x] != reference_blog_data[0]['content'][x]: 
                print "   =============== difference ==================="
                print reference_blog_data[0]['content'][x]
                print "   -------------------------------"
                print blog_data[0]['content'][x]
                print "   ===============            ==================="

        self.assertTrue(Utils.list_of_dicts_are_equal(reference_blog_data, blog_data, ignoreorder=True))

        ## optionally clean up:
        #remove(testfile_temp_output)

## END OF FILE #################################################################
# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
