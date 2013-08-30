#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2013-08-30 13:05:18 vk>

import unittest
from lib.htmlizer import *
from lib.utils import *

class TestHtmlizer(unittest.TestCase):

    ## FIXXME: (Note) These test are *not* exhaustive unit tests.

    logging = None

    def setUp(self):
        verbose = True
        quiet = False
        self.logging = Utils.initialize_logging("lazyblorg", verbose, quiet)

    def tearDown(self):
        pass


    def test_sanitize_external_links(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        htmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, targetdir, blog_data, generate, increment_version)

        ## Org-mode links of style [[foo][bar]]:

        self.assertTrue(htmlizer.sanitize_external_links("[[foo][bar]]") == "<a href=\"foo\">bar</a>")

        self.assertTrue(htmlizer.sanitize_external_links("xy[[foo][bar]]z") == "xy<a href=\"foo\">bar</a>z")

        self.assertTrue(htmlizer.sanitize_external_links("xy[[foo][bar]]z[[first][second]]end") == 
                        "xy<a href=\"foo\">bar</a>z<a href=\"first\">second</a>end")

        self.assertTrue(htmlizer.sanitize_external_links("xy[[foo][bar]][[first][second]]end") == 
                        "xy<a href=\"foo\">bar</a><a href=\"first\">second</a>end")

        self.assertTrue(htmlizer.sanitize_external_links("This is an [[http://www.example.com][example " + \
                                                             "web page]] and a [[https://example.com/page" + \
                                                             ".shtml$%^&*][second]] one as well.") == 
                        "This is an <a href=\"http://www.example.com\">example web page</a> " + \
                                                             "and a <a href=\"https://example.com/page" + \
                                                             ".shtml$%^&*\">second</a> one as well.")

        ## URL links of style http(s)://example.org

        self.assertTrue(htmlizer.sanitize_external_links("foo http://example.org bar") == \
                            "foo <a href=\"http://example.org\">http://example.org</a> bar")

        self.assertTrue(htmlizer.sanitize_external_links("foo https://example.org bar") == \
                            "foo <a href=\"https://example.org\">https://example.org</a> bar")

        ## combining both URL styles:

        mystring = "The URL of http://example.org/index.html?id=435#target will be mixed with " + \
            "[[https://www.example.org/path/index.html?id=435#target][some fancy URL]] in different mode."
        expected = "The URL of <a href=\"http://example.org/index.html?id=435#target\">http://example.org/" + \
            "index.html?id=435#target</a> will be mixed with " + \
            "<a href=\"https://www.example.org/path/index.html?id=435#target\">some fancy URL</a> in different mode."
        self.assertTrue(htmlizer.sanitize_external_links(mystring) == expected)


    def test_fix_ampersands_in_url(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        htmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, targetdir, blog_data, generate, increment_version)

        self.assertTrue(htmlizer.fix_ampersands_in_url('href="http://www.example.com/index.html&amp;s=foo" bar') == \
                            'href="http://www.example.com/index.html&s=foo" bar')

        # does not work #self.assertTrue(htmlizer.fix_ampersands_in_url('href="http://www.exa&amp;mple.com/" + \
        # does not work #    "index.html&amp;s=fo&amp;o" bar') == \
        # does not work #                    'href="http://www.exa&mple.com/index.html&s=fo&o" bar')
        ## ... does not work (yet). However, the use-case of several ampersands in one URL is very rare.

        mystring = "The URL of <a href=\"http://example.org/index.html&amp;id=435#target\">http://example.org/" + \
            "index.html?id=435#target</a> will be mixed with " + \
            "<a href=\"https://www.example.org/path/index.html?id=435#target&amp;foo\">some fancy URL</a> " + \
            "in different mode."
        expected = "The URL of <a href=\"http://example.org/index.html&id=435#target\">http://example.org/" + \
            "index.html?id=435#target</a> will be mixed with " + \
            "<a href=\"https://www.example.org/path/index.html?id=435#target&foo\">some fancy URL</a> " + \
            "in different mode."
        self.assertTrue(htmlizer.fix_ampersands_in_url(mystring) == expected)


# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
