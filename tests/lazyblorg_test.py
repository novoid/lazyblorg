#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

import argparse  # command line arguments
import unittest
from lazyblorg import Lazyblorg
from lib.utils import Utils
import os


class TestLazyblorg(unittest.TestCase):

    # FIXXME: (Note) These test are *not* exhaustive unit tests. They only
    #         show the usage of the methods. Please add "mean" test cases and
    #         borderline cases!

    logging = None

    def setUp(self):
        verbose = False
        quiet = False
        self.logging = Utils.initialize_logging("lazyblorg", verbose, quiet)

    def tearDown(self):
        pass

    def test_parse_HTML_output_template_and_generate_template_definitions(
            self):

        # FIXXME: implement
        # test_parse_HTML_output_template_and_generate_template_definitions()
        pass

    def test_determine_changes(self):

        # Checks on the situation before first iteration:

        # manually written Org-mode file; has to be placed in
        # "../testdata/basic_blog_update_test/"
        template_file = "templates/blog-format.org"
        org_testfile_firstrun = "testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.org"
        metadata_firstrun_output = "testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.pk"
        metadata_secondrun_output = "testdata/basic_blog_update_test/basic_blog_update_test_-_second_run.pk"
        log_firstrun = "testdata/basic_blog_update_test/basic_blog_update_test_-_first_run.log"
        org_testfile_secondrun = "testdata/basic_blog_update_test/basic_blog_update_test_-_second_run.org"

        # might be left over from a failed previous run:
        if os.path.isfile(metadata_firstrun_output):
            os.remove(metadata_firstrun_output)

        # might be left over from a failed previous run:
        if os.path.isfile(log_firstrun):
            os.remove(log_firstrun)

        # check, if test input file is found
        self.assertTrue(os.path.isfile(template_file))
        # check, if test input file is found
        self.assertTrue(os.path.isfile(org_testfile_firstrun))
        # check, if test input file is found
        self.assertTrue(os.path.isfile(org_testfile_secondrun))

        # Building the call parameters:

        first_parser = argparse.ArgumentParser()
        first_parser.add_argument("--orgfiles", dest="orgfiles", nargs='+')
        first_parser.add_argument("--targetdir", dest="targetdir")
        first_parser.add_argument(
            "--new-metadata",
            dest="new_metadatafilename")
        first_parser.add_argument(
            "--previous-metadata",
            dest="previous_metadatafilename")
        first_parser.add_argument("--logfile", dest="logfilename")
        first_parser.add_argument(
            "-v",
            "--verbose",
            dest="verbose",
            action="store_true")

        myoptions = "--orgfiles " + template_file + " " + org_testfile_firstrun + \
            " --targetdir ../testdata/basic_blog_update_test/2del-results/ --previous-metadata NOTEXISTING.pk --new-metadata " + \
            metadata_firstrun_output + \
            " --logfile " + log_firstrun  # + " --verbose"

        options = first_parser.parse_args(myoptions.split())

        # Invoking lazyblorg first interation:

        first_lazyblorg = Lazyblorg(options, self.logging)
        generate, marked_for_feed, increment_version, stats_parsed_org_files, stats_parsed_org_lines = first_lazyblorg.determine_changes()

        # Checking results:

        generate_sorted = sorted(generate)
        marked_for_feed_sorted = sorted(marked_for_feed)
        # increment_version_sorted = sorted(increment_version)

        self.assertTrue(increment_version == [])
        self.assertTrue(generate_sorted == marked_for_feed_sorted)
        self.assertTrue(
            generate_sorted == [
                'case4',
                'case5',
                'case6',
                'case7',
                'case8',
                'empty-language-autotag-page',
                'lazyblorg-templates'])
        # Checks on the situation before second iteration:

        # none

        # Building the call parameters:

        second_parser = argparse.ArgumentParser()
        second_parser.add_argument("--orgfiles", dest="orgfiles", nargs='+')
        second_parser.add_argument("--targetdir", dest="targetdir")
        second_parser.add_argument(
            "--new-metadata",
            dest="new_metadatafilename")
        second_parser.add_argument(
            "--previous-metadata",
            dest="previous_metadatafilename")
        second_parser.add_argument("--logfile", dest="logfilename")
        second_parser.add_argument(
            "-v",
            "--verbose",
            dest="verbose",
            action="store_true")

        myoptions = "--orgfiles " + org_testfile_secondrun + " " + template_file + \
            " --targetdir ../testdata/basic_blog_update_test/2del-results/ --previous-metadata " + \
            metadata_firstrun_output + \
            " --new-metadata " + metadata_secondrun_output + " --logfile " + log_firstrun  # + " --verbose"

        options = second_parser.parse_args(myoptions.split())

        # Invoking lazyblorg first interation:

        second_lazyblorg = Lazyblorg(options, self.logging)
        generate, marked_for_feed, increment_version, stats_parsed_org_files, stats_parsed_org_lines = second_lazyblorg.determine_changes()

        # Checking results:

        generate_sorted = sorted(generate)
        marked_for_feed_sorted = sorted(marked_for_feed)
        increment_version_sorted = sorted(increment_version)

        self.assertTrue(increment_version_sorted == ['case8'])
        self.assertTrue(marked_for_feed_sorted == ['case1', 'case8'])
        self.assertTrue(
            generate_sorted == [
                'case1',
                'case5',
                'case6',
                'case7',
                'case8',
                'empty-language-autotag-page',
                'lazyblorg-templates'])

        if os.path.isfile(log_firstrun):
            os.remove(log_firstrun)

        os.remove(metadata_firstrun_output)
        os.remove(metadata_secondrun_output)

        return

