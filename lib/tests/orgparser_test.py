#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

import config  # lazyblorg-global settings
import unittest
from lib.utils import *
from lib.orgparser import *
import pickle  # for serializing and storing objects into files
from os import remove
from os.path import isfile, join


class TestOrgParser(unittest.TestCase):

    # FIXXME: (Note) These test are *not* exhaustive unit tests. They only
    # show the usage of the methods. Please add "mean" test cases and
    # borderline cases!

    logging = None

    def setUp(self):
        verbose = False
        quiet = False
        self.logging = Utils.initialize_logging("lazyblorg", verbose, quiet)

    def tearDown(self):
        pass

    def test_get_list_indentation_number(self):

        # manually written Org-mode file; has to be placed in "lib/tests/"
        testfile_org = join("lib", "tests", "simple.org")
        parser = OrgParser(testfile_org)

        try:
            self.assertEqual(parser._get_list_indentation_number(42), 0)
        except AssertionError:
            pass  # this *should* be cause an AssertionError
        try:
            self.assertEqual(parser._get_list_indentation_number(True), 0)
        except AssertionError:
            pass  # this *should* be cause an AssertionError
        try:
            self.assertEqual(parser._get_list_indentation_number(['x']), 0)
        except AssertionError:
            pass  # this *should* be cause an AssertionError

        self.assertEqual(parser._get_list_indentation_number(''), 0)
        self.assertEqual(parser._get_list_indentation_number('x'), 0)
        self.assertEqual(parser._get_list_indentation_number('x'), 0)
        self.assertEqual(parser._get_list_indentation_number('-'), 0)
        self.assertEqual(parser._get_list_indentation_number('  - foo bar'), 4)
        self.assertEqual(
            parser._get_list_indentation_number('  - foo bar'), 4)
        self.assertEqual(
            parser._get_list_indentation_number('    foo bar'), 4)
        self.assertEqual(
            parser._get_list_indentation_number('  * foo bar'), 4)
        self.assertEqual(
            parser._get_list_indentation_number('  42) foo bar'), 6)
        self.assertEqual(
            parser._get_list_indentation_number('  23. foo bar'), 6)

    def test_simple_org_to_blogdata(self):

        # manually written Org-mode file; has to be placed in "lib/tests/"
        testfile_org = join("lib", "tests", "simple.org")
        testfile_temp_output = join("lib", "tests", "simple_org_-_lastrun.pk")
        testfile_temp_reference = join("lib", "tests", "simple_org_-_reference.pk")

        # check, if test input file is found
        self.assertTrue(isfile(testfile_org))

        # make sure that no old output file is found:
        if isfile(testfile_temp_output):
            remove(testfile_temp_output)

        blog_data = []  # initialize the empty list
        parser = OrgParser(testfile_org)

        # parse the example Org-mode file:
        file_blog_data, stats_parsed_org_lines = parser.parse_orgmode_file()
        blog_data.extend(file_blog_data)

        # write data to dump file:
        with open(testfile_temp_output, 'wb') as output:
            pickle.dump(blog_data, output)

        # check, if dump file was created:
        self.assertTrue(isfile(testfile_temp_output))

        reference_blog_data = None

        # read reference data from file:
        with open(testfile_temp_reference, 'rb') as fileinput:
            reference_blog_data = pickle.load(fileinput)

        # a more fine-grained diff (only) on the first element in blog_data:
        Utils.diff_two_lists(
            blog_data[0]['content'],
            reference_blog_data[0]['content'])
        # OLD# for x in range(len(blog_data[0]['content'])):
        # OLD#     if blog_data[0]['content'][x] != reference_blog_data[0]['content'][x]:
        # OLD#         print "   =============== difference ==================="
        # OLD#         print reference_blog_data[0]['content'][x]
        # OLD#         print "   -------------------------------"
        # OLD#         print blog_data[0]['content'][x]
        # OLD#         print "   ===============
        # ==================="

        self.assertTrue(
            Utils.list_of_dicts_are_equal(
                reference_blog_data,
                blog_data))

    def test_rawcontent_starts_with_heading(self):
        """Every blog entry's rawcontent must start with its heading line."""

        testfiles = [
            join("testdata", "end_to_end_test", "orgfiles", "test.org"),
            join("testdata", "end_to_end_test", "orgfiles", "real-world-entries.org"),
            join("testdata", "end_to_end_test", "orgfiles", "test_snippets.org"),
        ]

        for testfile in testfiles:
            parser = OrgParser(testfile)
            blog_data, _ = parser.parse_orgmode_file()

            for entry in blog_data:
                rawcontent = entry.get('rawcontent', '')
                first_line = rawcontent.split('\n')[0] if rawcontent else ''
                self.assertTrue(
                    first_line.startswith('*'),
                    "Entry '%s' in '%s': rawcontent should start with "
                    "heading line but starts with: %s" %
                    (entry.get('id', '?'), testfile, repr(first_line)))
                self.assertIn(
                    entry['title'], first_line,
                    "Entry '%s' in '%s': rawcontent heading should contain "
                    "the entry title '%s'" %
                    (entry.get('id', '?'), testfile, entry['title']))

    def test_consecutive_entries_rawcontent_heading(self):
        """Consecutive blog entries (back-to-back) must each have their heading in rawcontent."""

        # test.org has 14 consecutive old-entry entries at level 2
        testfile = join("testdata", "end_to_end_test", "orgfiles", "test.org")
        parser = OrgParser(testfile)
        blog_data, _ = parser.parse_orgmode_file()

        consecutive_ids = ['1985-01-01-old-entry' + str(i) for i in range(1, 15)]
        for entry_id in consecutive_ids:
            matches = [e for e in blog_data if e.get('id') == entry_id]
            self.assertEqual(len(matches), 1,
                             "Expected to find entry '%s'" % entry_id)
            entry = matches[0]
            rawcontent = entry.get('rawcontent', '')
            first_line = rawcontent.split('\n')[0]
            self.assertTrue(
                first_line.startswith('*'),
                "Consecutive entry '%s': rawcontent must start with "
                "heading but starts with: %s" % (entry_id, repr(first_line)))

    def test_entry_after_nonblog_content_rawcontent_heading(self):
        """A blog entry following non-blog content must have its heading in rawcontent."""

        # real-world-entries.org has the drawer-tests entry after non-blog paragraphs
        testfile = join("testdata", "end_to_end_test", "orgfiles",
                        "real-world-entries.org")
        parser = OrgParser(testfile)
        blog_data, _ = parser.parse_orgmode_file()

        entry = [e for e in blog_data
                 if e.get('id') == '2021-01-30-drawer-tests'][0]
        rawcontent = entry.get('rawcontent', '')
        first_line = rawcontent.split('\n')[0]
        self.assertTrue(
            first_line.startswith('*'),
            "drawer-tests entry rawcontent must start with heading "
            "but starts with: %s" % repr(first_line))
        self.assertIn('Test case with drawers', first_line)


# END OF FILE ###########################################################
# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
