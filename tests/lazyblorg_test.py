#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2014-02-02 18:46:11 vk>

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
        generate, marked_for_RSS, increment_version = first_lazyblorg.determine_changes()

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
        generate, marked_for_RSS, increment_version = second_lazyblorg.determine_changes()

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
        generate, marked_for_RSS, increment_version = mylazyblorg.determine_changes()

        ## Checking results:

        generate_sorted = sorted(generate)
        marked_for_RSS_sorted = sorted(marked_for_RSS)

        self.assertTrue(increment_version == [])
        self.assertTrue(generate_sorted == marked_for_RSS_sorted)
        self.assertTrue(generate_sorted == [u'2014-01-27-full-syntax-test', u'lazyblorg-templates'])

        blog_data = mylazyblorg._parse_orgmode_file(template_file)
        blog_data += mylazyblorg._parse_orgmode_file(org_testfile)
        
        ## extract HTML templates and store in class var
        template_definitions = mylazyblorg._generate_template_definitions_from_template_data()

        htmlizer = Htmlizer(template_definitions, testname, "blog", "about this blog",
                            target_dir, blog_data, generate, increment_version)
        #htmlizer.run()  ## FIXXME: return value?

        filename = htmlcontent = None
        for entry in blog_data:

            entry = htmlizer.sanitize_and_htmlize_blog_content(entry)

            if entry['category'] == htmlizer.TEMPORAL:
                filename, htmlcontent = htmlizer._create_time_oriented_blog_article(entry)

        htmloutputname = "../testdata/" + testname + ".html"
                
        ## generating HTML output in order to manually check in browser as well:
        with codecs.open(htmloutputname, 'wb', encoding='utf-8') as output:
            output.write(htmlcontent)

        self.assertTrue(os.path.isfile(htmloutputname))
            
        contentarray_from_file = []
        with codecs.open(htmloutputname, 'r', encoding='utf-8') as input:
            contentarray_from_file = input.readlines()
            
        comparison_string = '''  <!DOCTYPE html>
  <html xmlns="http://www.w3.org/1999/xhtml">
  <meta charset="UTF-8">
  <meta name="author" content="Karl Voit" />
  <meta name="generator" content="lazyblorg" />
  <link rel="stylesheet" title="public voit Standard CSS Style"
        href="http://Karl-Voit.at/public_voit.css" type="text/css" media="screen"  />

  <!-- WARNING: This page is written in (X)HTML5 and might not be displayed correctly in old browsers. -->

    <head>
      <!-- link rel="stylesheet" type="text/css" href="../../../../style.css" / -->
      <title>lazyblorg: Syntax-tests of the Currently Supported Org-mode Syntax Elements from the Parser and HTMLizer</title>

    </head>  <body>
    <article class="article">

	<header>

	  <nav class="article-header-nav">
	    <span class="breadcrumbs">
	      <a href="../../../../"><img src="http://karl-voit.at/images/public-voit_logo.svg" alt="public voit logo" width="350" style="vertical-align:middle;"></a><span style="padding-top:1em;">&nbsp;&nbsp;&nbsp;&nbsp;&raquo;
	      2014&nbsp;&ndash;&nbsp;01&nbsp;&ndash;&nbsp;30</span>
	      <!-- a href="../../../">2014</a>&nbsp;&ndash;&nbsp;<a href="../../">01</a>&nbsp;&ndash;&nbsp;<a href="../">30</a -->
	    </span>
	  </nav>
	  <aside>
	    <ul class="tags">	      <!-- span class="tag">publicvoit</span>&nbsp;-->
        <li><a href="#">publicvoit</a></li>	      <!-- span class="tag">lazyblorg</span>&nbsp;-->
        <li><a href="#">lazyblorg</a></li>	      <!-- span class="tag">MixedCaseTag</span>&nbsp;-->
        <li><a href="#">MixedCaseTag</a></li>	    </ul>
	  </aside>
	  <h1 class="article-title">lazyblorg: Syntax-tests of the Currently Supported Org-mode Syntax Elements from the Parser and HTMLizer</h1>

	</header>

  <div class="article-body">

<p>

This is a test entry for testing all currently implemented Org-mode syntax elements.

</p>

	  <header><h2 class="section-title">Implicit Org-mode Elements in This File</h2></header>

<p>

- headings - article tags - paragraphs

</p>

	  <header><h2 class="section-title">Drawers and Time-Stamps</h2></header>

<p>

Note: the time-stamps in the LOGBOOK and PROPERTIES drawers above are set to different days so that it is possible to check which time-stamp is used for what blog elements.

</p>

<p>

    A copy of the header:<br />
	  <pre>CLOSED: [2014-01-30 Thu 13:01]
:LOGBOOK:
- State "DONE"       from "DONE"       [2014-02-01 Sat 15:03]
- State "DONE"       from ""           [2014-01-30 Thu 14:02]
:END:
:PROPERTIES:
:CREATED:  [2014-01-28 Tue 12:00]
:ID: 2014-01-27-full-syntax-test
:END:	  </pre>

</p>
	  <header><h2 class="section-title">Basic Text Formatting</h2></header>

<p>

This is <b>bold</b> and <b>bold case</b>. And this is <code>teletype style</code>.

</p>

<p>

Examples with line-breaks in between: <b>This is a bold sentence which has a line break</b>.

</p>

	  <header><h2 class="section-title">URLs</h2></header>

<p>

Without brackets: <a href="http://heise.de">http://heise.de</a>

</p>

<p>

With brackets and no description: <a href="http://heise.de">http://heise.de</a>

</p>

<p>

With brackets and a description: <a href="http://heise.de">heise</a>

</p>

<p>

URLs with line breaks within: this is a very tough example of <a href="https://github.com/novoid/lazyblorg">an url like this which is very long</a>.

</p>

<p>

Multiple URLs in one line: <a href="http://heise.de">http://heise.de</a> <a href="http://heise.de">http://heise.de</a> <a href="http://heise.de">heise</a>

</p>

	  <header><h2 class="section-title">HTML-blocks</h2></header>
<p>
  <!-- a multi
       line comment -->
  <b>This is without any title</b>
</p>
<p>

    Example HTML snippet:<br />
	  <div class="example_code">&lt;b&gt;This&nbsp;is&nbsp;with&nbsp;a&nbsp;title&lt;/b&gt;<br />
&lt;ul&gt;<br />
&nbsp;&nbsp;&lt;li&gt;example&nbsp;list&nbsp;item&lt;/li&gt;<br />
&lt;/ul&gt;	  </div>

</p>

	  <header><h2 class="section-title">EXAMPLE-blocks</h2></header>

	  <pre>UPPER-case example without name
  indented line
     another indented line
This is *bold* and ~teletype~ with an URL https://github.com/novoid/lazyblorg and such.

  Last line.

This is a multi-line paragraph to demonstrate the behavior of line
break and so on. As you can see, the line breaks are now different
from Org-mode source or not.	  </pre>

	  <pre>lower-case example without name	  </pre>

<p>

    a name:<br />
	  <pre>UPPER-case example with name	  </pre>

</p>
<p>

    Another name:<br />
	  <pre>lower-case example with name	  </pre>

</p>
	  <header><h2 class="section-title">QUOTE-blocks</h2></header>

<blockquote>UPPER-case quote without name
  indented line
     another indented line
This is <b>bold</b> and <code>teletype</code> with an URL <a href="https://github.com/novoid/lazyblorg">https://github.com/novoid/lazyblorg</a> and such.

  Last line.

This is a multi-line paragraph to demonstrate the behavior of line
break and so on. As you can see, the line breaks are now different
from Org-mode source or not.</blockquote>

<blockquote>lower-case quote without name</blockquote>

<blockquote>UPPER-case quote with name</blockquote>

<blockquote>lower-case quote with name</blockquote>

	  <header><h2 class="section-title">VERSE-blocks</h2></header>

	  <pre>UPPER-case verse without name
  indented line
     another indented line
This is *bold* and ~teletype~ with an URL https://github.com/novoid/lazyblorg and such.

  Last line.

This is a multi-line paragraph to demonstrate the behavior of line
break and so on. As you can see, the line breaks are now different
from Org-mode source or not.	  </pre>

	  <pre>lower-case verse without name	  </pre>

<p>

    a name:<br />
	  <pre>UPPER-case verse with name	  </pre>

</p>
<p>

    Another name:<br />
	  <pre>lower-case verse with name	  </pre>

</p>
	  <header><h2 class="section-title">SRC-blocks</h2></header>

<p>

    #NAME#:<br />
	  <div class="example_code">UPPER-case&nbsp;src&nbsp;without&nbsp;name<br />
&nbsp;&nbsp;indented&nbsp;line<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;another&nbsp;indented&nbsp;line<br />
This&nbsp;is&nbsp;*bold*&nbsp;and&nbsp;~teletype~&nbsp;with&nbsp;an&nbsp;URL&nbsp;https://github.com/novoid/lazyblorg&nbsp;and&nbsp;such.<br />
<br />
&nbsp;&nbsp;Last&nbsp;line.<br />
<br />
This&nbsp;is&nbsp;a&nbsp;multi-line&nbsp;paragraph&nbsp;to&nbsp;demonstrate&nbsp;the&nbsp;behavior&nbsp;of&nbsp;line<br />
break&nbsp;and&nbsp;so&nbsp;on.&nbsp;As&nbsp;you&nbsp;can&nbsp;see,&nbsp;the&nbsp;line&nbsp;breaks&nbsp;are&nbsp;now&nbsp;different<br />
from&nbsp;Org-mode&nbsp;source&nbsp;or&nbsp;not.	  </div>

</p>

<p>

    #NAME#:<br />
	  <div class="example_code">lower-case&nbsp;src&nbsp;without&nbsp;name	  </div>

</p>

<p>

    #NAME#:<br />
	  <div class="example_code">UPPER-case&nbsp;src&nbsp;with&nbsp;name	  </div>

</p>

<p>

    #NAME#:<br />
	  <div class="example_code">lower-case&nbsp;src&nbsp;with&nbsp;name	  </div>

</p>

<p>

    #NAME#:<br />
	  <div class="example_code">test&nbsp;=&nbsp;42;<br />
print&nbsp;"Hello&nbsp;Python&nbsp;world!"<br />
if&nbsp;test&nbsp;==&nbsp;42:<br />
&nbsp;&nbsp;&nbsp;&nbsp;print&nbsp;"yes,&nbsp;it&nbsp;is&nbsp;42"<br />
else:<br />
&nbsp;&nbsp;&nbsp;&nbsp;print&nbsp;"there&nbsp;is&nbsp;something&nbsp;phishy&nbsp;around&nbsp;here."	  </div>

</p>

	  <header><h2 class="section-title">noexport-tags in headings</h2></header>

	  <header><h3 class="section-title">not ignored because it got no :noexport: tag set</h3></header>

<p>

This is somewhat tricky because it contains a tag surrounded by colons.

</p>

	  <header><h3 class="section-title">not ignored because it got no :NOEXPORT: tag set</h3></header>

<p>

This is somewhat tricky because it contains a tag surrounded by colons.

</p>

	  <header><h2 class="section-title">Horizontal Rule</h2></header>

<p>

Horizontal rules end up only in a wider vertical space.

</p>

<p>

Between this and the previous paragraph, there is no horizontal rule.

</p>
<div class="orgmode-hr" />
<p>

Between this and the previous paragraph, there was an horizontal rule.

</p>

    </div> <!-- article-body -->
    </article>
	  <aside class="published-on">
	    Published on <time datetime="2014-01-30T14:02+02:00">2014-01-30T14:02</time>
	  </aside>

    <footer>
      <p><i>about this blog</i> is authored in <a href="http://orgmode.org">Org-mode</a> and generated by <a href="https://github.com/novoid/lazyblorg">lazyblorg</a>

	 	&nbsp;&bull;&nbsp; <a href="http://validator.w3.org/check/referer">HTML5</a>

	 	&nbsp;&bull;&nbsp; <a href="http://jigsaw.w3.org/css-validator/">CSS3</a>
      </p>
    </footer>

  </body>
</html>'''

        comparison_string_array = comparison_string.split('\n')

        if len(comparison_string_array) != len(contentarray_from_file):
            print "length of produced data (" + str(len(contentarray_from_file)) + ") differs from comparison data (" + str(len(comparison_string_array)) + ")"
        
        ## a more fine-grained diff (only) on the first element in blog_data:
        for line in range(len(comparison_string_array)): 
            if contentarray_from_file[line].rstrip() != comparison_string_array[line].rstrip(): 
                print "=================  first difference  ===================== in line " + str(line)
                print "[" + contentarray_from_file[line].rstrip() + "]"
                print "   ---------------  comparison data:  --------------------"
                print "[" + comparison_string_array[line].rstrip() + "]"
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
