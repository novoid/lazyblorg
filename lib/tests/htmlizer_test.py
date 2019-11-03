#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

from config import *
import unittest
from lib.htmlizer import *
from lib.utils import *


class TestHtmlizer(unittest.TestCase):

    # FIXXME: (Note) These test are *not* exhaustive unit tests.

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

        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        template_definitions = [
            ['html-block', 'paragraph', ['<p>#PAR-CONTENT#</p>']],
            ['html-block', 'section-begin', ['<header>#SECTION-TITLE#</header>']]
        ]

        # entry['content'][index][0] == 'hr': -> ohne template_definition
        #
        # entry['content'][index][0] == 'par': template_definition[9]
        # ['html-block', u'paragraph', [u'', u'<p>', u'', u'#PAR-CONTENT#', u'', u'</p>', u'']]
        #
        # entry['content'][index][0] == 'heading': template_definition[8]
        # ['html-block', u'section-begin', [u'', u'\t  <header><h#SECTION-LEVEL# class="section-title">#SECTION-TITLE#</h#SECTION-LEVEL#></header>', u'']]

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)

        entry = {'content': [
            ['par', 'First paragraph'],
            ['par', 'Second paragraph'],
        ], 'category': 'TEMPORAL'}
        htmlized_content_expected = [
            '<p>First paragraph</p>',
            '<p>Second paragraph</p>']
        htmlized_entry_test = htmlizer.sanitize_and_htmlize_blog_content(entry)
        self.assertTrue(
            htmlized_entry_test['content'] == htmlized_content_expected)
        self.assertTrue(
            'htmlteaser-equals-content' in list(htmlized_entry_test.keys()))
        self.assertTrue(
            htmlized_entry_test['htmlteaser-equals-content'] is True)
        self.assertTrue('htmlteaser' not in list(htmlized_entry_test.keys()))

        entry = {'content': [
            ['par', 'First paragraph'],
            ['hr'],
            ['par', 'Second paragraph']
        ], 'category': 'TEMPORAL'}
        htmlized_content_expected = [
            '<p>First paragraph</p>',
            '<div class="orgmode-hr" ></div>',
            '<p>Second paragraph</p>']
        htmlized_entry_test = htmlizer.sanitize_and_htmlize_blog_content(entry)
        self.assertTrue(
            htmlized_entry_test['content'] == htmlized_content_expected)
        self.assertTrue(htmlized_entry_test['htmlteaser'] == [
                        '<p>First paragraph</p>'])
        self.assertTrue(
            'htmlteaser-equals-content' in list(htmlized_entry_test.keys()))
        self.assertTrue(
            htmlized_entry_test['htmlteaser-equals-content'] is False)

        entry = {'content': [
            ['par', 'First paragraph'],
            ['heading', {'title': 'My article header', 'level': 3}],
            ['par', 'Second paragraph']
        ], 'level': 1, 'category': 'TEMPORAL'}
        htmlized_content_expected = [
            '<p>First paragraph</p>',
            '<header>My article header</header>',
            '<p>Second paragraph</p>']
        htmlized_entry_test = htmlizer.sanitize_and_htmlize_blog_content(entry)

        self.assertTrue(
            htmlized_entry_test['content'] == htmlized_content_expected)
        self.assertTrue(htmlized_entry_test['htmlteaser'] == [
                        '<p>First paragraph</p>'])
        self.assertTrue(
            'htmlteaser-equals-content' in list(htmlized_entry_test.keys()))
        self.assertTrue(
            htmlized_entry_test['htmlteaser-equals-content'] is False)

    def test_sanitize_and_htmlize_simple_table(self):
        """
        This tests the correct htmlization of tables
        """

        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        template_definitions = [
            ['html-block', 'paragraph', ['<p>#PAR-CONTENT#</p>']],
            ['html-block', 'section-begin', ['<header>#SECTION-TITLE#</header>']]
        ]

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)

        entry = {'content': [
            ['par', 'First paragraph'],
            ['table', 'Table-name', ['| My  | table |     |',
                                      '|-----+-------+-----|',
                                      '| 23  | 42    |  65 |',
                                      '| foo | bar   | baz |']],
            ['par', 'Final paragraph']
        ], 'level': 1, 'category': 'TEMPORAL'}
        htmlized_table_expected = '''<table>
<thead>
<tr class="header">
<th>My</th>
<th>table</th>
<th></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>23</td>
<td>42</td>
<td>65</td>
</tr>
<tr class="even">
<td>foo</td>
<td>bar</td>
<td>baz</td>
</tr>
</tbody>
</table>
'''
        htmlized_content_expected = ['<p>First paragraph</p>',
                                     htmlized_table_expected,
                                     '<p>Final paragraph</p>']
        htmlized_entry_test = htmlizer.sanitize_and_htmlize_blog_content(entry)

        self.assertTrue(
            Utils.normalize_lineendings(
                htmlized_entry_test['content'][0]) == Utils.normalize_lineendings(
                htmlized_content_expected[0]))

        self.assertTrue(
            Utils.normalize_lineendings(htmlized_entry_test['content'][1]) ==
            Utils.normalize_lineendings(htmlized_content_expected[1])
        )

        self.assertTrue(
            Utils.normalize_lineendings(
                htmlized_entry_test['content'][2]) == Utils.normalize_lineendings(
                htmlized_content_expected[2]))

        self.assertTrue(
            'htmlteaser-equals-content' in list(htmlized_entry_test.keys()))
        self.assertTrue(
            htmlized_entry_test['htmlteaser-equals-content'] is True)

    def test_sanitize_and_htmlize_complex_table(self):
        """
        This tests the correct htmlization of a complex table
        """

        prefix_dir = 'foo'
        targetdir = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        blog_data = [{'id': '2014-03-02-my-persistent',
                      'category': config.PERSISTENT,
                      'firstpublishTS' : datetime.datetime(2008, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2008, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2008, 12, 29, 19, 40),
                                                     datetime.datetime(2008, 1, 29, 19, 40),
                                                     datetime.datetime(2008, 11, 29, 19, 40)]},
                     {'id': '2014-03-02-my-temporal',
                      'category': config.TEMPORAL,
                      'firstpublishTS' : datetime.datetime(2007, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2007, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2007, 12, 29, 19, 40),
                                                     datetime.datetime(2007, 1, 29, 19, 40),
                                                     datetime.datetime(2007, 11, 29, 19, 40)]},
                     {'id': '2015-03-02-my-additional-temporal',
                      'category': config.TEMPORAL,
                      'firstpublishTS' : datetime.datetime(2006, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2006, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2006, 12, 29, 19, 40),
                                                     datetime.datetime(2006, 1, 29, 19, 40),
                                                     datetime.datetime(2006, 11, 29, 19, 40)]},
                     {'id': 'my-tag',
                      'category': config.TAGS,
                      'firstpublishTS' : datetime.datetime(2011, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2011, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2011, 12, 29, 19, 40),
                                                     datetime.datetime(2011, 1, 29, 19, 40),
                                                     datetime.datetime(2011, 11, 29, 19, 40)]}]

        template_definitions = [
            ['html-block', 'paragraph', ['<p>#PAR-CONTENT#</p>']],
            ['html-block', 'section-begin', ['<header>#SECTION-TITLE#</header>']]
        ]

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)

        entry = {'content': [
            ['par', 'First paragraph'],
            ['table', 'Table-name',
             ['| *What*               |   *€* | *Amount* |  *Sum* | *Notes*             |',
              '|----------------------+-------+----------+--------+---------------------|',
              '| [[https://roses.example.com/myroses.html][My Roses]]             | 42.23 |       12 | 506.76 | *best* roses ~evar~ |',
              '| [[id:2014-03-02-my-temporal][internal *link* test]] |    10 |        2 |     20 | Umlaut test: öÄß    |']],
            ['par', 'Final paragraph']
        ], 'level': 1, 'category': 'TEMPORAL'}
        htmlized_table_expected = '''<table>
<thead>
<tr class="header">
<th><strong>What</strong></th>
<th><strong>\u20ac</strong></th>
<th><strong>Amount</strong></th>
<th><strong>Sum</strong></th>
<th><strong>Notes</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td><a href="https://roses.example.com/myroses.html">My Roses</a></td>
<td>42.23</td>
<td>12</td>
<td>506.76</td>
<td><strong>best</strong> roses <code>evar</code></td>
</tr>
<tr class="even">
<td><a href="''' + config.BASE_URL + '''/2007/01/29/my-temporal">internal <strong>link</strong> test</a></td>
<td>10</td>
<td>2</td>
<td>20</td>
<td>Umlaut test: \xf6\xc4\xdf</td>
</tr>
</tbody>
</table>
'''
        # FIXXME: Umlauts do not work yet :-(
        # FIXXME: *foo* gets converted to <strong>foo</strong> instead of
        # <b>foo</b>

        htmlized_content_expected = ['<p>First paragraph</p>',
                                     htmlized_table_expected,
                                     '<p>Final paragraph</p>']
        htmlized_entry_test = htmlizer.sanitize_and_htmlize_blog_content(entry)

        self.assertTrue(
            Utils.normalize_lineendings(
                htmlized_entry_test['content'][0]) == Utils.normalize_lineendings(
                htmlized_content_expected[0]))

        Utils.diff_two_lists(htmlized_entry_test['content'][1].split('\n'),
                             htmlized_content_expected[1].split('\n'))
        self.assertTrue(
            Utils.normalize_lineendings(
                htmlized_entry_test['content'][1]) == Utils.normalize_lineendings(
                htmlized_content_expected[1]))

        self.assertTrue(
            Utils.normalize_lineendings(
                htmlized_entry_test['content'][2]) == Utils.normalize_lineendings(
                htmlized_content_expected[2]))

        self.assertTrue(
            'htmlteaser-equals-content' in list(htmlized_entry_test.keys()))
        self.assertTrue(
            htmlized_entry_test['htmlteaser-equals-content'] is True)

    def test_get_newest_and_oldest_timestamp(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)

        entry = {
            'finished-timestamp-history': [
                datetime.datetime(
                    2011, 12, 29, 19, 40), datetime.datetime(
                    2008, 1, 29, 19, 40), datetime.datetime(
                    2013, 1, 29, 19, 40)],
            'category': config.TEMPORAL}

        self.assertTrue(
            Utils.get_newest_timestamp_for_entry(entry) == (
                datetime.datetime(2013, 1, 29, 19, 40),
                '2013', '01', '29', '19', '40'))
        self.assertTrue(
            Utils.get_oldest_timestamp_for_entry(entry) == (
                datetime.datetime(
                    2008, 1, 29, 19, 40),
                '2008', '01', '29', '19', '40'))

    def testgenerate_entry_list_by_newest_timestamp(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        blog_data = 'foo'
        targetdir = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        blog_data = [{'id': 'a_entry_from_2008',
                      'category': config.PERSISTENT,
                      'firstpublishTS' : datetime.datetime(2008, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2008, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2008, 12, 29, 19, 40),
                                                     datetime.datetime(2008, 1, 29, 19, 40),
                                                     datetime.datetime(2008, 11, 29, 19, 40)]},
                     {'id': 'b_entry_from_2007',
                      'category': config.TEMPORAL,
                      'firstpublishTS' : datetime.datetime(2007, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2007, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2007, 12, 29, 19, 40),
                                                     datetime.datetime(2007, 1, 29, 19, 40),
                                                     datetime.datetime(2007, 11, 29, 19, 40)]},
                     {'id': 'c_entry_from_2011',
                      'title': 'testtag',
                      'category': config.TAGS,
                      'firstpublishTS' : datetime.datetime(2011, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2011, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2011, 12, 29, 19, 40),
                                                     datetime.datetime(2011, 1, 29, 19, 40),
                                                     datetime.datetime(2011, 11, 29, 19, 40)]}]

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)

        entrylist = htmlizer.generate_entry_list_by_newest_timestamp()

        self.assertTrue(entrylist[0]['id'] == 'c_entry_from_2011')
        self.assertTrue(entrylist[1]['id'] == 'a_entry_from_2008')
        self.assertTrue(entrylist[2]['id'] == 'b_entry_from_2007')

    def test_generate_tag_page_with_more_than_one_word_in_title(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        blog_data = 'foo'
        targetdir = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        blog_data = [{'id': 'a_entry_from_2008',
                      'title': 'testtag',
                      'category': config.TAGS,
                      'firstpublishTS' : datetime.datetime(2008, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2008, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2008, 12, 29, 19, 40),
                                                     datetime.datetime(2008, 1, 29, 19, 40),
                                                     datetime.datetime(2008, 11, 29, 19, 40)]},
                     {'id': 'c_entry_from_2011',
                      'title': 'test title with multiple words',
                      'category': config.TAGS,
                      'firstpublishTS' : datetime.datetime(2011, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2011, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2011, 12, 29, 19, 40),
                                                     datetime.datetime(2011, 1, 29, 19, 40),
                                                     datetime.datetime(2011, 11, 29, 19, 40)]}]

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)
        with self.assertRaises(HtmlizerException):
            htmlizer.generate_entry_list_by_newest_timestamp()

    def test_populate_dict_of_tags_with_ids(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        blog_data = 'foo'
        targetdir = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        blog_data = [{'id': 'tag-page-entry',
                      'title': 'testtag',
                      'category': config.TAGS,
                      'usertags': []},
                     {'id': 'temporal-page-1',
                      'title': 'temporal 1',
                      'category': config.TEMPORAL,
                      'usertags': ['tag1', 'tag2']},
                     {'id': 'temporal-page-2',
                      'title': 'temporal 2',
                      'category': config.TEMPORAL,
                      'usertags': ['tag2', 'tag3']},
                     {'id': 'temporal-page-3',
                      'title': 'temporal 3',
                      'category': config.TEMPORAL,
                      'usertags': ['tag1', 'tag3']},
                     {'id': 'temporal-page-4',
                      'title': 'temporal 4',
                      'category': config.TEMPORAL,
                      'usertags': ['tag4']},
                     {'id': 'temporal-page-5',
                      'title': 'temporal 5',
                      'category': config.TEMPORAL,
                      'usertags': ['tag4', 'hidden']},
                     {'id': 'persistent-page-1',
                      'title': 'persistent 1',
                      'category': config.PERSISTENT,
                      'usertags': ['tag3']},
                     {'id': 'persistent-page-2',
                      'title': 'persistent 2',
                      'category': config.PERSISTENT,
                      'usertags': ['tag3', 'hidden']},
                     {'id': 'persistent-page-3',
                      'title': 'persistent 3',
                      'category': config.PERSISTENT,
                      'usertags': ['tag5', 'hidden']}]

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)

        dict_of_tags_with_ids = htmlizer._populate_dict_of_tags_with_ids(
            blog_data)

        self.assertEqual(sorted(dict_of_tags_with_ids.keys()),
                         ['tag1', 'tag2', 'tag3', 'tag4'])
        self.assertEqual(sorted(dict_of_tags_with_ids['tag1']), [
                         'temporal-page-1', 'temporal-page-3'])
        self.assertEqual(sorted(dict_of_tags_with_ids['tag2']), [
                         'temporal-page-1', 'temporal-page-2'])
        self.assertEqual(sorted(dict_of_tags_with_ids['tag3']), [
                         'persistent-page-1', 'temporal-page-2', 'temporal-page-3'])
        self.assertEqual(
            sorted(
                dict_of_tags_with_ids['tag4']),
            ['temporal-page-4'])

    def test_simple_formatting(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)

        self.assertTrue(htmlizer.htmlize_simple_text_formatting("*This* is *bold face* and *bold face style*. With *end*") ==
                        "<b>This</b> is <b>bold face</b> and <b>bold face style</b>. With <b>end</b>")

        self.assertTrue(htmlizer.htmlize_simple_text_formatting("~This~ is ~code~ and ~code style~. With ~end~") ==
                        "<code>This</code> is <code>code</code> and <code>code style</code>. With <code>end</code>")

        self.assertTrue(htmlizer.htmlize_simple_text_formatting("=This= is =verbatim= and =verbatim style=. With =end=") ==
                        "<code>This</code> is <code>verbatim</code> and <code>verbatim style</code>. With <code>end</code>")

        self.assertTrue(htmlizer.htmlize_simple_text_formatting("+This+ is +strike through+ and +strike through style+. With +end+") ==
                        "<s>This</s> is <s>strike through</s> and <s>strike through style</s>. With <s>end</s>")

        # real-world examples:

        # testing bold at begin and end of line:
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(
            "Das ist *ohne Umlaut und so weiter*.") == "Das ist <b>ohne Umlaut und so weiter</b>.")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(
            "Das ist *ohne Umlaut und Ende*") == "Das ist <b>ohne Umlaut und Ende</b>")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(
            "*ohne Umlaut und Anfang und Ende*") == "<b>ohne Umlaut und Anfang und Ende</b>")

        # testing bold at begin and end of line with german umlauts:
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(
            "Das ist *mit Umlaut Öäß und so weiter*.") == "Das ist <b>mit Umlaut Öäß und so weiter</b>.")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(
            "Das ist *mit Umlaut Öäß und Ende*") == "Das ist <b>mit Umlaut Öäß und Ende</b>")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(
            "*mit Umlaut Öäß und Anfang und Ende*") == "<b>mit Umlaut Öäß und Anfang und Ende</b>")

        # testing teletype at begin and end of line with german umlauts:
        self.assertTrue(htmlizer.htmlize_simple_text_formatting("Das ist ~mit Umlaut Öäß und so weiter~.") ==
                        "Das ist <code>mit Umlaut Öäß und so weiter</code>.")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(
            "Das ist ~mit Umlaut Öäß und Ende~") == "Das ist <code>mit Umlaut Öäß und Ende</code>")
        self.assertTrue(htmlizer.htmlize_simple_text_formatting(
            "~mit Umlaut Öäß und Anfang und Ende~") == "<code>mit Umlaut Öäß und Anfang und Ende</code>")

    def test_sanitize_HTML_entities(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)

        self.assertTrue(htmlizer.sanitize_html_characters("An & and <this> will be ampersand and <similar>.")
                        == "An &amp; and &lt;this&gt; will be ampersand and &lt;similar&gt;.")

    def test_sanitize_internal_links(self):

        # NOTE: with the simplification of the signature of
        # sanitize_internal_links (by removing the parameter for the
        # source page type in order to generate relative links) and
        # the move towards absolute links, the set of tests in this
        # function might be more redundant than necessary. During the
        # migration, I just removed the removed parameter and changed
        # from "../../../../foo/" to config.BASE_URL + "/foo/"
        # instead.

        template_definitions = 'foo'
        prefix_dir = 'foo'
        blog_data = 'foo'
        targetdir = 'mytargetdir'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        blog_data = [{'id': '2014-03-02-my-persistent',
                      'category': config.PERSISTENT,
                      'firstpublishTS' : datetime.datetime(2008, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2008, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2008, 12, 29, 19, 40),
                                                     datetime.datetime(2008, 1, 29, 19, 40),
                                                     datetime.datetime(2008, 11, 29, 19, 40)]},
                     {'id': '2014-03-02-my-temporal',
                      'category': config.TEMPORAL,
                      'firstpublishTS' : datetime.datetime(2007, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2007, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2007, 12, 29, 19, 40),
                                                     datetime.datetime(2007, 1, 29, 19, 40),
                                                     datetime.datetime(2007, 11, 29, 19, 40)]},
                     {'id': '2015-03-02-my-additional-temporal',
                      'category': config.TEMPORAL,
                      'firstpublishTS' : datetime.datetime(2006, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2006, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2006, 12, 29, 19, 40),
                                                     datetime.datetime(2006, 1, 29, 19, 40),
                                                     datetime.datetime(2006, 11, 29, 19, 40)]},
                     {'id': 'my-tag',
                      'title': 'testtag',
                      'category': config.TAGS,
                      'firstpublishTS' : datetime.datetime(2011, 1, 29, 19, 40),
                      'latestupdateTS' : datetime.datetime(2011, 12, 29, 19, 40),
                      'finished-timestamp-history': [datetime.datetime(2011, 12, 29, 19, 40),
                                                     datetime.datetime(2011, 1, 29, 19, 40),
                                                     datetime.datetime(2011, 11, 29, 19, 40)]}]

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)

        # Org-mode links of style [[id:foo][bar]] or [[id:foo]]:

        # negative case:
        self.assertTrue(
            htmlizer.sanitize_internal_links(
                "no link here to find") == "no link here to find")

        # simple links:
        self.assertTrue(htmlizer.sanitize_internal_links("[[id:2014-03-02-my-persistent]]") ==
                        "<a href=\"" + config.BASE_URL + "/my-persistent\">2014-03-02-my-persistent</a>")
        self.assertTrue(htmlizer.sanitize_internal_links("[[id:2014-03-02-my-temporal]]") ==
                        "<a href=\"" + config.BASE_URL + "/2007/01/29/my-temporal\">2014-03-02-my-temporal</a>")
        self.assertTrue(
            htmlizer.sanitize_internal_links(
                "[[id:my-tag]]") == "<a href=\"" + config.BASE_URL + "/tags/testtag\">my-tag</a>")
        self.assertTrue(
            htmlizer.sanitize_internal_links(
                "[[id:my-tag]]",
                keep_orgmode_format=True) == "[[" + config.BASE_URL + "/tags/testtag][my-tag]]")

        # links with description:
        self.assertTrue(htmlizer.sanitize_internal_links("[[id:2014-03-02-my-persistent][my description text]]") ==
                        "<a href=\"" + config.BASE_URL + "/my-persistent\">my description text</a>")
        self.assertTrue(htmlizer.sanitize_internal_links("[[id:2014-03-02-my-temporal][another description text]]") ==
                        "<a href=\"" + config.BASE_URL + "/2007/01/29/my-temporal\">another description text</a>")
        self.assertTrue(htmlizer.sanitize_internal_links("[[id:my-tag][tag link description text]]") ==
                        "<a href=\"" + config.BASE_URL + "/tags/testtag\">tag link description text</a>")

        self.assertTrue(
            htmlizer.sanitize_internal_links(
                "[[id:2014-03-02-my-persistent][my description text]]") == "<a href=\"" + config.BASE_URL + "/my-persistent\">my description text</a>")
        self.assertTrue(htmlizer.sanitize_internal_links("[[id:2014-03-02-my-temporal][another description text]]") ==
                        "<a href=\"" + config.BASE_URL + "/2007/01/29/my-temporal\">another description text</a>")
        self.assertTrue(
            htmlizer.sanitize_internal_links(
                "[[id:my-tag][tag link description text]]") == "<a href=\"" + config.BASE_URL + "/tags/testtag\">tag link description text</a>")

        self.assertTrue(
            htmlizer.sanitize_internal_links(
                "[[id:2014-03-02-my-persistent][my description text]]") == "<a href=\"" + config.BASE_URL + "/my-persistent\">my description text</a>")
        self.assertTrue(htmlizer.sanitize_internal_links("[[id:2014-03-02-my-temporal][another description text]]") ==
                        "<a href=\"" + config.BASE_URL + "/2007/01/29/my-temporal\">another description text</a>")
        self.assertTrue(htmlizer.sanitize_internal_links("[[id:my-tag][tag link description text]]") ==
                        "<a href=\"" + config.BASE_URL + "/tags/testtag\">tag link description text</a>")
        self.assertTrue(
            htmlizer.sanitize_internal_links(
                "like [[id:my-tag][text]] used") == "like <a href=\"" + config.BASE_URL + "/tags/testtag\">text</a> used")
        self.assertTrue(htmlizer.sanitize_internal_links("like [[id:my-tag][this]] and [[id:my-tag][that]] used") ==
                        "like <a href=\"" + config.BASE_URL + "/tags/testtag\">this</a> and <a href=\"" + config.BASE_URL + "/tags/testtag\">that</a> used")
        self.assertTrue(htmlizer.sanitize_internal_links("like [[id:my-tag][this]] and [[id:my-tag][that]] used",
                                                         keep_orgmode_format=True) ==
                        "like [[" + config.BASE_URL + "/tags/testtag][this]] and [[" + config.BASE_URL + "/tags/testtag][that]] used")

        # links with description and formatting:
        self.assertTrue(htmlizer.sanitize_internal_links("[[id:2014-03-02-my-persistent][my *description* text]]") ==
                        "<a href=\"" + config.BASE_URL + "/my-persistent\">my *description* text</a>")
        self.assertTrue(
            htmlizer.htmlize_simple_text_formatting(
                htmlizer.sanitize_internal_links("[[id:2014-03-02-my-temporal][another ~description~ text]]")) ==
            "<a href=\"" + config.BASE_URL + "/2007/01/29/my-temporal\">another <code>description</code> text</a>")
        self.assertTrue(
            htmlizer.htmlize_simple_text_formatting(
                htmlizer.sanitize_internal_links("[[id:2014-03-02-my-persistent][my *description* ~text~]]")) ==
            "<a href=\"" + config.BASE_URL + "/my-persistent\">my <b>description</b> <code>text</code></a>")
        self.assertTrue(
            htmlizer.htmlize_simple_text_formatting(
                htmlizer.sanitize_internal_links("[[id:2014-03-02-my-persistent][my *description* text]]")) ==
            "<a href=\"" + config.BASE_URL + "/my-persistent\">my <b>description</b> text</a>")

        # multiple internal links in one line:
        myinput = "foo [[id:2014-03-02-my-persistent][my *description* text]], " + \
                  "[[id:2014-03-02-my-temporal]], " + \
                  "[[id:2015-03-02-my-additional-temporal]], " + \
                  "[[id:2014-03-02-my-temporal][another ~description~ text]] and so forth"
        expectedoutput = "foo <a href=\"" + config.BASE_URL + "/my-persistent\">my *description* text</a>, " + \
                                       "<a href=\"" + config.BASE_URL + "/2007/01/29/my-temporal\">2014-03-02-my-temporal</a>, " + \
                                       "<a href=\"" + config.BASE_URL + "/2006/01/29/my-additional-temporal\">2015-03-02-my-additional-temporal</a>, " + \
                                       "<a href=\"" + config.BASE_URL + "/2007/01/29/my-temporal\">another ~description~ text</a> and so forth"
        value = htmlizer.sanitize_internal_links(myinput)
        if expectedoutput != value:
            print("expectedoutput: [" + expectedoutput + "]")
            print("value         : [" + value + "]")
        self.assertTrue(expectedoutput == value)

        # internal and external links in one line:
        myinput = "foo http://karl-voit.at [[id:2014-03-02-my-persistent][my *description* text]], " + \
                  "[[id:2014-03-02-my-temporal]], [[http://karl-voit.at][my home-page]], " + \
                  "[[id:2014-03-02-my-temporal][another ~description~ text]] and so forth"
        expectedoutput = "foo http://karl-voit.at " + \
                         "<a href=\"" + config.BASE_URL + "/my-persistent\">my *description* text</a>, " + \
                         "<a href=\"" + config.BASE_URL + "/2007/01/29/my-temporal\">2014-03-02-my-temporal</a>, " + \
                         "[[http://karl-voit.at][my home-page]], " + \
                         "<a href=\"" + config.BASE_URL + "/2007/01/29/my-temporal\">another ~description~ text</a> and so forth"
        value = htmlizer.sanitize_internal_links(myinput)
        if expectedoutput != value:
            print("expectedoutput: [" + expectedoutput + "]")
            print("value         : [" + value + "]")
        self.assertTrue(expectedoutput == value)

    def test_sanitize_external_links(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)

        # Org-mode links of style [[foo][bar]]:

        self.assertTrue(htmlizer.sanitize_external_links(
            "[[http://foo][bar]]") == "<a href=\"http://foo\">bar</a>")

        self.assertTrue(htmlizer.sanitize_external_links(
            "xy[[https://foo][bar]]z") == "xy<a href=\"https://foo\">bar</a>z")

        self.assertTrue(htmlizer.sanitize_external_links("xy[[http://foo][bar]]z[[http://first][second]]end") ==
                        "xy<a href=\"http://foo\">bar</a>z<a href=\"http://first\">second</a>end")

        self.assertTrue(htmlizer.sanitize_external_links("xy[[http://foo][bar]][[http://first][second]]end") ==
                        "xy<a href=\"http://foo\">bar</a><a href=\"http://first\">second</a>end")

        self.assertTrue(htmlizer.sanitize_external_links("This is an [[http://www.example.com][example " +
                                                         "web page]] and a [[https://example.com/page" +
                                                         ".shtml$%^&*][second]] one as well.") ==
                        "This is an <a href=\"http://www.example.com\">example web page</a> " +
                        "and a <a href=\"https://example.com/page" +
                        ".shtml$%^&*\">second</a> one as well.")

        # URL links of style http(s)://example.org

        self.assertTrue(htmlizer.sanitize_external_links("foo http://example.org bar") ==
                        "foo <a href=\"http://example.org\">http://example.org</a> bar")

        self.assertTrue(htmlizer.sanitize_external_links("foo https://example.org bar") ==
                        "foo <a href=\"https://example.org\">https://example.org</a> bar")

        # combining both URL styles:

        orgstring = "The URL of http://example.org/index.html?id=435#target will be mixed with " + \
            "[[https://www.example.org/path/index.html?id=435#target][some fancy URL]] in different mode."
        htmlstring = "The URL of <a href=\"http://example.org/index.html?id=435#target\">http://example.org/" + \
            "index.html?id=435#target</a> will be mixed with " + \
            "<a href=\"https://www.example.org/path/index.html?id=435#target\">some fancy URL</a> in different mode."
        self.assertTrue(
            htmlizer.sanitize_external_links(orgstring) == htmlstring)

        orgstring = "Multiple URLs in one line: http://heise.de [[http://heise.de]] [[http://heise.de][heise]]"
        htmlstring = "Multiple URLs in one line: <a href=\"http://heise.de\">http://heise.de</a> <a href=\"http://heise.de\">http://heise.de</a> <a href=\"http://heise.de\">heise</a>"
        self.assertTrue(
            htmlizer.sanitize_external_links(orgstring) == htmlstring)

        # edge cases

        orgstring = "URLs with special characters: [[https://de.wikipedia.org/wiki/Partition_%28Datentr%C3%A4ger%29]] [[https://de.wikipedia.org/wiki/Partition_%28Datentr%C3%A4ger%29][description]] foobar"
        htmlstring = "URLs with special characters: <a href=\"https://de.wikipedia.org/wiki/Partition_%28Datentr%C3%A4ger%29\">https://de.wikipedia.org/wiki/Partition_%28Datentr%C3%A4ger%29</a> <a href=\"https://de.wikipedia.org/wiki/Partition_%28Datentr%C3%A4ger%29\">description</a> foobar"
        self.assertTrue(
            htmlizer.sanitize_external_links(orgstring) == htmlstring)

    def test_fix_ampersands_in_url(self):

        template_definitions = 'foo'
        prefix_dir = 'foo'
        targetdir = 'foo'
        blog_data = 'foo'
        generate = 'foo'
        increment_version = 'foo'
        autotag_language = False
        ignore_missing_ids = False
        entries_timeline_by_published = {}

        htmlizer = Htmlizer(
            template_definitions,
            prefix_dir,
            targetdir,
            blog_data,
            None,
            entries_timeline_by_published,
            generate,
            increment_version,
            autotag_language,
            ignore_missing_ids)

        self.assertTrue(htmlizer.fix_ampersands_in_url('href="http://www.example.com/index.html&amp;s=foo" bar') ==
                        'href="http://www.example.com/index.html&s=foo" bar')

        # does not work #self.assertTrue(htmlizer.fix_ampersands_in_url('href="http://www.exa&amp;mple.com/" + \
        # does not work #    "index.html&amp;s=fo&amp;o" bar') == \
        # does not work #                    'href="http://www.exa&mple.com/index.html&s=fo&o" bar')
        # ... does not work (yet). However, the use-case of several ampersands in one URL is very rare.

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
