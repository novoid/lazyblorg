#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

# import config  ## lazyblorg-global settings
import unittest
from lib.utils import *


class TestUtils(unittest.TestCase):

    # FIXXME: (Note) These test are *not* exhaustive unit tests.

    logging = None

    def setUp(self):
        verbose = False
        quiet = False
        self.logging = Utils.initialize_logging(
            "lazyblorg.tests", verbose, quiet)

    def tearDown(self):
        pass

    def test_list_of_dicts_are_equal(self):

        # lists have different length
        list1 = [{'a': 1}]
        list2 = [{'a': 1}, {'b': 2}]

        self.assertTrue(Utils.list_of_dicts_are_equal(list1, list1))
        self.assertTrue(Utils.list_of_dicts_are_equal(list2, list2))
        self.assertFalse(Utils.list_of_dicts_are_equal(list1, list2))

        # lists differ only in key
        list1 = [{'a': 1, 'b': 2, 'c': 3}]
        list2 = [{'a': 2, 'b': 2, 'd': 3}]

        self.assertTrue(Utils.list_of_dicts_are_equal(list1, list1))
        self.assertTrue(Utils.list_of_dicts_are_equal(list2, list2))
        self.assertFalse(Utils.list_of_dicts_are_equal(list1, list2))

        # lists differ only in value
        list1 = [{'a': 1, 'b': 2, 'c': 3}]
        list2 = [{'a': 2, 'b': 2, 'c': 4}]

        self.assertTrue(Utils.list_of_dicts_are_equal(list1, list1))
        self.assertTrue(Utils.list_of_dicts_are_equal(list2, list2))
        self.assertFalse(Utils.list_of_dicts_are_equal(list1, list2))

        # value differs only in second dict
        list1 = [{'a': 1}, {'b': 2, 'c': 3}]
        list2 = [{'a': 1}, {'b': 2, 'c': 4}]

        self.assertTrue(Utils.list_of_dicts_are_equal(list1, list1))
        self.assertTrue(Utils.list_of_dicts_are_equal(list2, list2))
        self.assertFalse(Utils.list_of_dicts_are_equal(list1, list2))

        # lists only have different sorting order (but are equal)
        list1 = [{'a': 1}, {'b': 2, 'c': 3}]
        list2 = [{'b': 2, 'c': 3}, {'a': 1}]

        self.assertTrue(Utils.list_of_dicts_are_equal(list1, list1))
        self.assertTrue(Utils.list_of_dicts_are_equal(list2, list2))

    def notest_datastructs_are_equal(self):

        self.assertTrue(Utils.datastructs_are_equal(1, 1))
        self.assertTrue(Utils.datastructs_are_equal(42.21, 42.21))
        self.assertTrue(Utils.datastructs_are_equal('foo', 'foo'))
        self.assertTrue(Utils.datastructs_are_equal('foo', 'foo'))

        self.assertTrue(Utils.datastructs_are_equal([], []))
        self.assertTrue(Utils.datastructs_are_equal([1, 2], [1, 2]))
        self.assertFalse(Utils.datastructs_are_equal([1, 2], [2, 1]))
        self.assertTrue(Utils.datastructs_are_equal([1, 2],
                                                    [2, 1], ignoreorder=True))
        self.assertFalse(Utils.datastructs_are_equal(
            [1, 2], [2, 1], ignoreorder=False))
        self.assertTrue(Utils.datastructs_are_equal([5, 'a'],
                                                    [5, 'a']))
        self.assertFalse(Utils.datastructs_are_equal([5, 'a'],
                                                     [5, 'a', 43.12]))
        self.assertTrue(Utils.datastructs_are_equal(
            [43.12, 5, 'a'], [5, 'a', 43.12], ignoreorder=True))
        self.assertFalse(Utils.datastructs_are_equal(
            [43.12, 5, 'a'], [5, 'a', 43.12], ignoreorder=False))

        self.assertTrue(Utils.datastructs_are_equal({}, {}))
        self.assertTrue(Utils.datastructs_are_equal({'a': 1},
                                                    {'a': 1}))
        self.assertFalse(Utils.datastructs_are_equal({'a': 1},
                                                     {'b': 1}))
        self.assertFalse(Utils.datastructs_are_equal({'a': 1},
                                                     {'a': 2}))
        self.assertTrue(Utils.datastructs_are_equal({'a': [], 2: {'b': 'c'}},
                                                    {'a': [], 2: {'b': 'c'}}))
        self.assertFalse(Utils.datastructs_are_equal({'a': [], 2: {'b': 'c'}},
                                                     {'a': [], 2: {'b': 'X'}}))
        self.assertTrue(Utils.datastructs_are_equal({'a': [], 2: {'b': ['foo', {'bar': [2, 3, 4]}]}},
                                                    {'a': [], 2: {'b': ['foo', {'bar': [2, 3, 4]}]}}))
        self.assertTrue(Utils.datastructs_are_equal({2: {'b': [{'bar': [2, 3, 4]}, 'foo']}, 'a': []},
                                                    {'a': [], 2: {'b': ['foo', {'bar': [2, 3, 4]}]}}))
        self.assertFalse(Utils.datastructs_are_equal({'a': [], 2: {'b': ['foo', {
                         'bar': [2, 3, 4]}]}}, {'a': [], 2: {'b': ['foo', {'bar': [2, 3, 4, 5]}]}}))

    def test_append_lists_in_dict(self):

        source = {}
        destination = {}
        result = {}
        self.assertEqual(
            Utils.append_lists_in_dict(
                source, destination), result)

        source = {'foo': []}
        destination = {}
        result = {'foo': []}
        self.assertEqual(
            Utils.append_lists_in_dict(
                source, destination), result)

        source = {}
        destination = {'foo': []}
        result = {'foo': []}
        self.assertEqual(
            Utils.append_lists_in_dict(
                source, destination), result)

        source = {'foo': [23, 42]}
        destination = {'foo': [74]}
        result = {'foo': [23, 42, 74]}
        self.assertEqual(
            Utils.append_lists_in_dict(
                source,
                destination)['foo'].sort(),
            result['foo'].sort())

        source = {'foo': [23, 42, 'other']}
        destination = {'foo': [74], 'bar': ['test', 302]}
        result = {'foo': [74, 23, 42, 'other'], 'bar': ['test', 302]}
        self.assertEqual(Utils.append_lists_in_dict(source, destination),
                         result)

    def test_guess_language_from_stopword_percentages(self):

        EXAMPLE_TEXTS_GERMAN = [
            "Ohne Anspruch auf irgendeine Art von Experte in dem Gebiet zu sein,\n" +
            "selftelle ich hier eine meiner Meinung nach interessante Theorie in den\n" +
            "Raum: diente die Fastenzeit in früheren Tagen (auch) dazu, um\n" +
            "Aufstände in der Bevölkerung zu unterbinden?",
            "Bekanntermaßen hat die katholische Kirche bereits davor existierende\n" +
            "Feiertage mit ihren eigenen \"überschrieben\", damit die Ungläubigen\n" +
            "weiterhin zu den selben Zeiten etwas zu feiern haben und die \"neuen\"\n" +
            "Feiertage leichter eingeführt werden können (Quellen: [[http://www.rpi-loccum.de" +
            "/wettbewerbe/jugend/beitr/feiertage.html][1 deutsch]], " +
            "[[http://godkind.org/pagan-holidays.html][2\n" +
            "deutsch]], [[http://www.goodnewsaboutgod.com/studies/holidays2.htm][3 englisch]]," +
            " [1]).\n\n" +
            "Beispielsweise hängen [[https://de.wikipedia.org/wiki/Weihnachten#Au.C3.9" +
            "Ferchristliche_Parallelen][Weihnachten]] und die [[https://de.wikipedia.org/" +
            "wiki/Wintersonnenwende#Feste_und_Feiern][Wintersonnenwende]] zusammen\n" +
            "und Ostern mit diversen [[https://de.wikipedia.org/wiki/Ostern#Fr.C3." +
            "BChlingsfeste][Frühlingsfesten]].\n",
            "Nun kam mir der Gedanke, dass die Fastenzeit eventuell einen\n" +
            "(zusätzlichen?) politischen Zweck erfüllte: Am Ende der kalten\n" +
            "Jahreszeit wird wohl nach schlechteren Ernten die\n" +
            "Lebensmittelknappheit eine gewisse Unruhe verursacht\n" +
            "haben. Bevölkerung mit Hunger war schon immer eine explosive Sache. Da\n" +
            "ist es doch praktisch, dass die katholische Kirche eine gewisse\n" +
            "Enthaltsamkeit mit Religion als Begründung vorschreibt.\n\n" +
            "Dadurch wird durchaus eine generelle Missstimmung vermindert, die\n" +
            "sich ansonsten zu Aufständen hochschaukeln könnte.\n\n" +
            "Ich konnte bei meiner kurzen Internetrecherche nichts zu dem Thema\n" +
            "finden. Wenn du etwas dazu weißt oder findest, freue ich mich über\n" +
            "einen Kommentar (siehe Link unten)."]

        EXAMPLE_TEXTS_ENGLISH = [
            "Update 2014-05-14: added real world example\n\n" +
            "Update 2015-03-16: filtering photographs according to their GPS coordinates\n\n" +
            "I am a passionate photographer when being on vacation or whenever I\n" +
            "see something beautiful. This way, I collected many [[https://en.wikipedia.org/" +
            "wiki/Jpeg][JPEG]] files over\n" +
            "the past years. Here, I describe how I manage my digital photographs\n" +
            "while avoiding any [[http://en.wikipedia.org/wiki/Vendor_lock-in][vendor " +
            "lock-in]] which binds me to a temporary\n" +
            "solution and leads to loss of data. Instead, I prefer solutions where\n" +
            "I am able to *invest my time and effort for a long-term relationship*.\n\n" +
            "This (very long) entry is *not about image files only*: I am going to\n" +
            "explain further things like my folder hierarchy, file name convention,\n" +
            "and so forth. Therefore, this information applies to all kind of\n" +
            "files I process.\n\n" +
            "Before I start explaining my method, we should come to an agreement\n" +
            "whether or not we do have the same set of requirements I am trying to\n" +
            "match with my method. If you are into [[https://en.wikipedia.org/wiki/" +
            "Raw_image_format][raw image formats]], storing your\n" +
            "photographs somewhere in the cloud or anything else very special to\n" +
            "you (and not to me), you might not get satisfied with the things\n" +
            "described here. Decide yourself.\n"]

        assert(Utils.STOPWORDS[0][0] == 'english')
        assert(Utils.STOPWORDS[1][0] == 'deutsch')

        assert(Utils.guess_language_from_stopword_percentages(
            EXAMPLE_TEXTS_ENGLISH) == 'english')
        assert(Utils.guess_language_from_stopword_percentages(
            EXAMPLE_TEXTS_GERMAN) == 'deutsch')
        assert(Utils.guess_language_from_stopword_percentages(
            EXAMPLE_TEXTS_ENGLISH + 2 * EXAMPLE_TEXTS_GERMAN) is False)

    def test_entries_timeline_by_published_functions(
            entries_timeline_by_published):

        # simple tests using only a faked dict of years:

        entries_timeline_by_published = {
            2014: [], 1975: [], 1983: [], 2099: [], 2042: []}

        assert(Utils.get_year_of_first_entry(
            entries_timeline_by_published) == 1975)
        assert(Utils.get_year_of_last_entry(
            entries_timeline_by_published) == 2099)

        # tests using partly filled entries:

        entry = {'finished-timestamp-history': [datetime.datetime(1991, 12, 29, 19, 40),
                                                datetime.datetime(1990, 12, 31, 23, 59),
                                                datetime.datetime(1993, 1, 29, 19, 40)],
                 'category': 'TEMPORAL',
                 'id': 'id:1990-12-31-foo'}

        entries_timeline_by_published = Utils._add_entry_to_entries_timeline_by_published({
        }, entry)

        entry = {'finished-timestamp-history': [datetime.datetime(1991, 12, 29, 19, 40),
                                                datetime.datetime(1990, 12, 31, 23, 59),
                                                datetime.datetime(1993, 1, 29, 19, 40)],
                 'category': 'TEMPORAL',
                 'id': 'id:1990-12-31-bar'}

        entries_timeline_by_published = Utils._add_entry_to_entries_timeline_by_published(
            entries_timeline_by_published, entry)

        entry = {'finished-timestamp-history': [datetime.datetime(2011, 12, 29, 19, 40),
                                                datetime.datetime(2008, 1, 20, 19, 40),
                                                datetime.datetime(2013, 1, 29, 19, 40)],
                 'category': 'TEMPORAL',
                 'id': 'id:2008-01-20-foo'}

        entries_timeline_by_published = Utils._add_entry_to_entries_timeline_by_published(
            entries_timeline_by_published, entry)

        entry = {'finished-timestamp-history': [datetime.datetime(2011, 12, 29, 19, 40),
                                                datetime.datetime(2008, 5, 17, 19, 40),
                                                datetime.datetime(2013, 1, 29, 19, 40)],
                 'category': 'TEMPORAL',
                 'id': 'id:2008-05-17-foo'}

        entries_timeline_by_published = Utils._add_entry_to_entries_timeline_by_published(
            entries_timeline_by_published, entry)

        entry = {'finished-timestamp-history': [datetime.datetime(2011, 12, 29, 19, 40),
                                                datetime.datetime(2008, 1, 29, 19, 40),
                                                datetime.datetime(2013, 1, 29, 19, 40)],
                 'category': 'TEMPORAL',
                 'id': 'id:2008-01-29-foo'}

        entries_timeline_by_published = Utils._add_entry_to_entries_timeline_by_published(
            entries_timeline_by_published, entry)

        assert(Utils.get_year_of_first_entry(
            entries_timeline_by_published) == 1990)
        assert(Utils.get_year_of_last_entry(
            entries_timeline_by_published) == 2008)

        assert(
            Utils.get_entries_of_published_date(
                entries_timeline_by_published,
                year=2008,
                month=0o1,
                day=29) == ['id:2008-01-29-foo'])

        assert(
            Utils.get_entries_of_published_date(
                entries_timeline_by_published,
                year=1990,
                month=12,
                day=31) == [
                'id:1990-12-31-bar',
                'id:1990-12-31-foo'])

        assert(
            Utils.get_entries_of_published_date(
                entries_timeline_by_published,
                year=2008,
                month=0o1,
                day=29) == ['id:2008-01-29-foo'])

        assert(
            Utils.get_entries_of_published_date(
                entries_timeline_by_published,
                year=2008,
                month=0o1) == [
                'id:2008-01-20-foo',
                'id:2008-01-29-foo'])

        assert(
            Utils.get_entries_of_published_date(
                entries_timeline_by_published,
                year=2008) == [
                'id:2008-01-20-foo',
                'id:2008-01-29-foo',
                'id:2008-05-17-foo'])

        assert(
            Utils.get_entries_of_published_date(entries_timeline_by_published) == [
                'id:1990-12-31-bar',
                'id:1990-12-31-foo',
                'id:2008-01-20-foo',
                'id:2008-01-29-foo',
                'id:2008-05-17-foo'])

        print('\nBEGIN debug output of entries_timeline_by_published: ' + '=' * 20)
        for year in sorted(entries_timeline_by_published.keys()):
            for month in enumerate(
                    entries_timeline_by_published[year],
                    start=0):
                # month = tuple(index, list of days)
                for day in enumerate(month[1], start=0):
                    # day = tuple(index, list of IDs)
                    for blogentry in day[1]:
                        print(str(year) + '-' + str(month[0]) + '-' + str(day[0]) + " has entry: " + str(blogentry))
        print('END debug output of entries_timeline_by_published: ' + '=' * 20)


# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
