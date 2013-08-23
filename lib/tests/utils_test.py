#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2013-08-23 13:29:50 vk>

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

# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
