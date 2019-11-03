## -*- coding: utf-8;mode: org;  -*-
## This file is best viewed with GNU Emacs Org-mode: http://orgmode.org/

#+BEGIN_QUOTE
«A designer knows he has achieved perfection not when there is nothing
left to add, but when there is nothing left to take away.» ([[https://en.wikipedia.org/wiki/Antoine_de_Saint-Exup%25C3%25A9ry][Antoine de
Saint-Exupéry]])
#+END_QUOTE

* lazyblorg -- blogging with Org-mode for very lazy people

This is a web log (blog) environment for [[http://en.wikipedia.org/wiki/Emacs][GNU Emacs]] with [[http://orgmode.org/][Org-mode]]
which generates static HTML5 web pages. It is much more superior to
any other Org-mode-to-blog-solution I have seen so far!

: <(All?) your Org-mode files>  --lazyblorg-->  static HTML pages
:                                                       |
:                                                       v
:                                  optional upload (shell) script
:                                                       |
:                                                       v
:                                                  your web space

There is [[http://orgmode.org/worg/org-blog-wiki.html][a list of similar/alternative Org-mode blogging projects]]
whose workflows seem really tedious to me.

See [[http://article.gmane.org/gmane.emacs.orgmode/49747/][my original post to the Org-mode ML]] for how this idea of lazyblorg
started in 2011.

This awesome piece of software is a sheer beauty with regard to:
- simplicity of creating a new blog entry
  - *I mean it*: there is no step which can be skipped!
    - add heading+content anywhere, add ID, tag, invoke lazyblorg
- integration into [[http://karl-voit.at/tags/pim/][my personal, published workflows]]
  - here, you have to either adapt my totally awesome workflows or you
    have to find alternative ways of doing following things:
    - linking/including image files or attachments in general (I use [[https://github.com/novoid/Memacs/blob/master/docs/memacs_filenametimestamps.org][this Memacs module]])
      - advantage of my method: I simply add an image file by typing
        ~tsfile:2014-03-03-this-is-my-file-name.jpg~ in
        double-brackets and I really don't care in which folder the
        file is currently located on my system
    - copying resulting HTML files to webspace (I do it using [[http://www.cis.upenn.edu/~bcpierce/unison/][unison]]/rsync)
    - probably more to come

** Target group

Lazy users of [[http://orgmode.org/][Org-mode]] who want to do blogging very easily and totally
cool.

Or simply wannabes. I'm perfectly fine with this as long as they use
lazyblorg.

** Other people using lazyblorg

Pages using lazyblorg are listed [[https://karl-voit.at/tags/lazyblorg/][on my personal tag page on
"lazyblorg"]]. Please do drop me a line when you want to get your page
added to the list.

Quote from [[https://seppjansen.com/2018/04/24/site-using-lazyblorg/][Sepp Jansen]]:

#+BEGIN_QUOTE
[...]

But when I revisited lazyblorg after studying the other packages, it
suddenly seemed like a better solution. After only a short time of
reading I figured out the entire templating and post generation
system. Although not the most elegant, it is super simple and easy to
understand. And those are my most important points.

The developer states that it is easy to configure and start building,
and is absolutely right.

In just a few hours I went from installing dependencies to having a
fully working website, including some layout and CSS customization.
The included HTML and CSS is easy to modify so I could (lazily) make
the site look like I wanted it to without too much digging in many
little files. I even managed to make it look a lot like my old site
without too much effort! Lazyblorg really lives up to its name!

[...]

I really like lazyblorg, and I'll happily manage [[https://seppjansen.com/][this website]] with it
for as long as possible.
#+END_QUOTE

** Skills necessary

- modifying configuration settings, e.g., in script files
- optional: creating scheduled tasks (cronjob, ...) if you
  are a *really* lazy one (and if you trust lazyblorg to do its job in
  the background)

** System requirements
:PROPERTIES:
:CREATED:  [2014-03-14 Fr 13:24]
:END:

lazyblorg is written in *Python 3*.

Development platform is Debian GNU/Linux. So with any decent GNU/Linux
you should be fine as well.

It might work on OS X but I never tried it so far.

I definitely does not work with Microsoft Windows. Although a
programmer can add a couple of ~os.path.thisorthat()~ here and there
and it should be good to go. Please consider sending a pull-request if
you are fixing this issue. Thanks!

** Version and Changelog
:PROPERTIES:
:CREATED:  [2014-03-14 Fr 13:28]
:END:

Currently (2019-10-23), I consider lazyblorg in beta-status with
version 0.96 or so.

I don't maintain a specific changelog. However, when there are
substantial changes to lazyblorg, you will find [[https://karl-voit.at/tags/lazyblorg/][a blog article tagged
with "lazyblorg"]]. Use an RSS/Atom aggregator to follow the blog.

** Why lazyblorg?

*Minimum effort* for blogging.

And: your blog entries can be written *anywhere in your Org-mode
files*. They will be found by lazyblorg. :-)

Further advantages are listed below.

** Example workflow for creating a blog entry

1. write a blog entry *anywhere* in your Org-mode files
   - With lazyblorg, you can, e.g., write a blog article about an
     event as a sub-heading of the event itself!
2. tag your entry with ~:blog:~
3. add an unique ID in the PROPERTIES drawer
   - You might want to use a package that automatically generates
     unique IDs to your headings (I don't).
   - You might want to take a look [[http://article.gmane.org/gmane.emacs.orgmode/16199][at this solution using file or
     directory variables]].
4. set the state of your entry to ~DONE~
   - make sure that a ~:LOGBOOK:~ drawer entry will be created that
     contains the time-stamp

An example blog entry looks like this:

: ** DONE An Example Blog Post           :blog:lazyblorg:software:
: CLOSED: [2017-06-18 Sun 00:16]
: :PROPERTIES:
: :ID: 2017-07-17-example-posting
: :CREATED:  [2017-06-17 Sat 23:45]
: :END:
: :LOGBOOK:
: - State "DONE"       from "NEXT"       [2017-06-18 Sun 00:16]
: :END:
:        […]
: Today, I found out that…

That's it. lazyblorg does the rest. It feels like magic, doesn't it? :-)

** Advantages

These things make a blogger a happy one:

*No other Org-mode blogging system* I know of is able to process blog
entries which are *scattered across all your Org-mode documents*.

*No other Org-mode blogging system* I know of is able to generate a
blog entry with that *minimum effort* to the author.

You do not need to maintain a specific Org-mode file that contains you
blog posts only. [[http://www.tbray.org/ongoing/When/201x/2011/03/07/BNotes][*Create* blog posts]] *anywhere* in between your notes,
todos, contacts, ...


And there are some technological advantages you might consider as well:

- You don't need to write or correct HTML code by yourself.
- produces static, state-of-the-art HTML5
  - it's super-fast on delivery to browsers
  - very low computing requirements on your web server: minimum of server load
- No in-between format or tool.
  - Direct conversion from Org-mode to HTML/CSS.
  - dependencies have the tendency to cause problems when the
    dependent tools change over time
  - lazyblorg should be running fine for a long time after it is set
    up properly
- Decide by yourself how and where you are hosting your blog files
  and log files.
- you will find more advantages when running and using lazyblorg - I
  am very confident about that ;-)

** Disadvantages

Yes, there are some disadvantages. I am totally honest with you since we
are becoming close friends right now:

- lazyblorg *re-generates the complete set of output pages on every run*
  - this will probably changed in a future release (to me: no high priority)
  - most of the time this is not an issue at all
    - if pages are generated on a different system as the web server
      runs on, performance is a minor issue
    - if you don't have thousands of pages, this will not take long

- lazyblorg is implemented in Python:
  - Its Org-mode parser supports *only a (large) sub-set of Org-mode syntax*
    and features.
    - Basic rule: use *an empty line between two different syntax
      elements* such as paragraphs, lists, tables, and so on.
    - Whenever I think that an additional Org-mode syntax element is
      needed for my blog, I start thinking of implementing it
    - I am using Pandoc as a fall-back for all other Org-mode syntax
      elements which works pretty fine
    - For a list of general Org-mode parsers please [[http://orgmode.org/worg/org-tools/][read this page]]

- lazyblorg is using state-of-the art HTML5 and CSS3
  - No old HTML4.01 transitional stuff or similar
  - Results might not be compatible with browsers such as Internet
    Explorer or mobile devices.
    - tell your Internet Explorer friends that they should do
      themselves a favor and switch to a real browser

- You have to accept the one-time setup effort which requires
  knowledge of:
  - using command-line tools
  - modifying configuration files
  - summary: getting this beautiful thing to work in your environment

** Features

#+BEGIN_QUOTE
«Technology develops from the primitive via the complex to the
simple.»
#+END_QUOTE
([[https://en.wikipedia.org/wiki/Antoine_de_Saint-Exup%25C3%25A9ry][Antoine de Saint-Exupéry]]; note: lazyblorg is currently "primitive"
but with a great outlook up to the status of being simple)

Here is a selection of features of lazyblorg which helps you to blog
efficiently:

- Converts Org-mode To HTML5: lazyblorg supports [[https://github.com/novoid/lazyblorg/wiki/Orgmode-Elements][a (large sub-)set of
  syntax elements of Org-mode]]
  - also see FAQs for "What Org-mode elements are supported by
    lazyblorg?"

- Different [[https://github.com/novoid/lazyblorg/wiki/Page-Types][page types]] allow you to create:
  1. articles related to a specific date ([[https://github.com/novoid/lazyblorg/wiki/Temporal-Pages][temporal pages]])
     - Those articles are published and hardly updated.
  2. articles not related to a specific date ([[https://github.com/novoid/lazyblorg/wiki/Persistent-Pages][persistent pages]])
     - Frequent updates or the absence of any day-relation makes this
       page type very sexy to use.
  3. articles describing a tag you are using ([[https://github.com/novoid/lazyblorg/wiki/Tag-Pages][tag pages]])
     - Yes, with lazyblorg, you are (optionally) able to explain how
       you are using a certain tag. You can link your most important
       tag-related articles and so forth. Most systems don't offer any
       possibility to communicate the meaning of the tags used.
  4. the [[https://github.com/novoid/lazyblorg/wiki/Entry-Page][entry page]] of your blog
     - You gotta give them a starting page ;-)
  5. the [[https://github.com/novoid/lazyblorg/wiki/Templates][templates]] which are used to generate your blog pages
     - Hooray, you are able to define all templates of your blog
       within Org-mode as well. No need to edit source code here.
       Isn't this great?

- To efficiently notify users of new articles or changes to existing
  articles, lazyblorg generates [[https://github.com/novoid/lazyblorg/wiki/Feeds][RSS/ATOM feeds]].

- Really fast to use [[https://github.com/novoid/lazyblorg/wiki/Links#linking-other-blog-articles-internal-links][linking to other blog articles]] using their ID property.

- At the bottom of each article, there is a list of related articles
  that back-link to here.

- You can very easily [[https://github.com/novoid/lazyblorg/wiki/Images][embed image files]] with automatically scaling to
  their desired width
  - This feature is hardened against image file renaming and broken
    links because of moving images files to different folders
  - Users of [[https://github.com/novoid/Memacs][Memacs]] do have advanced possibilities here as well
  - An optional image cache directory holds previously resized image
    file and therefore prevents resizing effort for each run.

- For navigating through the blog articles I do recommend using the
  [[https://github.com/novoid/lazyblorg/wiki/Tag-Pages][tags]]. Articles related to one topic share common tags whereas a
  date-oriented archive has only very limited use. The tag cloud which
  is on the [[http://karl-voit.at/tags/][tag overview page]] offers a quick overview of your most used
  tags.

- There is a search feature which brings you to the content by
  searching for keywords or phrases.

- Easy embedding of [[https://github.com/novoid/lazyblorg/wiki/Embedding-External-Content][external content]] such as Tweets or YouTube videos.

- You can exclude content from being published with various features:
  1. [[https://github.com/novoid/lazyblorg/wiki/Comments][Comment lines]]
  2. Mark an article/heading as hidden [[https://github.com/novoid/lazyblorg/wiki/Headings#headings-within-a-blog-article][using the tag NOEXPORT]]
  3. The [[https://github.com/novoid/lazyblorg/wiki/Headings#tag-hidden][hidden tag]] does publish an article but hides it from
     the entry page, navigational pages, and the feeds. This way, you
     can publish pages who can only be access by people knowing its URL.

** FAQs

See https://github.com/novoid/lazyblorg/wiki/FAQs

* Installing and Starting with lazyblorg

I am using it for [[http://Karl-Voit.at][my own blog]] and therefore it gets more and more
ready to use as I add new features.

What's working so far:
- parsing a large sub-set of Org-mode
  - most important: the parser requires a blank line between different
    Org mode elements
- parsing the HTML templates
- generating HTML5 pages with [[https://github.com/novoid/lazyblorg/wiki/Org-mode-Elements][a sub-set of the sub-set of the Org-mode
  syntax elements]]

** External dependencies

The number of external dependencies is kept at a minimum.

This is a list of the most important dependencies:
- [[http://werkzeug.pocoo.org/][Werkzeug]]
  - for sanitizing path components
  - I installed it on Debian GNU/Linux with ~apt-get install python3-werkzeug~
- pickle
  - object serialization
  - most likely: should be part of your Python distribution
- pypandoc
  - some Org-mode syntax elements are being converted using [[http://pandoc.org/][Pandoc]] and
    its Python binding [[https://github.com/bebraw/pypandoc][pypandoc]]
  - you can get it via ~sudo apt-get install pandoc~ and ~sudo pip
    install python3-pypandoc~
  - *Note:* Debian GNU/Linux 8 (Jessie) comes with a Pandoc version
    [[https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=800701][which is has bugs]]. Please install a more recent version. I
    upgraded to ~pandoc-1.15.1-1-amd64.deb~ from:
    http://pandoc.org/installing.html
- [[https://pypi.python.org/pypi/opencv-python][opencv-python]]
  - lazyblorg scales embedded images according to the HTML export attributes
  - Install using =sudo apt-get install python3-opencv=
- [[http://sass-lang.com/][Sass]] (optional) if you want to generate your CSS from the scss-file
- [[https://github.com/novoid/orgformat][orgformat]]
  - This is my library that provides basic utility functions when
    working with Org mode strings

All other libraries should be part of a standard Python distribution.

** How to Start

1. Get the source
   - ~git clone https://github.com/novoid/lazyblorg.git~ or
     [[https://github.com/novoid/lazyblorg/archive/master.zip][download current version as ZIP file]]

2. Adapt ~config.py~ to meet your settings.

3. Do a technological test-drive
   - start: ~lazyblorg/example_invocation.sh~
   - this should work with GNU/Linux (and most probably OS X)
   - if not, there is something wrong with the set-up; maybe missing
     external libraries, wrong paths, ...

4. Study, understand, and adopt the content of [[https://github.com/novoid/lazyblorg/blob/master/example_invocation.sh][example_invocation.sh]]
   - with this, you are able to modify command line parameters to meet
     your requirements
   - if unsure, ask for help using ~lazyblorg.py --help~

5. Get yourself an overview on *what defines a lazyblorg blog post* and
   write your own blog posts. A (normal temporal) blog article consists of:
   1. A (direct) tag has to be ~blog~
      - Sorry, no tag inheritance. Every blog entry has to be
        explicitely tagged.
   2. You have to add an unique ~:ID:~ property
   3. The entry has to be marked with ~DONE~
   4. A ~:LOGBOOK:~ entry has to be found with the time-stamp of
      setting the entry to ~DONE~
      - in [[https://github.com/novoid/dot-emacs][my set-up]], this is created automatically
   5. Do not use Org-mode elements that lazyblorg does not understand
      - You should not get a disaster if you are using new
        elements. The result might disappoint you, that's all.
      - However, many Org-mode elements are automatically converted
        through pandoc.

6. OPTIONAL: Write your own CSS file
   - you can [[http://Karl-Voit.at/public_voit.css][take a look on mine]] if you do not care that I am not
     really into Web design :-)
   - please replace hard-coded URL to CSS file in
     [[https://github.com/novoid/lazyblorg/blob/master/templates/blog-format.org][lazyblorg/templates/blog-format.org]] and link it to your CSS file

7. OPTIONAL: Adopt the blog template
   - default template is defined in
     [[https://github.com/novoid/lazyblorg/blob/master/templates/blog-format.org][lazyblorg/templates/blog-format.org]]

8. OPTIONAL: Create tag pages for your most important tags where you
   describe how you are using this tag, what are the most important
   blog entries related to the tag and so forth.

9. Publish your pages on a web space of your choice
   - publishing can be done in various ways. This is how I do it using
     ~lazyblorg/make_and_publish_public_voit.sh~ which is an
     adopted version of ~lazyblorg/example_invocation.sh~:
     1. invoking ~testall.sh~
        - this is for checking whether or not recent code changes did
          something harmful to my (unfortunately very limited) set of
          unit tests
     2. invoking ~lazyblorg~ with my more or less fixed set of
        command line parameters
     3. invoking ~rsync -av testdata/2del/blog/* $HOME/public_html/~
        - it synchronizes the newly generated blog data to the local
          copy of my web space data
        - this separation makes sense to me because with this, I am
          able to do test drives without overwriting my (local copy of
          my) blog
     4. invoking [[http://www.cis.upenn.edu/~bcpierce/unison/][unison]]
        - in order to transfer my local copy of my web space data to
          my public web space
   - This method has the advantage that generating (invoking
     ~lazyblorg~) and publishing (invoking ~unison~) are separate
     steps. This way, I can locally re-generate the blog (for testing
     purposes) as often I want to. However, as long as I do not sync
     it to my web space, I keep the meta-data (which is in the local
     web space copy) of the published version (and not the meta-data
     of the previous test-run).

10. Have fun with a pretty neat method to generate your blog pages

Because we are already close friends now, I tell you a *hidden
feature* of lazyblorg nobody knows yet: whenever you see a π-symbol in
the upper right corner of a blog entry on [[http://qr.cx/7wKz][my blog]]: this is a link to
the original Org-mode source of that page. This way, you can compare
Org-mode-source and HTML-result right away. Isn't that cool? :-)

** Five categories of page type

There are five different types of pages in lazyblorg. Most of the
time, you are going to produce temporal pages. However, it is
important to understand the other ones as well.

In order to process a blog-heading to its HTML5 representation, its
Org-mode file has to be included in the ~--orgfiles~ command line
argument of ~lazyblorg.py~. Do not forget to include the archive files
as well.

1. *temporal*
2. *persistent*
3. *tags*
4. *entry page*
5. *templates*

Please do read https://github.com/novoid/lazyblorg/wiki/Page-Types for
important details.

** BONUS: Preview Blog Article
:PROPERTIES:
:CREATED:  [2014-02-25 Tue 17:27]
:END:

It is tedious to re-generate the whole blog and even upload it to your
web-space just to check the HTML version of the article you are
currently writing.

Yeah, this also sucks at my side.

Good news everybody: There is a simple method to preview the article
under the cursor. The script [[https://github.com/novoid/lazyblorg/blob/master/preview_blogentry.sh][preview_blogentry.sh]] contains an ELISP
function that extracts the current blog article (all lazyblorg criteria
has to be fulfilled: ID, ~blog~ tag, status ~DONE~), stores it into a
temporary file, and invokes lazyblorg via ~preview_blogentry.sh~ with
this temporary file and the Org-mode file containing the format
definitions.

If this worked out, your browser shows you all generated blog
articles.

Please *do adopt the mentioned scripts* to you specific requirements -
the ones from the repository are for my personal set-up which is
unlikely to fit yours (directory paths mostly).

Bang! Another damn cool feature of lazyblorg. This is going better and
better. :-)

** BONUS: Jump From URL to Blog Article

Imagine, you're looking at a blog article of your nice
lazyblorg-generated blog. Now you want to go to the corresponding
Org-mode source to fix a typo.

The issue here is, that you have to either know, where your heading is
located or you have to go to the HTML page source, extract the ID, and
jump to this ID.

I've got a better method: put the URL of your blog article into your
clipboard (via ~C-l C-c~), press a magic shortcut in Emacs, and BAAAM!
you're right on spot.

How's that magic happening?

Just use the following Emacs lisp code snippet, adapt the ~domain~
string, and assign a keyboard shortcut:

#+begin_src elisp
  (defun my-jump-to-lazyblorg-heading-according-to-URL-in-clipboard ()
    "Retrieves an URL from the clipboard, gets its Org-mode source,
     extracts the ID of the article and jumps to its Org-mode heading"
    (interactive)
    (let (
          ;; Getting URL from the clipboard. Since it may contain
          ;; some text properties we are using substring-no-properties
          ;; function
          (url (substring-no-properties (current-kill 0)))
          ;; This is a check string: if the URL in the clipboard
          ;; doesn't start with this, an error message is shown
          (domain "http://karl-voit.at")
    )
      ;; Check if URL string is from my domain (all other strings do
      ;; not make any sense here)
      (if (string-prefix-p (upcase domain) (upcase url))
      ;; Retrieving content by URL into new buffer asynchronously
      (url-retrieve url
                        ;; call this lambda function when URL content is retrieved
            (lambda (status)
               ;; Extrating and preparing the ID
               (let* (
                                  ;; Limit the ID search to the top 1000 characters of the buffer
                  (pageheader (buffer-substring 1 1000))
                  ;; Start index of the id
                                  (start (string-match "<meta name=\"orgmode-id\" content=\"" pageheader))
                                  ;; End index of the id
                                  (end (string-match "\" />" pageheader start))
                                  ;; Amount of characters to skip for the openning tag
                                  (chars-to-skip (length "<meta name=\"orgmode-id\" content=\""))
                                  ;; Extract ID
                                  (lazyblorg-id (if (and start end (< start end))
                                                    ;; ... extract it and return.
                                                    (substring pageheader (+ start chars-to-skip) end)
                                                  nil))
                                  )
                 (message (concat "Looking for id:" lazyblorg-id " ..."))
                 (org-open-link-from-string (concat "id:" lazyblorg-id))
                 )
               )
            )
    (message (concat "Sorry: the URL \"" (substring url 0 (length domain)) "...\" doesn't start with \"" domain "\". Aborting."))
    )
      )
    )
#+end_src

** BONUS: Embedding External Things

- Do read [[https://github.com/novoid/lazyblorg/wiki/Orgmode-Elements#embedding-external-content][the Wiki]] for embedding external stuff like Tweets or YouTube
  videos.

* How to Thank Me

I'm glad you like my tools. If you want to support me:

- Send old-fashioned *postcard* per snailmail - I love personal feedback!
  - see [[http://tinyurl.com/j6w8hyo][my address]]
- Send feature wishes or improvements as an issue on GitHub
- Create issues on GitHub for bugs
- Contribute merge requests for bug fixes
- Check out my other cool [[https://github.com/novoid][projects on GitHub]]

If you want to contribute to this cool project, please fork and
contribute!

Issues, bugs,… are maintained in the [[https://github.com/novoid/lazyblorg/issues][GitHub issue tracker]].

I am using [[http://www.python.org/dev/peps/pep-0008/][Python PEP8]] and some ideas from [[http://en.wikipedia.org/wiki/Test-driven_development][Test Driven Development
(TDD)]].

* Local Variables                                                  :noexport:

[[http://karl-voit.at/temp/github/2017-06-04_lazyblorg_README.png]]

# Local Variables:
# mode: auto-fill
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
