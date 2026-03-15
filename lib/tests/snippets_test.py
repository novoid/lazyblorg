#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

import config
import unittest
from lib.snippets import SnippetResolver, SnippetException
from lib.utils import Utils


class TestSnippetResolver(unittest.TestCase):

    logging = None

    def setUp(self):
        verbose = False
        quiet = False
        self.logging = Utils.initialize_logging("lazyblorg", verbose, quiet)

    def tearDown(self):
        pass

    def _make_snippet(self, snippet_id, content, rawcontent='', level=2):
        """Helper to create a snippet entry."""
        return {
            'id': snippet_id,
            'category': config.SNIPPET,
            'title': 'Snippet ' + snippet_id,
            'level': level,
            'lbtags': ['blog', 'lbsnippet'],
            'usertags': [],
            'content': content,
            'rawcontent': rawcontent,
        }

    def _make_entry(self, entry_id, content, rawcontent='', level=2):
        """Helper to create a blog entry."""
        return {
            'id': entry_id,
            'category': config.TEMPORAL,
            'title': 'Article ' + entry_id,
            'level': level,
            'lbtags': ['blog'],
            'usertags': [],
            'content': content,
            'rawcontent': rawcontent,
        }

    def test_simple_inline_replacement(self):
        """Short snippet inlined in paragraph."""
        snippet = self._make_snippet('greeting-snippet',
                                      [['par', 'Hello World']])
        entry = self._make_entry('article-1',
                                  [['par', 'I say [[id:greeting-snippet]] to you.']])
        blog_data = [snippet, entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['content'],
                         [['par', 'I say Hello World to you.']])

    def test_block_replacement(self):
        """Paragraph-only snippet ref replaced with content."""
        snippet = self._make_snippet('block-snippet',
                                      [['par', 'First paragraph.'],
                                       ['par', 'Second paragraph.']])
        entry = self._make_entry('article-1',
                                  [['par', 'Intro text.'],
                                   ['par', '[[id:block-snippet]]'],
                                   ['par', 'Outro text.']])
        blog_data = [snippet, entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['content'],
                         [['par', 'Intro text.'],
                          ['par', 'First paragraph.'],
                          ['par', 'Second paragraph.'],
                          ['par', 'Outro text.']])

    def test_multi_element_block_replacement(self):
        """Snippet with headings + paragraphs."""
        snippet = self._make_snippet('heading-snippet',
                                      [['par', 'Intro.'],
                                       ['heading', {'title': 'Sub', 'level': 3}],
                                       ['par', 'Under sub.']])
        entry = self._make_entry('article-1',
                                  [['heading', {'title': 'Context', 'level': 3}],
                                   ['par', 'Some text.'],
                                   ['par', '[[id:heading-snippet]]']])
        blog_data = [snippet, entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        self.assertEqual(len(result), 1)
        content = result[0]['content']
        # The snippet heading should be adapted: previous heading is level 3,
        # so snippet headings should be at level 4 (prev+1)
        self.assertEqual(content[0], ['heading', {'title': 'Context', 'level': 3}])
        self.assertEqual(content[1], ['par', 'Some text.'])
        self.assertEqual(content[2], ['par', 'Intro.'])
        self.assertEqual(content[3], ['heading', {'title': 'Sub', 'level': 4}])
        self.assertEqual(content[4], ['par', 'Under sub.'])

    def test_recursive_resolution(self):
        """Snippet within snippet."""
        inner = self._make_snippet('inner-snippet',
                                    [['par', 'inner content']])
        outer = self._make_snippet('outer-snippet',
                                    [['par', '[[id:inner-snippet]]']])
        entry = self._make_entry('article-1',
                                  [['par', '[[id:outer-snippet]]']])
        blog_data = [inner, outer, entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['content'],
                         [['par', 'inner content']])

    def test_loop_detection(self):
        """Circular reference raises SnippetException."""
        snippet_a = self._make_snippet('snippet-a',
                                        [['par', '[[id:snippet-b]]']])
        snippet_b = self._make_snippet('snippet-b',
                                        [['par', '[[id:snippet-a]]']])
        entry = self._make_entry('article-1',
                                  [['par', '[[id:snippet-a]]']])
        blog_data = [snippet_a, snippet_b, entry]

        resolver = SnippetResolver(blog_data)
        with self.assertRaises(SnippetException):
            resolver.resolve_all()

    def test_self_reference_loop(self):
        """Snippet references itself."""
        snippet = self._make_snippet('self-ref',
                                      [['par', '[[id:self-ref]]']])
        blog_data = [snippet]

        resolver = SnippetResolver(blog_data)
        with self.assertRaises(SnippetException):
            resolver.resolve_all()

    def test_heading_level_adaptation(self):
        """Headings adjusted to context."""
        snippet = self._make_snippet('h-snippet',
                                      [['heading', {'title': 'H1', 'level': 2}],
                                       ['par', 'Text.'],
                                       ['heading', {'title': 'H2', 'level': 3}],
                                       ['par', 'More text.']])
        # Previous heading is level 4, so snippet level 2 → level 5, snippet level 3 → level 6
        entry = self._make_entry('article-1',
                                  [['heading', {'title': 'Deep section', 'level': 4}],
                                   ['par', '[[id:h-snippet]]']])
        blog_data = [snippet, entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        content = result[0]['content']
        self.assertEqual(content[0], ['heading', {'title': 'Deep section', 'level': 4}])
        self.assertEqual(content[1], ['heading', {'title': 'H1', 'level': 5}])
        self.assertEqual(content[2], ['par', 'Text.'])
        self.assertEqual(content[3], ['heading', {'title': 'H2', 'level': 6}])
        self.assertEqual(content[4], ['par', 'More text.'])

    def test_described_link_warning(self):
        """[[id:snip][text]] logs warning but still works."""
        snippet = self._make_snippet('desc-snippet',
                                      [['par', 'replaced text']])
        entry = self._make_entry('article-1',
                                  [['par', 'See [[id:desc-snippet][my description]] here.']])
        blog_data = [snippet, entry]

        resolver = SnippetResolver(blog_data)
        with self.assertLogs(level='WARNING') as cm:
            result = resolver.resolve_all()

        self.assertEqual(len(result), 1)
        self.assertIn('description which will be ignored', cm.output[0])
        self.assertEqual(result[0]['content'],
                         [['par', 'See replaced text here.']])

    def test_bare_id_reference(self):
        """id:snippet-id works."""
        snippet = self._make_snippet('bare-snippet',
                                      [['par', 'bare content']])
        entry = self._make_entry('article-1',
                                  [['par', 'id:bare-snippet']])
        blog_data = [snippet, entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        self.assertEqual(len(result), 1)
        # Bare id: as whole paragraph → block replacement
        self.assertEqual(result[0]['content'],
                         [['par', 'bare content']])

    def test_bare_id_inline_reference(self):
        """id:snippet-id used inline."""
        snippet = self._make_snippet('bare-snippet',
                                      [['par', 'bare content']])
        entry = self._make_entry('article-1',
                                  [['par', 'text id:bare-snippet here']])
        blog_data = [snippet, entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['content'],
                         [['par', 'text bare content here']])

    def test_snippets_removed_from_output(self):
        """Snippet entries not in returned blog_data."""
        snippet = self._make_snippet('remove-me', [['par', 'content']])
        entry = self._make_entry('article-1', [['par', 'no refs']])
        blog_data = [snippet, entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'article-1')
        for e in result:
            self.assertNotEqual(e.get('category'), config.SNIPPET)

    def test_snippet_tag_is_lbtag(self):
        """lbsnippet should be in lbtags not usertags (tested via config constant)."""
        self.assertEqual(config.TAG_FOR_SNIPPET_ENTRY, 'lbsnippet')
        self.assertEqual(config.SNIPPET, 'SNIPPET')

    def test_rawcontent_replacement(self):
        """rawcontent updated with snippet rawcontent."""
        snippet = self._make_snippet(
            'raw-snippet',
            [['par', 'snippet text']],
            rawcontent='** DONE Snippet raw-snippet  :blog:lbsnippet:\nSnippet body here.\nMore body.\n')
        entry = self._make_entry(
            'article-1',
            [['par', '[[id:raw-snippet]]']],
            rawcontent='Some text with [[id:raw-snippet]] reference.\n')
        blog_data = [snippet, entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        self.assertEqual(len(result), 1)
        self.assertIn('Snippet body here.', result[0]['rawcontent'])
        self.assertNotIn('[[id:raw-snippet]]', result[0]['rawcontent'])

    def test_rawcontent_strips_metadata(self):
        """rawcontent replacement must strip heading, CLOSED, LOGBOOK, and PROPERTIES drawers."""
        snippet_raw = (
            '** DONE My snippet                              :blog:lbsnippet:\n'
            'CLOSED: [2026-01-01 Wed 10:00]\n'
            ':LOGBOOK:\n'
            '- State "DONE"       from ""           [2026-01-01 Wed 10:00]\n'
            ':END:\n'
            ':PROPERTIES:\n'
            ':CREATED:  [2026-01-01 Wed 09:00]\n'
            ':ID: meta-snippet\n'
            ':END:\n'
            '\n'
            'This is the actual snippet body.\n'
            '\n'
            'Second paragraph of snippet.\n'
        )
        snippet = self._make_snippet(
            'meta-snippet',
            [['par', 'This is the actual snippet body.'],
             ['par', 'Second paragraph of snippet.']],
            rawcontent=snippet_raw)

        entry_raw = (
            '** DONE My article                              :blog:mytest:\n'
            'CLOSED: [2026-01-10 Fri 14:00]\n'
            ':LOGBOOK:\n'
            '- State "DONE"       from ""           [2026-01-10 Fri 14:00]\n'
            ':END:\n'
            ':PROPERTIES:\n'
            ':CREATED:  [2026-01-10 Fri 12:00]\n'
            ':ID: 2026-01-10-test\n'
            ':END:\n'
            '\n'
            'Intro text.\n'
            '\n'
            '[[id:meta-snippet]]\n'
            '\n'
            'Outro text.\n'
        )
        entry = self._make_entry(
            'article-1',
            [['par', 'Intro text.'],
             ['par', '[[id:meta-snippet]]'],
             ['par', 'Outro text.']],
            rawcontent=entry_raw)
        blog_data = [snippet, entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        raw = result[0]['rawcontent']
        # Body content must be present
        self.assertIn('This is the actual snippet body.', raw)
        self.assertIn('Second paragraph of snippet.', raw)
        # Snippet metadata must NOT leak into the article rawcontent
        self.assertNotIn('CLOSED: [2026-01-01', raw)
        self.assertNotIn('State "DONE"       from ""           [2026-01-01', raw)
        self.assertNotIn(':CREATED:  [2026-01-01', raw)
        self.assertNotIn(':ID: meta-snippet', raw)
        # The article's own LOGBOOK/PROPERTIES must still be present
        self.assertIn('CLOSED: [2026-01-10', raw)
        self.assertIn(':LOGBOOK:', raw)
        self.assertIn(':CREATED:  [2026-01-10', raw)
        # The snippet reference must be resolved
        self.assertNotIn('[[id:meta-snippet]]', raw)
        # Verify there is only one :LOGBOOK: (the article's own, not the snippet's)
        self.assertEqual(raw.count(':LOGBOOK:'), 1)
        self.assertEqual(raw.count(':PROPERTIES:'), 1)

    def test_no_references_unchanged(self):
        """Entries without refs pass through unchanged."""
        entry = self._make_entry('article-1',
                                  [['par', 'Just normal text.'],
                                   ['heading', {'title': 'Heading', 'level': 3}],
                                   ['par', 'More text.']])
        blog_data = [entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['content'],
                         [['par', 'Just normal text.'],
                          ['heading', {'title': 'Heading', 'level': 3}],
                          ['par', 'More text.']])

    def test_no_snippets_passthrough(self):
        """When no snippets exist, blog_data passes through unchanged."""
        entry = self._make_entry('article-1',
                                  [['par', 'Just text.']])
        blog_data = [entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['content'], [['par', 'Just text.']])

    def test_nonexistent_id_link_not_replaced(self):
        """[[id:nonexistent]] should not be modified."""
        entry = self._make_entry('article-1',
                                  [['par', 'See [[id:some-other-entry]] for details.']])
        blog_data = [entry]

        resolver = SnippetResolver(blog_data)
        result = resolver.resolve_all()

        self.assertEqual(result[0]['content'],
                         [['par', 'See [[id:some-other-entry]] for details.']])


if __name__ == '__main__':
    unittest.main()
