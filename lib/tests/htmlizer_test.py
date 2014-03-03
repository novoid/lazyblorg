#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2014-03-03 20:41:20 vk>

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

    def test_sanitize_and_htmlize_blog_content(self):
        """
        This tests only the correct recognition of teaser parts of an 
        article: teaser ends with first heading or first <hr>-element.
        """

        prefix_dir = u'foo'
        targetdir = u'foo'
        blog_data = u'foo'
        generate = u'foo'
        increment_version = u'foo'

        template_definitions = [
            ['html-block', u'paragraph', [u'<p>#PAR-CONTENT#</p>']],
            ['html-block', u'section-begin', [u'<header>#SECTION-TITLE#</header>']]
        ]

        ## entry['content'][index][0] == 'hr': -> ohne template_definition
        ## 
        ## entry['content'][index][0] == 'par': template_definition[9]
        ## ['html-block', u'paragraph', [u'', u'<p>', u'', u'#PAR-CONTENT#', u'', u'</p>', u'']]
        ## 
        ## entry['content'][index][0] == 'heading': template_definition[8]
        ## ['html-block', u'section-begin', [u'', u'\t  <header><h#SECTION-LEVEL# class="section-title">#SECTION-TITLE#</h#SECTION-LEVEL#></header>', u'']]

        htmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, prefix_dir, targetdir,
                            blog_data, generate, increment_version)

        entry = {'content':[ \
                             ['par', u'First paragraph'],
                             ['par', u'Second paragraph'],
                         ], 'category':'TEMPORAL'}
        htmlized_content_expected = [u'<p>First paragraph</p>', u'<p>Second paragraph</p>']
        htmlized_entry_test = htmlizer.sanitize_and_htmlize_blog_content(entry)
        self.assertTrue(htmlized_entry_test['content'] == htmlized_content_expected)
        self.assertTrue('htmlteaser-equals-content' in htmlized_entry_test.keys())
        self.assertTrue(htmlized_entry_test['htmlteaser-equals-content'] == True)
        self.assertTrue('htmlteaser' not in htmlized_entry_test.keys())
        
        entry = {'content':[ \
                             ['par', u'First paragraph'],
                             ['hr'],
                             ['par', u'Second paragraph']
                         ], 'category':'TEMPORAL'}
        htmlized_content_expected = [u'<p>First paragraph</p>', '<div class="orgmode-hr" />', u'<p>Second paragraph</p>']
        htmlized_entry_test = htmlizer.sanitize_and_htmlize_blog_content(entry)
        self.assertTrue(htmlized_entry_test['content'] == htmlized_content_expected)
        self.assertTrue(htmlized_entry_test['htmlteaser'] == [u'<p>First paragraph</p>'])
        self.assertTrue('htmlteaser-equals-content' in htmlized_entry_test.keys())
        self.assertTrue(htmlized_entry_test['htmlteaser-equals-content'] == False)

        entry = {'content':[ \
                             ['par', u'First paragraph'],
                             ['heading', {'title': u'My article header', 'level': 3}],
                             ['par', u'Second paragraph']
                         ],\
                 'level':1, 'category':'TEMPORAL'}
        htmlized_content_expected = [u'<p>First paragraph</p>', u'<header>My article header</header>', u'<p>Second paragraph</p>']
        htmlized_entry_test = htmlizer.sanitize_and_htmlize_blog_content(entry)

        self.assertTrue(htmlized_entry_test['content'] == htmlized_content_expected)
        self.assertTrue(htmlized_entry_test['htmlteaser'] == [u'<p>First paragraph</p>'])
        self.assertTrue('htmlteaser-equals-content' in htmlized_entry_test.keys())
        self.assertTrue(htmlized_entry_test['htmlteaser-equals-content'] == False)

        
    def test_get_newest_and_oldest_timestamp(self):

        template_definitions = u'foo'
        prefix_dir = u'foo'
        targetdir = u'foo'
        blog_data = u'foo'
        generate = u'foo'
        increment_version = u'foo'
        htmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, prefix_dir, targetdir,
                            blog_data, generate, increment_version)

        entry = {'finished-timestamp-history':[datetime.datetime(2011, 12, 29, 19, 40),
                                               datetime.datetime(2008, 1, 29, 19, 40),
                                               datetime.datetime(2013, 1, 29, 19, 40)], 'category':'TEMPORAL'}

        self.assertTrue(htmlizer._get_newest_timestamp_for_entry(entry) == (datetime.datetime(2013, 1, 29, 19, 40),
                                                                            "2013", "01", "29",
                                                                            "19", "40"))
        self.assertTrue(htmlizer._get_oldest_timestamp_for_entry(entry) == (datetime.datetime(2008, 1, 29, 19, 40),
                                                                            "2008", "01", "29",
                                                                            "19", "40"))
        
    def testgenerate_entry_list_by_newest_timestamp(self):

        template_definitions = u'foo'
        prefix_dir = u'foo'
        blog_data = u'foo'
        targetdir = u'foo'
        generate = u'foo'
        increment_version = u'foo'

        tmphtmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, prefix_dir, targetdir,
                            blog_data, generate, increment_version)
        
        blog_data = [{'id':'a_entry_from_2008',
                      'category':tmphtmlizer.PERSISTENT,
                      'finished-timestamp-history':[datetime.datetime(2008, 12, 29, 19, 40),
                                                    datetime.datetime(2008, 1, 29, 19, 40),
                                                    datetime.datetime(2008, 11, 29, 19, 40)]},
                     {'id':'b_entry_from_2007',
                      'category':tmphtmlizer.TEMPORAL,
                      'finished-timestamp-history':[datetime.datetime(2007, 12, 29, 19, 40),
                                                    datetime.datetime(2007, 1, 29, 19, 40),
                                                    datetime.datetime(2007, 11, 29, 19, 40)]},
                     {'id':'c_entry_from_2011',
                      'category':tmphtmlizer.TAGS,
                      'finished-timestamp-history':[datetime.datetime(2011, 12, 29, 19, 40),
                                                    datetime.datetime(2011, 1, 29, 19, 40),
                                                    datetime.datetime(2011, 11, 29, 19, 40)]}]

        htmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, prefix_dir, targetdir,
                            blog_data, generate, increment_version)

        entrylist = htmlizer.generate_entry_list_by_newest_timestamp()

        self.assertTrue(entrylist[0]['id'] == 'c_entry_from_2011')
        self.assertTrue(entrylist[1]['id'] == 'a_entry_from_2008')
        self.assertTrue(entrylist[2]['id'] == 'b_entry_from_2007')
        
        
    def test_simple_formatting(self):

        template_definitions = u'foo'
        prefix_dir = u'foo'
        targetdir = u'foo'
        blog_data = u'foo'
        generate = u'foo'
        increment_version = u'foo'
        htmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, prefix_dir, targetdir,
                            blog_data, generate, increment_version)

        self.assertTrue(htmlizer.htmlize_simple_text_formatting(u"This is *bold face* and ~teletype style~.") ==
                        u"This is <b>bold face</b> and <code>teletype style</code>.")

        ## real-world examples:

        ## testing bold at begin and end of line:
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(u"Das ist *ohne Umlaut und so weiter*.") ==
                        u"Das ist <b>ohne Umlaut und so weiter</b>.")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(u"Das ist *ohne Umlaut und Ende*") ==
                        u"Das ist <b>ohne Umlaut und Ende</b>")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(u"*ohne Umlaut und Anfang und Ende*") ==
                        u"<b>ohne Umlaut und Anfang und Ende</b>")

        ## testing bold at begin and end of line with german umlauts:
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(u"Das ist *mit Umlaut Öäß und so weiter*.") ==
                        u"Das ist <b>mit Umlaut Öäß und so weiter</b>.")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(u"Das ist *mit Umlaut Öäß und Ende*") ==
                        u"Das ist <b>mit Umlaut Öäß und Ende</b>")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(u"*mit Umlaut Öäß und Anfang und Ende*") ==
                        u"<b>mit Umlaut Öäß und Anfang und Ende</b>")

        ## testing teletype at begin and end of line with german umlauts:
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(u"Das ist ~mit Umlaut Öäß und so weiter~.") ==
                        u"Das ist <code>mit Umlaut Öäß und so weiter</code>.")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(u"Das ist ~mit Umlaut Öäß und Ende~") ==
                        u"Das ist <code>mit Umlaut Öäß und Ende</code>")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(u"~mit Umlaut Öäß und Anfang und Ende~") ==
                        u"<code>mit Umlaut Öäß und Anfang und Ende</code>")

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

    def test_sanitize_internal_links(self):
        
        template_definitions = u'foo'
        prefix_dir = u'foo'
        blog_data = u'foo'
        targetdir = u'mytargetdir'
        generate = u'foo'
        increment_version = u'foo'
        tmphtmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, prefix_dir, targetdir,
                            blog_data, generate, increment_version)

        blog_data = [{'id':'2014-03-02-my-persistent',
                      'category':tmphtmlizer.PERSISTENT,
                      'finished-timestamp-history':[datetime.datetime(2008, 12, 29, 19, 40),
                                                    datetime.datetime(2008, 1, 29, 19, 40),
                                                    datetime.datetime(2008, 11, 29, 19, 40)]},
                     {'id':'2014-03-02-my-temporal',
                      'category':tmphtmlizer.TEMPORAL,
                      'finished-timestamp-history':[datetime.datetime(2007, 12, 29, 19, 40),
                                                    datetime.datetime(2007, 1, 29, 19, 40),
                                                    datetime.datetime(2007, 11, 29, 19, 40)]},
                     {'id':'2015-03-02-my-additional-temporal',
                      'category':tmphtmlizer.TEMPORAL,
                      'finished-timestamp-history':[datetime.datetime(2006, 12, 29, 19, 40),
                                                    datetime.datetime(2006, 1, 29, 19, 40),
                                                    datetime.datetime(2006, 11, 29, 19, 40)]},
                     {'id':'my-tag',
                      'category':tmphtmlizer.TAGS,
                      'finished-timestamp-history':[datetime.datetime(2011, 12, 29, 19, 40),
                                                    datetime.datetime(2011, 1, 29, 19, 40),
                                                    datetime.datetime(2011, 11, 29, 19, 40)]}]

        htmlizer = Htmlizer(template_definitions, prefix_dir, prefix_dir, prefix_dir, targetdir,
                            blog_data, generate, increment_version)

        ## Org-mode links of style [[id:foo][bar]] or [[id:foo]]:

        ## FIXXME: also defined in htmlizer.py and more! -> grab from central instance!
        TAGS = 'TAGS'
        PERSISTENT = 'PERSISTENT'
        TEMPORAL = 'TEMPORAL'
        
        ## negative case:
        self.assertTrue(htmlizer.sanitize_internal_links(TEMPORAL, u"no link here to find") == u"no link here to find")

        ## simple links:
        self.assertTrue(htmlizer.sanitize_internal_links(TEMPORAL, u"[[id:2014-03-02-my-persistent]]") ==
                        u"<a href=\"../../../../my-persistent\">2014-03-02-my-persistent</a>")
        self.assertTrue(htmlizer.sanitize_internal_links(TEMPORAL, u"[[id:2014-03-02-my-temporal]]") ==
                        u"<a href=\"../../../../2007/01/29/my-temporal\">2014-03-02-my-temporal</a>")
        self.assertTrue(htmlizer.sanitize_internal_links(TEMPORAL, u"[[id:my-tag]]") ==
                        u"<a href=\"../../../../tags/my-tag\">my-tag</a>")

        ## links with description:
        self.assertTrue(htmlizer.sanitize_internal_links(TEMPORAL, u"[[id:2014-03-02-my-persistent][my description text]]") ==
                        u"<a href=\"../../../../my-persistent\">my description text</a>")
        self.assertTrue(htmlizer.sanitize_internal_links(TEMPORAL, u"[[id:2014-03-02-my-temporal][another description text]]") ==
                        u"<a href=\"../../../../2007/01/29/my-temporal\">another description text</a>")
        self.assertTrue(htmlizer.sanitize_internal_links(TEMPORAL, u"[[id:my-tag][tag link description text]]") ==
                        u"<a href=\"../../../../tags/my-tag\">tag link description text</a>")

        self.assertTrue(htmlizer.sanitize_internal_links(PERSISTENT, u"[[id:2014-03-02-my-persistent][my description text]]") ==
                        u"<a href=\"../my-persistent\">my description text</a>")
        self.assertTrue(htmlizer.sanitize_internal_links(PERSISTENT, u"[[id:2014-03-02-my-temporal][another description text]]") ==
                        u"<a href=\"../2007/01/29/my-temporal\">another description text</a>")
        self.assertTrue(htmlizer.sanitize_internal_links(PERSISTENT, u"[[id:my-tag][tag link description text]]") ==
                        u"<a href=\"../tags/my-tag\">tag link description text</a>")

        self.assertTrue(htmlizer.sanitize_internal_links(TAGS, u"[[id:2014-03-02-my-persistent][my description text]]") ==
                        u"<a href=\"../../my-persistent\">my description text</a>")
        self.assertTrue(htmlizer.sanitize_internal_links(TAGS, u"[[id:2014-03-02-my-temporal][another description text]]") ==
                        u"<a href=\"../../2007/01/29/my-temporal\">another description text</a>")
        self.assertTrue(htmlizer.sanitize_internal_links(TAGS, u"[[id:my-tag][tag link description text]]") ==
                        u"<a href=\"../../tags/my-tag\">tag link description text</a>")

        ## links with description and formatting:
        self.assertTrue(htmlizer.sanitize_internal_links(TEMPORAL, u"[[id:2014-03-02-my-persistent][my *description* text]]") ==
                        u"<a href=\"../../../../my-persistent\">my *description* text</a>")
        self.assertTrue(
            htmlizer.htmlize_simple_text_formatting(
            htmlizer.sanitize_internal_links(TEMPORAL, u"[[id:2014-03-02-my-temporal][another ~description~ text]]")) ==
                        u"<a href=\"../../../../2007/01/29/my-temporal\">another <code>description</code> text</a>")
        self.assertTrue(
            htmlizer.htmlize_simple_text_formatting(
            htmlizer.sanitize_internal_links(TEMPORAL, u"[[id:2014-03-02-my-persistent][my *description* ~text~]]")) ==
                        u"<a href=\"../../../../my-persistent\">my <b>description</b> <code>text</code></a>")
        self.assertTrue(
            htmlizer.htmlize_simple_text_formatting(
            htmlizer.sanitize_internal_links(TEMPORAL, u"[[id:2014-03-02-my-persistent][my *description* text]]")) ==
            u"<a href=\"../../../../my-persistent\">my <b>description</b> text</a>")

        
        ## multiple internal links in one line:
        myinput = u"foo [[id:2014-03-02-my-persistent][my *description* text]], " + \
                u"[[id:2014-03-02-my-temporal]], " + \
                u"[[id:2015-03-02-my-additional-temporal]], " + \
                u"[[id:2014-03-02-my-temporal][another ~description~ text]] and so forth"
        expectedoutput = u"foo <a href=\"../../../../my-persistent\">my *description* text</a>, " + \
                         u"<a href=\"../../../../2007/01/29/my-temporal\">2014-03-02-my-temporal</a>, " + \
                         u"<a href=\"../../../../2006/01/29/my-additional-temporal\">2015-03-02-my-additional-temporal</a>, " + \
                         u"<a href=\"../../../../2007/01/29/my-temporal\">another ~description~ text</a> and so forth"
        value = htmlizer.sanitize_internal_links(TEMPORAL, myinput)
        if expectedoutput != value:
            print "expectedoutput: [" + expectedoutput + "]"
            print "value         : [" + value + "]"
        self.assertTrue(expectedoutput == value)

        ## internal and external links in one line:
        myinput = u"foo http://karl-voit.at [[id:2014-03-02-my-persistent][my *description* text]], " + \
                u"[[id:2014-03-02-my-temporal]], [[http://karl-voit.at][my home-page]], " + \
                u"[[id:2014-03-02-my-temporal][another ~description~ text]] and so forth"
        expectedoutput = u"foo http://karl-voit.at " + \
                         u"<a href=\"../../../../my-persistent\">my *description* text</a>, " + \
                         u"<a href=\"../../../../2007/01/29/my-temporal\">2014-03-02-my-temporal</a>, " + \
                         u"[[http://karl-voit.at][my home-page]], " + \
                         u"<a href=\"../../../../2007/01/29/my-temporal\">another ~description~ text</a> and so forth"
        value = htmlizer.sanitize_internal_links(TEMPORAL, myinput)
        if expectedoutput != value:
            print "expectedoutput: [" + expectedoutput + "]"
            print "value         : [" + value + "]"
        self.assertTrue(expectedoutput == value)
        
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

        ## edge cases

        orgstring = "URLs with special characters: [[https://de.wikipedia.org/wiki/Partition_%28Datentr%C3%A4ger%29]] [[https://de.wikipedia.org/wiki/Partition_%28Datentr%C3%A4ger%29][description]] foobar"
        htmlstring = "URLs with special characters: <a href=\"https://de.wikipedia.org/wiki/Partition_%28Datentr%C3%A4ger%29\">https://de.wikipedia.org/wiki/Partition_%28Datentr%C3%A4ger%29</a> <a href=\"https://de.wikipedia.org/wiki/Partition_%28Datentr%C3%A4ger%29\">description</a> foobar"
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
