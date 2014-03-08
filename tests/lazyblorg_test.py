#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2014-03-08 20:39:52 vk>

import argparse  ## command line arguments
import unittest
from lazyblorg import Lazyblorg
from lib.utils import *
from lib.orgparser import *
from lib.htmlizer import *
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
        metadata_secondrun_output = "../testdata/basic_blog_update_test/basic_blog_update_test_-_second_run.pk"
        log_firstrun = "../testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.log"
        org_testfile_secondrun = "../testdata/basic_blog_update_test/basic_blog_update_test_-_second_run.org"

        ## might be left over from a failed previous run:
        if os.path.isfile(metadata_firstrun_output):
            remove(metadata_firstrun_output)

        ## might be left over from a failed previous run:
        if os.path.isfile(log_firstrun):
            remove(log_firstrun)

        self.assertTrue(os.path.isfile(template_file))  ## check, if test input file is found
        self.assertTrue(os.path.isfile(org_testfile_firstrun))  ## check, if test input file is found
        self.assertTrue(os.path.isfile(org_testfile_secondrun))  ## check, if test input file is found
        
        ## Building the call parameters:

        first_parser = argparse.ArgumentParser()
        first_parser.add_argument("--orgfiles", dest="orgfiles", nargs='+')
        first_parser.add_argument("--targetdir", dest="targetdir")
        first_parser.add_argument("--new-metadata", dest="new_metadatafilename")
        first_parser.add_argument("--previous-metadata", dest="previous_metadatafilename")
        first_parser.add_argument("--logfile", dest="logfilename")
        first_parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")

        myoptions = "--orgfiles " + org_testfile_firstrun + " " + template_file + \
            " --targetdir ../testdata/basic_blog_update_test/2del-results/ --previous-metadata NOTEXISTING.pk --new-metadata " + \
            metadata_firstrun_output + \
            " --logfile " + log_firstrun# + " --verbose"

        options = first_parser.parse_args(myoptions.split())

        ## Invoking lazyblorg first interation:

        first_lazyblorg = Lazyblorg(options, self.logging)
        generate, marked_for_RSS, increment_version, stats_parsed_org_files, stats_parsed_org_lines = first_lazyblorg.determine_changes()

        ## Checking results:

        generate_sorted = sorted(generate)
        marked_for_RSS_sorted = sorted(marked_for_RSS)
        ##increment_version_sorted = sorted(increment_version)

        self.assertTrue(increment_version == [])
        self.assertTrue(generate_sorted == marked_for_RSS_sorted)
        self.assertTrue(generate_sorted == [u'case4', u'case5', u'case6', u'case7', u'case8', u'lazyblorg-templates'])

        ## Checks on the situation before second iteration:

        ## none

        ## Building the call parameters:

        second_parser = argparse.ArgumentParser()
        second_parser.add_argument("--orgfiles", dest="orgfiles", nargs='+')
        second_parser.add_argument("--targetdir", dest="targetdir")
        second_parser.add_argument("--new-metadata", dest="new_metadatafilename")
        second_parser.add_argument("--previous-metadata", dest="previous_metadatafilename")
        second_parser.add_argument("--logfile", dest="logfilename")
        second_parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")

        myoptions = "--orgfiles " + org_testfile_secondrun + " " + template_file + \
            " --targetdir ../testdata/basic_blog_update_test/2del-results/ --previous-metadata " + \
            metadata_firstrun_output + \
            " --new-metadata " + metadata_secondrun_output + " --logfile " + log_firstrun# + " --verbose"

        options = second_parser.parse_args(myoptions.split())

        ## Invoking lazyblorg first interation:

        second_lazyblorg = Lazyblorg(options, self.logging)
        generate, marked_for_RSS, increment_version, stats_parsed_org_files, stats_parsed_org_lines = second_lazyblorg.determine_changes()

        ## Checking results:

        generate_sorted = sorted(generate)
        marked_for_RSS_sorted = sorted(marked_for_RSS)
        increment_version_sorted = sorted(increment_version)

        self.assertTrue(increment_version_sorted == [u'case8'])
        self.assertTrue(marked_for_RSS_sorted == [u'case1', u'case8'])
        self.assertTrue(generate_sorted == [u'case1', u'case5', u'case6', u'case7', u'case8', u'lazyblorg-templates'])

        if os.path.isfile(log_firstrun):
            remove(log_firstrun)

        remove(metadata_firstrun_output)
        remove(metadata_secondrun_output)

        return

    def test_example_entry_with_all_implemented_orgmode_elements(self):

        ## Checks on the situation before first iteration:

        ## manually written Org-mode file; has to be placed in "../testdata/basic_blog_update_test/"
        testname = "currently_supported_orgmode_syntax"
        template_file = "../templates/blog-format.org"
        org_testfile = "../testdata/" + testname + ".org"
        metadata_output = "../testdata/" + testname + ".pk"
        metadata_input = "../testdata/nonexisting.pk"
        log_firstrun = "../testdata/" + testname + ".log"
        target_dir = "../testdata/"

        ## might be left over from a failed previous run:
        if os.path.isfile(metadata_output):
            remove(metadata_output)

        ## might be left over from a failed previous run:
        if os.path.isfile(log_firstrun):
            remove(log_firstrun)

        self.assertTrue(os.path.isfile(template_file))  ## check, if test input file is found
        self.assertTrue(os.path.isfile(org_testfile))  ## check, if test input file is found
        
        ## Building the call parameters:
        first_parser = argparse.ArgumentParser()
        first_parser.add_argument("--orgfiles", dest="orgfiles", nargs='+')
        first_parser.add_argument("--targetdir", dest="targetdir")
        first_parser.add_argument("--new-metadata", dest="new_metadatafilename")
        first_parser.add_argument("--previous-metadata", dest="previous_metadatafilename")
        first_parser.add_argument("--logfile", dest="logfilename")
        first_parser.add_argument("-v", "--verbose", dest="verbose", action="store_true")

        myoptions = "--orgfiles " + org_testfile + " " + template_file + \
            " --targetdir " + target_dir + " --previous-metadata " + metadata_input + " --new-metadata " + \
            metadata_output + \
            " --logfile " + log_firstrun# + " --verbose"

        options = first_parser.parse_args(myoptions.split())

        ## Invoking lazyblorg first interation:

        mylazyblorg = Lazyblorg(options, self.logging)
        generate, marked_for_RSS, increment_version, stats_parsed_org_files, stats_parsed_org_lines = mylazyblorg.determine_changes()

        ## Checking results:

        generate_sorted = sorted(generate)
        marked_for_RSS_sorted = sorted(marked_for_RSS)

        self.assertTrue(increment_version == [])
        self.assertTrue(generate_sorted == marked_for_RSS_sorted)
        self.assertTrue(generate_sorted == [u'2014-01-27-full-syntax-test', u'lazyblorg-templates'])

        blog_data, stats_parsed_org_lines = mylazyblorg._parse_orgmode_file(org_testfile)
        template_blog_data, template_stats_parsed_org_lines = mylazyblorg._parse_orgmode_file(template_file)
        blog_data += template_blog_data
        
        ## extract HTML templates and store in class var
        template_definitions = mylazyblorg._generate_template_definitions_from_template_data()

        htmlizer = Htmlizer(template_definitions, testname, "blog", "about this blog",
                            target_dir, blog_data, generate, increment_version)

        filename = htmlcontent = None
        for entry in blog_data:

            entry = htmlizer.sanitize_and_htmlize_blog_content(entry)

            if entry['category'] == htmlizer.TEMPORAL:
                filename, orgfilename, htmlcontent = htmlizer._generate_temporal_article(entry)

        htmloutputname = "../testdata/" + testname + ".html"
                
        ## generating HTML output in order to manually check in browser as well:
        with codecs.open(htmloutputname, 'wb', encoding='utf-8') as output:
            output.write(htmlcontent)

        self.assertTrue(os.path.isfile(htmloutputname))
            
        ## read in generated data from file:
        contentarray_from_file = []
        with codecs.open(htmloutputname, 'r', encoding='utf-8') as input:
            contentarray_from_file = input.readlines()

        ## read in comparson data from file:
        comparisonfilename = "../testdata/" + testname + "_COMPARISON.html"
        comparison_file_content = None
        with codecs.open(comparisonfilename, 'r', encoding='utf-8') as input:
            comparison_string_array = input.readlines()

        if len(comparison_string_array) != len(contentarray_from_file):
            print "length of produced data (" + str(len(contentarray_from_file)) + ") differs from comparison data (" + str(len(comparison_string_array)) + ")"
        
        ## a more fine-grained diff (only) on the first element in blog_data:
        for line in range(len(comparison_string_array)): 
            if contentarray_from_file[line].rstrip() != comparison_string_array[line].rstrip(): 
                print "=================  first difference  ===================== in line " + str(line)
                print "       [" + contentarray_from_file[line-1].rstrip() + "]"
                print "found  [" + contentarray_from_file[line].rstrip() + "]"
                print "       [" + contentarray_from_file[line+1].rstrip() + "]"
                print "    ---------------  comparison data:  --------------------"
                print "       [" + comparison_string_array[line-1].rstrip() + "]"
                print "should [" + comparison_string_array[line].rstrip() + "]"
                print "       [" + comparison_string_array[line+1].rstrip() + "]"
                print "=================                    ====================="
                self.assertTrue(contentarray_from_file[line].rstrip() == comparison_string_array[line].rstrip())
                    
        if os.path.isfile(metadata_output):
            remove(metadata_output)

        if os.path.isdir("../testdata/" + testname):
            import shutil
            shutil.rmtree("../testdata/" + testname)
            #import pdb; pdb.set_trace()


## END OF FILE #################################################################
# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
