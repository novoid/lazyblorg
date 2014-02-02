#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2014-02-02 19:23:17 vk>

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


    def test_simple_formatting(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        htmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, prefix_dir, targetdir,
                            blog_data, generate, increment_version)

        self.assertTrue(htmlizer.htmlize_simple_text_formatting(u"This is *bold face* and ~teletype style~.") ==
                        u"This is <b>bold face</b> and <code>teletype style</code>.")

    def test_sanitize_HTML_entities(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        htmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, prefix_dir, targetdir,
                            blog_data, generate, increment_version)

        self.assertTrue(htmlizer.sanitize_html_characters(u"An & and <this> will be ampersand and <similar>.") ==
                        u"An &amp; and &lt;this&gt; will be ampersand and &lt;similar&gt;.")

    def test_sanitize_external_links(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        htmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, prefix_dir, targetdir,
                            blog_data, generate, increment_version)

        ## Org-mode links of style [[foo][bar]]:

        self.assertTrue(htmlizer.sanitize_external_links("[[http://foo][bar]]") == "<a href=\"http://foo\">bar</a>")

        self.assertTrue(htmlizer.sanitize_external_links("xy[[https://foo][bar]]z") == "xy<a href=\"https://foo\">bar</a>z")

        self.assertTrue(htmlizer.sanitize_external_links("xy[[http://foo][bar]]z[[http://first][second]]end") ==
                        "xy<a href=\"http://foo\">bar</a>z<a href=\"http://first\">second</a>end")

        self.assertTrue(htmlizer.sanitize_external_links("xy[[http://foo][bar]][[http://first][second]]end") ==
                        "xy<a href=\"http://foo\">bar</a><a href=\"http://first\">second</a>end")

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

        orgstring = "The URL of http://example.org/index.html?id=435#target will be mixed with " + \
            "[[https://www.example.org/path/index.html?id=435#target][some fancy URL]] in different mode."
        htmlstring = "The URL of <a href=\"http://example.org/index.html?id=435#target\">http://example.org/" + \
            "index.html?id=435#target</a> will be mixed with " + \
            "<a href=\"https://www.example.org/path/index.html?id=435#target\">some fancy URL</a> in different mode."
        self.assertTrue(htmlizer.sanitize_external_links(orgstring) == htmlstring)

        orgstring = "Multiple URLs in one line: http://heise.de [[http://heise.de]] [[http://heise.de][heise]]"
        htmlstring = "Multiple URLs in one line: <a href=\"http://heise.de\">http://heise.de</a> <a href=\"http://heise.de\">http://heise.de</a> <a href=\"http://heise.de\">heise</a>"
        self.assertTrue(htmlizer.sanitize_external_links(orgstring) == htmlstring)


    def test_fix_ampersands_in_url(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        htmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, prefix_dir, targetdir,
                            blog_data, generate, increment_version)

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
