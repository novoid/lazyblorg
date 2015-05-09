#!/usr/bin/env python
# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2015-05-09 12:11:57 vk>

#import config  ## lazyblorg-global settings
import unittest
from lib.utils import *

class TestUtils(unittest.TestCase):

    ## FIXXME: (Note) These test are *not* exhaustive unit tests.

    logging = None


    def setUp(self):
        verbose = False
        quiet = False
        self.logging = Utils.initialize_logging("lazyblorg.tests", verbose, quiet)


    def tearDown(self):
        pass


    def test_list_of_dicts_are_equal(self):

        ## lists have different length
        list1 = [{ 'a':1 }]
        list2 = [{ 'a':1 }, {'b':2}]

        self.assertTrue(Utils.list_of_dicts_are_equal(list1, list1))
        self.assertTrue(Utils.list_of_dicts_are_equal(list2, list2))
        self.assertFalse(Utils.list_of_dicts_are_equal(list1, list2))

        ## lists differ only in key
        list1 = [{ 'a':1, 'b':2, 'c':3 }]
        list2 = [{ 'a':2, 'b':2, 'd':3 }]

        self.assertTrue(Utils.list_of_dicts_are_equal(list1, list1))
        self.assertTrue(Utils.list_of_dicts_are_equal(list2, list2))
        self.assertFalse(Utils.list_of_dicts_are_equal(list1, list2))

        ## lists differ only in value
        list1 = [{ 'a':1, 'b':2, 'c':3 }]
        list2 = [{ 'a':2, 'b':2, 'c':4 }]

        self.assertTrue(Utils.list_of_dicts_are_equal(list1, list1))
        self.assertTrue(Utils.list_of_dicts_are_equal(list2, list2))
        self.assertFalse(Utils.list_of_dicts_are_equal(list1, list2))

        ## value differs only in second dict
        list1 = [{ 'a':1 }, { 'b':2, 'c':3 }]
        list2 = [{ 'a':1 }, { 'b':2, 'c':4 }]

        self.assertTrue(Utils.list_of_dicts_are_equal(list1, list1))
        self.assertTrue(Utils.list_of_dicts_are_equal(list2, list2))
        self.assertFalse(Utils.list_of_dicts_are_equal(list1, list2))

        ## lists only have different sorting order (but are equal)
        list1 = [{ 'a':1 }, { 'b':2, 'c':3 }]
        list2 = [{ 'b':2, 'c':3 }, { 'a':1 }]

        self.assertTrue(Utils.list_of_dicts_are_equal(list1, list1))
        self.assertTrue(Utils.list_of_dicts_are_equal(list2, list2))
        self.assertFalse(Utils.list_of_dicts_are_equal(list1, list2, ignoreorder=False))
        self.assertTrue(Utils.list_of_dicts_are_equal(list1, list2, ignoreorder=True))

    def notest_datastructs_are_equal(self):

        self.assertTrue(Utils.datastructs_are_equal(1, 1))
        self.assertTrue(Utils.datastructs_are_equal(42.21, 42.21))
        self.assertTrue(Utils.datastructs_are_equal('foo', 'foo'))
        self.assertTrue(Utils.datastructs_are_equal(u'foo', u'foo'))

        self.assertTrue(Utils.datastructs_are_equal([], []))
        self.assertTrue(Utils.datastructs_are_equal([1, 2], [1, 2]))
        self.assertFalse(Utils.datastructs_are_equal([1, 2], [2, 1]))
        self.assertTrue(Utils.datastructs_are_equal([1, 2],
                                                    [2, 1], ignoreorder=True))
        self.assertFalse(Utils.datastructs_are_equal([1, 2],
                                                     [2, 1], ignoreorder=False))
        self.assertTrue(Utils.datastructs_are_equal([5, 'a'],
                                                    [5, 'a']))
        self.assertFalse(Utils.datastructs_are_equal([5, 'a'],
                                                     [5, 'a', 43.12]))
        self.assertTrue(Utils.datastructs_are_equal([43.12, 5, 'a'],
                                                    [5, 'a', 43.12], ignoreorder=True))
        self.assertFalse(Utils.datastructs_are_equal([43.12, 5, 'a'],
                                                     [5, 'a', 43.12], ignoreorder=False))

        self.assertTrue(Utils.datastructs_are_equal({}, {}))
        self.assertTrue(Utils.datastructs_are_equal({'a':1},
                                                    {'a':1}))
        self.assertFalse(Utils.datastructs_are_equal({'a':1},
                                                     {'b':1}))
        self.assertFalse(Utils.datastructs_are_equal({'a':1},
                                                     {'a':2}))
        self.assertTrue(Utils.datastructs_are_equal({'a':[], 2:{'b':'c'}},
                                                    {'a':[], 2:{'b':'c'}}))
        self.assertFalse(Utils.datastructs_are_equal({'a':[], 2:{'b':'c'}},
                                                     {'a':[], 2:{'b':'X'}}))
        self.assertTrue(Utils.datastructs_are_equal({'a':[], 2:{'b':['foo', {'bar':[2,3,4]}]}},
                                                    {'a':[], 2:{'b':['foo', {'bar':[2,3,4]}]}}))
        self.assertTrue(Utils.datastructs_are_equal({2:{'b':[{'bar':[2,3,4]}, 'foo']}, 'a':[]},
                                                    {'a':[], 2:{'b':['foo', {'bar':[2,3,4]}]}}))
        self.assertFalse(Utils.datastructs_are_equal({'a':[], 2:{'b':['foo', {'bar':[2,3,4]}]}},
                                                     {'a':[], 2:{'b':['foo', {'bar':[2,3,4,5]}]}}))

    def test_append_lists_in_dict(self):

        source = {}
        destination = {}
        result = {}
        self.assertEqual(Utils.append_lists_in_dict(source, destination), result)

        source = {'foo':[]}
        destination = {}
        result = {'foo':[]}
        self.assertEqual(Utils.append_lists_in_dict(source, destination), result)

        source = {}
        destination = {'foo':[]}
        result = {'foo':[]}
        self.assertEqual(Utils.append_lists_in_dict(source, destination), result)

        source = {'foo':[23, 42]}
        destination = {'foo':[74]}
        result = {'foo':[23, 42, 74]}
        self.assertEqual(Utils.append_lists_in_dict(source, destination)['foo'].sort(),
                         result['foo'].sort())

        source = {'foo':[23, 42, 'other']}
        destination = {'foo':[74], 'bar':['test', 302]}
        result = {'foo':[74, 23, 42, 'other'], 'bar':['test', 302]}
        self.assertEqual(Utils.append_lists_in_dict(source, destination),
                         result)

    def test_guess_language_from_stopword_percentages(self):

        EXAMPLE_TEXTS_GERMAN = [u"Ohne Anspruch auf irgendeine Art von Experte in dem Gebiet zu sein,\n" +
                                u"selftelle ich hier eine meiner Meinung nach interessante Theorie in den\n" +
                                u"Raum: diente die Fastenzeit in früheren Tagen (auch) dazu, um\n" +
                                u"Aufstände in der Bevölkerung zu unterbinden?",
                                u"Bekanntermaßen hat die katholische Kirche bereits davor existierende\n" +
                                u"Feiertage mit ihren eigenen \"überschrieben\", damit die Ungläubigen\n" +
                                u"weiterhin zu den selben Zeiten etwas zu feiern haben und die \"neuen\"\n" +
                                u"Feiertage leichter eingeführt werden können (Quellen: [[http://www.rpi-loccum.de" +
                                u"/wettbewerbe/jugend/beitr/feiertage.html][1 deutsch]], " +
                                u"[[http://godkind.org/pagan-holidays.html][2\n" +
                                u"deutsch]], [[http://www.goodnewsaboutgod.com/studies/holidays2.htm][3 englisch]]," +
                                u" [1]).\n\n" +
                                u"Beispielsweise hängen [[https://de.wikipedia.org/wiki/Weihnachten#Au.C3.9" +
                                u"Ferchristliche_Parallelen][Weihnachten]] und die [[https://de.wikipedia.org/" +
                                u"wiki/Wintersonnenwende#Feste_und_Feiern][Wintersonnenwende]] zusammen\n" +
                                u"und Ostern mit diversen [[https://de.wikipedia.org/wiki/Ostern#Fr.C3." +
                                u"BChlingsfeste][Frühlingsfesten]].\n",
                                u"Nun kam mir der Gedanke, dass die Fastenzeit eventuell einen\n" +
                                u"(zusätzlichen?) politischen Zweck erfüllte: Am Ende der kalten\n" +
                                u"Jahreszeit wird wohl nach schlechteren Ernten die\n" +
                                u"Lebensmittelknappheit eine gewisse Unruhe verursacht\n" +
                                u"haben. Bevölkerung mit Hunger war schon immer eine explosive Sache. Da\n" +
                                u"ist es doch praktisch, dass die katholische Kirche eine gewisse\n" +
                                u"Enthaltsamkeit mit Religion als Begründung vorschreibt.\n\n" +
                                u"Dadurch wird durchaus eine generelle Missstimmung vermindert, die\n" +
                                u"sich ansonsten zu Aufständen hochschaukeln könnte.\n\n" +
                                u"Ich konnte bei meiner kurzen Internetrecherche nichts zu dem Thema\n" +
                                u"finden. Wenn du etwas dazu weißt oder findest, freue ich mich über\n" +
                                u"einen Kommentar (siehe Link unten)."]

        EXAMPLE_TEXTS_ENGLISH = [u"Update 2014-05-14: added real world example\n\n" +
                                 u"Update 2015-03-16: filtering photographs according to their GPS coordinates\n\n" +
                                 u"I am a passionate photographer when being on vacation or whenever I\n" +
                                 u"see something beautiful. This way, I collected many [[https://en.wikipedia.org/" +
                                 u"wiki/Jpeg][JPEG]] files over\n" +
                                 u"the past years. Here, I describe how I manage my digital photographs\n" +
                                 u"while avoiding any [[http://en.wikipedia.org/wiki/Vendor_lock-in][vendor " +
                                 u"lock-in]] which binds me to a temporary\n" +
                                 u"solution and leads to loss of data. Instead, I prefer solutions where\n" +
                                 u"I am able to *invest my time and effort for a long-term relationship*.\n\n" +
                                 u"This (very long) entry is *not about image files only*: I am going to\n" +
                                 u"explain further things like my folder hierarchy, file name convention,\n" +
                                 u"and so forth. Therefore, this information applies to all kind of\n" +
                                 u"files I process.\n\n" +
                                 u"Before I start explaining my method, we should come to an agreement\n" +
                                 u"whether or not we do have the same set of requirements I am trying to\n" +
                                 u"match with my method. If you are into [[https://en.wikipedia.org/wiki/" +
                                 u"Raw_image_format][raw image formats]], storing your\n" +
                                 u"photographs somewhere in the cloud or anything else very special to\n" +
                                 u"you (and not to me), you might not get satisfied with the things\n" +
                                 u"described here. Decide yourself.\n"]

        assert(Utils.STOPWORDS[0][0] == 'english')
        assert(Utils.STOPWORDS[1][0] == 'deutsch')

        assert(Utils.guess_language_from_stopword_percentages(EXAMPLE_TEXTS_ENGLISH) == 'english')
        assert(Utils.guess_language_from_stopword_percentages(EXAMPLE_TEXTS_GERMAN) == 'deutsch')
        assert(Utils.guess_language_from_stopword_percentages(EXAMPLE_TEXTS_ENGLISH + 2 * EXAMPLE_TEXTS_GERMAN) is False)


# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