#old#    def test_example_entry_with_all_implemented_orgmode_elements_from_org_to_html(
#old#            self):
#old#
#old#        testnames = ["test_case_from_nothing_to_DONE",
#old#                     "test_case_with_tag_page"]
#old#
#old#        for testname in testnames:
#old#
#old#            # manually written Org-mode file; has to be placed in
#old#            # "../testdata/"
#old#            generate_sorted, blog_data, metadata, increment_version, mylazyblorg, generate, metadata_output = self.generate_parser_data_from_orgmode_file(
#old#                testname)
#old#
#old#            htmloutputname = self.htmlize_parser_data_to_html_files(
#old#                testname, blog_data, metadata, increment_version, mylazyblorg, generate)
#old#            self.compare_generated_html_content_to_comparison_html_file(
#old#                testname, htmloutputname, metadata_output)
#old#
#old#    def generate_parser_data_from_orgmode_file(self, testname):
#old#
#old#        # Checks on the situation before first iteration:
#old#
#old#        # manually written Org-mode file; has to be placed in
#old#        # "../testdata/basic_blog_update_test/"
#old#        template_file = "../templates/blog-format.org"
#old#        org_testfile = "../testdata/" + testname + ".org"
#old#        additional_org_file = "../testdata/about-placeholder.org"
#old#        metadata_output = "../testdata/" + testname + ".pk"
#old#        metadata_input = "../testdata/nonexisting.pk"
#old#        log_firstrun = "../testdata/" + testname + ".log"
#old#        target_dir = "../testdata/"
#old#
#old#        # might be left over from a failed previous run:
#old#        if os.path.isfile(metadata_output):
#old#            os.remove(metadata_output)
#old#
#old#        # might be left over from a failed previous run:
#old#        if os.path.isfile(log_firstrun):
#old#            os.remove(log_firstrun)
#old#
#old#        # check, if test input file is found
#old#        self.assertTrue(os.path.isfile(template_file))
#old#        # check, if test input file is found
#old#        self.assertTrue(os.path.isfile(org_testfile))
#old#        # check, if test input file is found
#old#        self.assertTrue(os.path.isfile(additional_org_file))
#old#
#old#        # Building the call parameters:
#old#        first_parser = argparse.ArgumentParser()
#old#        first_parser.add_argument("--orgfiles", dest="orgfiles", nargs='+')
#old#        first_parser.add_argument("--targetdir", dest="targetdir")
#old#        first_parser.add_argument(
#old#            "--new-metadata",
#old#            dest="new_metadatafilename")
#old#        first_parser.add_argument(
#old#            "--previous-metadata",
#old#            dest="previous_metadatafilename")
#old#        first_parser.add_argument("--logfile", dest="logfilename")
#old#        first_parser.add_argument(
#old#            "-v",
#old#            "--verbose",
#old#            dest="verbose",
#old#            action="store_true")
#old#
#old#        myoptions = "--orgfiles " + org_testfile + " " + template_file + " " + additional_org_file + \
#old#            " --targetdir " + target_dir + " --previous-metadata " + metadata_input + " --new-metadata " + \
#old#            metadata_output + \
#old#            " --logfile " + log_firstrun  # + " --verbose"
#old#
#old#        options = first_parser.parse_args(myoptions.split())
#old#
#old#        # Invoking lazyblorg first interation:
#old#
#old#        mylazyblorg = Lazyblorg(options, self.logging)
#old#        generate, marked_for_feed, increment_version, stats_parsed_org_files, stats_parsed_org_lines = mylazyblorg.determine_changes()
#old#
#old#        # Checking results:
#old#
#old#        generate_sorted = sorted(generate)
#old#        marked_for_feed_sorted = sorted(marked_for_feed)
#old#
#old#        self.assertTrue(increment_version == [])
#old#        self.assertTrue(generate_sorted == marked_for_feed_sorted)
#old#
#old#        blog_data, stats_parsed_org_lines = mylazyblorg._parse_orgmode_file(
#old#            org_testfile)
#old#        template_blog_data, template_stats_parsed_org_lines = mylazyblorg._parse_orgmode_file(
#old#            template_file)
#old#        additional_blog_data, additional_stats_parsed_org_lines = mylazyblorg._parse_orgmode_file(
#old#            additional_org_file)
#old#        blog_data += template_blog_data
#old#        blog_data += additional_blog_data
#old#
#old#        metadata = Utils.generate_metadata_from_blogdata(blog_data)
#old#
#old#        return generate_sorted, blog_data, metadata, increment_version, mylazyblorg, generate, metadata_output
#old#
#old#    def htmlize_parser_data_to_html_files(
#old#            self,
#old#            testname,
#old#            blog_data,
#old#            metadata,
#old#            increment_version,
#old#            mylazyblorg,
#old#            generate):
#old#
#old#        target_dir = "../testdata/"
#old#        autotag_language = True
#old#        entries_timeline_by_published = {}
#old#
#old#        # extract HTML templates and store in class var
#old#        template_definitions = mylazyblorg._generate_template_definitions_from_template_data()
#old#
#old#        htmlizer = Htmlizer(
#old#            template_definitions,
#old#            "blog",
#old#            target_dir,
#old#            blog_data,
#old#            metadata,
#old#            entries_timeline_by_published,
#old#            generate,
#old#            increment_version,
#old#            autotag_language)
#old#
#old#        htmlcontent = None
#old#        for entry in blog_data:
#old#
#old#            entry = htmlizer.sanitize_and_htmlize_blog_content(entry)
#old#
#old#            if entry['category'] == config.TEMPORAL:
#old#                filename, orgfilename, htmlcontent = htmlizer._generate_temporal_article(
#old#                    entry)
#old#            elif entry['category'] == config.PERSISTENT:
#old#                pass  # FIXXME: probably add test for generating about-page as well
#old#            elif entry['category'] == config.TAGS:
#old#                filename, orgfilename, htmlcontent = htmlizer._generate_tag_page(
#old#                    entry)
#old#
#old#        htmloutputname = "../testdata/" + testname + ".html"
#old#
#old#        assert(htmlcontent)  # make sure that /some/ HTML content was generated
#old#
#old#        # generating HTML output in order to manually check in browser as well:
#old#        with codecs.open(htmloutputname, 'wb', encoding='utf-8') as output:
#old#            output.write(htmlcontent)
#old#
#old#        self.assertTrue(os.path.isfile(htmloutputname))
#old#
#old#        return htmloutputname
#old#
#old#    def compare_generated_html_content_to_comparison_html_file(
#old#            self, testname, htmloutputname, metadata_output):
#old#
#old#        # read in generated data from file:
#old#        contentarray_from_file = []
#old#        with codecs.open(htmloutputname, 'r', encoding='utf-8') as input:
#old#            contentarray_from_file = input.readlines()
#old#
#old#        # read in comparson data from file:
#old#        comparisonfilename = "../testdata/" + testname + "_COMPARISON.html"
#old#
#old#        with codecs.open(comparisonfilename, 'r', encoding='utf-8') as input:
#old#            comparison_string_array = input.readlines()
#old#
#old#        if len(comparison_string_array) != len(contentarray_from_file):
#old#            print "length of produced data (" + str(len(contentarray_from_file)) + ") differs from comparison data (" + str(len(comparison_string_array)) + ")"
#old#
#old#        # a more fine-grained diff (only) on the first element in blog_data:
#old#        self.assertTrue(Utils.diff_two_lists(contentarray_from_file,
#old#                                             comparison_string_array,
#old#                                             normalize_lineendings=True))
#old#
#old#        if os.path.isfile(metadata_output):
#old#            os.remove(metadata_output)
#old#
#old#        if os.path.isdir("../testdata/" + testname):
#old#            import shutil
#old#            shutil.rmtree("../testdata/" + testname)


# END OF FILE #################################################################
# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
