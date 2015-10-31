#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2015-10-17 12:28:16 vk>

import unittest
import sys
from lib.utils import Utils

try:
    import pypandoc
except ImportError:
    print "Could not find Python module \"pypandoc\".\nPlease install it, e.g., with \"sudo pip install pypandoc\"."
    sys.exit(1)


class TestPypandoc(unittest.TestCase):

    ## FIXXME: (Note) These test are *not* exhaustive unit tests.

    logging = None

    def setUp(self):
        verbose = False
        quiet = False
        self.logging = Utils.initialize_logging("lazyblorg.tests", verbose, quiet)

    def tearDown(self):
        pass

    def test_pypandoc_compatibility(self):

        """
        This test is testing if org-mode can be converted to html via pypandoc
        """

        from_formats, to_formats = pypandoc.get_pandoc_formats()
        self.assertTrue(u'org' in from_formats)
        self.assertTrue(u'html5' in to_formats)

    def test_basic_pypandoc_example(self):
        """
        This test is testing a basic pypandoc function call.
        """

        pypandoc_result = pypandoc.convert('- *foo* bar', 'html5', format='org')
        expected_html5_result = u'<ul>\n<li><strong>foo</strong> bar</li>\n</ul>\n'

        self.assertEqual(Utils.normalize_lineendings(pypandoc_result), Utils.normalize_lineendings(expected_html5_result))

    def test_pypandoc_with_umlauts(self):
        """
        This test is testing umlaut and charset with pypandoc.
        """

        pypandoc_result = pypandoc.convert('This is an umlaut test: öÄß€',
                                           'html5', format='org', encoding='utf-8')
        expected_html5_result = u'<p>This is an umlaut test: öÄß€</p>\n'

        ## FIXXME: Umlaut conversion does habe encoding issues.
        self.assertEqual(Utils.normalize_lineendings(pypandoc_result),
                         Utils.normalize_lineendings(expected_html5_result))

    def test_pypandoc_formatting_examples(self):
        """
        This test is testing Org-mode formatting examples.
        """

        org_example = u'''* Basic tests

- *bold*
- /italic/
- _underline_
- +strike through+
- =code=
- ~commands~

- http://orgmode.org

: small example

#+COMMENT: this will never be exported

#+BEGIN_COMMENT
multi
line
comment
#+END_COMMENT

- not (yet) working and edge cases:
  - /*combination*/
  - */combination/*
  - _*combination*_
  - *_combination_*
  - =*combination*=
  - ~C:\a\very\old\DOS\path~
  - http://orgmode.org
  - [[http://orgmode.org][orgmode-Homepage]]
  - [[http://orgmode.org][*orgmode* /Homepage/]]
'''

        expected_html5_result = u'''<h1 id="basic-tests">Basic tests</h1>
<ul>
<li><strong>bold</strong></li>
<li><em>italic</em></li>
<li><strong>underline</strong></li>
<li><del>strike through</del></li>
<li><code>code</code></li>
<li><p><code>commands</code></p></li>
<li><p><a href="http://orgmode.org" class="uri">http://orgmode.org</a></p></li>
</ul>
<pre class="example"><code>small example
</code></pre>
<ul>
<li>not (yet) working and edge cases:
<ul>
<li><em><strong>combination</strong></em></li>
<li><strong><em>combination</em></strong></li>
<li><strong><strong>combination</strong></strong></li>
<li><strong><strong>combination</strong></strong></li>
<li><code>*combination*</code></li>
<li><code>C:\x07\x0bery\\old\\DOS\\path</code></li>
<li><a href="http://orgmode.org" class="uri">http://orgmode.org</a></li>
<li><a href="http://orgmode.org">orgmode-Homepage</a></li>
<li><a href="http://orgmode.org"><strong>orgmode</strong> <em>Homepage</em></a></li>
</ul></li>
</ul>
'''
        self.maxDiff = None
        pypandoc_result = pypandoc.convert(org_example, 'html5', format='org')

        self.assertEqual(Utils.normalize_lineendings(pypandoc_result), Utils.normalize_lineendings(expected_html5_result))


# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
