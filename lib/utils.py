# -*- coding: utf-8; mode: python; -*-
# Time-stamp: <2017-02-12 15:05:13 vk>

import config
from sys import stdout, exit
import logging
from hashlib import md5  # generating checksums
from time import localtime  # for generating Org-mode timestamps
from orgformat import *
from operator import itemgetter  # for sorted()
import datetime


class Utils(object):
    """
    Class for providing misc utility methods.
    """

    # The stopword lists were obtained from:
    # http://anoncvs.postgresql.org/cvsweb.cgi/pgsql/src/backend/snowball/stopwords/
    # You can add as many languages as you wish. There have to be at least two of them.
    # Clearly, it helps when you omit stepwords that occur in multiple
    # languages.
    STOPWORDS = [('english', [u'I', u'me', u'my', u'myself', u'we', u'our', u'ours',
                              u'ourselves', u'you', u'your', u'yours', u'yourself',
                              u'yourselves', u'he', u'him', u'his', u'himself',
                              u'she', u'her', u'hers', u'herself', u'it', u'its',
                              u'itself', u'they', u'them', u'their', u'theirs', u'themselves',
                              u'what', u'which', u'who', u'whom', u'this', u'that',
                              u'these', u'those', u'is', u'are', u'were', u'be',
                              u'been', u'being', u'have', u'has', u'had', u'having',
                              u'do', u'does', u'did', u'doing', u'a', u'the',
                              u'and', u'but', u'if', u'or', u'because', u'as',
                              u'until', u'while', u'of', u'at', u'by', u'for',
                              u'with', u'about', u'against', u'between', u'into', u'through',
                              u'during', u'before', u'after', u'above', u'below', u'to',
                              u'from', u'up', u'down', u'on', u'off', u'over',
                              u'under', u'again', u'further', u'then', u'once', u'here',
                              u'there', u'when', u'where', u'why', u'how', u'all',
                              u'any', u'both', u'each', u'few', u'more', u'most',
                              u'other', u'some', u'such', u'no', u'nor', u'not',
                              u'only', u'own', u'same', u'than', u'too', u'very',
                              u'can', u'just', u'don', u'should', u'now']),
                 ('deutsch', [u'aber', u'alle', u'allem', u'allen', u'aller', u'alles', u'als',
                              u'also', u'ander', u'andere', u'anderem', u'anderen', u'anderer',
                              u'anderes', u'anderm', u'andern', u'anderr', u'anders', u'auch',
                              u'auf', u'aus', u'bei', u'bin', u'bis', u'bist',
                              u'da', u'damit', u'dann', u'der', u'den', u'des',
                              u'dem', u'die', u'das', u'daß', u'derselbe', u'derselben',
                              u'denselben', u'desselben', u'demselben', u'dieselbe', u'dieselben', u'dasselbe',
                              u'dazu', u'dein', u'deine', u'deinem', u'deinen', u'deiner',
                              u'deines', u'denn', u'derer', u'dessen', u'dich', u'dir',
                              u'du', u'dies', u'diese', u'diesem', u'diesen', u'dieser',
                              u'dieses', u'doch', u'dort', u'durch', u'ein', u'eine',
                              u'einem', u'einen', u'einer', u'eines', u'einig', u'einige',
                              u'einigem', u'einigen', u'einiger', u'einiges', u'einmal', u'er',
                              u'ihn', u'ihm', u'es', u'etwas', u'euer', u'eure',
                              u'eurem', u'euren', u'eurer', u'eures', u'für', u'gegen',
                              u'gewesen', u'hab', u'habe', u'haben', u'hat', u'hatte',
                              u'hatten', u'hier', u'hin', u'hinter', u'ich', u'mich',
                              u'mir', u'ihr', u'ihre', u'ihrem', u'ihren', u'ihrer',
                              u'ihres', u'euch', u'im', u'indem', u'ins', u'ist',
                              u'jede', u'jedem', u'jeden', u'jeder', u'jedes', u'jene',
                              u'jenem', u'jenen', u'jener', u'jenes', u'jetzt', u'kann',
                              u'kein', u'keine', u'keinem', u'keinen', u'keiner', u'keines',
                              u'können', u'könnte', u'machen', u'man', u'manche', u'manchem',
                              u'manchen', u'mancher', u'manches', u'mein', u'meine', u'meinem',
                              u'meinen', u'meiner', u'meines', u'mit', u'muss', u'musste',
                              u'nach', u'nicht', u'nichts', u'noch', u'nun', u'nur',
                              u'ob', u'oder', u'ohne', u'sehr', u'sein', u'seine',
                              u'seinem', u'seinen', u'seiner', u'seines', u'selbst', u'sich',
                              u'sie', u'ihnen', u'sind', u'solche', u'solchem', u'solchen',
                              u'solcher', u'solches', u'soll', u'sollte', u'sondern', u'sonst',
                              u'über', u'um', u'und', u'uns', u'unse', u'unsem',
                              u'unsen', u'unser', u'unses', u'unter', u'viel', u'vom',
                              u'von', u'vor', u'während', u'war', u'waren', u'warst',
                              u'weg', u'weil', u'weiter', u'welche', u'welchem', u'welchen',
                              u'welcher', u'welches', u'wenn', u'werde', u'werden', u'wie',
                              u'wieder', u'wir', u'wird', u'wirst', u'wo', u'wollen',
                              u'wollte', u'würde', u'wüden', u'zu', u'zum', u'zur',
                              u'zwar', u'zwischen'])]

    def __init__(self):

        pass

    @staticmethod
    def error_exit(errorcode):
        """
        Exits with return value of errorcode and prints to stderr.

        @param errorcode: integer that will be reported as return value.
        """

        logger = logging.getLogger('lazyblorg.Utils.error_exit')
        logger.debug("exiting with error code %s" % str(errorcode))

        stdout.flush()
        exit(errorcode)

    @staticmethod
    def error_exit_with_userlog(logfilename, errorcode, message):
        """
        Exits with return value of errorcode, prints to stderr,
        creates an entry in the user log file.

        @param logfilename: file name of the user log file
        @param errorcode: integer that will be reported as return value.
        @param message: error message
        """

        logger = logging.getLogger('lazyblorg.Utils.error_exit_with_userlog')
        logger.critical(message)
        Utils.append_logfile_entry(logfilename, 'critical', message)
        Utils.error_exit(errorcode)

    @staticmethod
    def initialize_logging(identifier, verbose, quiet):
        """Log handling and configuration"""

        logger = logging.getLogger(identifier)

        # create console handler and set level to debug
        ch = logging.StreamHandler()

        FORMAT = None
        if verbose:
            FORMAT = "%(levelname)-8s %(asctime)-15s %(message)s"
            ch.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        elif quiet:
            FORMAT = "%(levelname)-8s %(message)s"
            ch.setLevel(logging.ERROR)
            logger.setLevel(logging.ERROR)
        else:
            FORMAT = "%(levelname)-8s %(message)s"
            ch.setLevel(logging.INFO)
            logger.setLevel(logging.INFO)

        # create formatter
        formatter = logging.Formatter(FORMAT)

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

        # omit double output (default handler and my own handler):
        logger.propagate = False

        # "application" code
        ## logger.debug("debug message")
        ## logger.info("info message")
        ## logger.warn("warn message")
        ## logger.error("error message")
        ## logger.critical("critical message")

        # logger.debug("logging initialized")

        return logger

    @staticmethod
    def append_logfile_entry(filename, level, message):
        """Appends messages to the given log file."""

        logger = logging.getLogger('lazyblorg.Utils.append_logfile_entry')
        logger.debug("appending to Org-mode log-file %s" % (filename))

        with open(filename, 'a') as outputhandle:
            datetimestamp = OrgFormat.datetime(localtime())
    # add daily repeating that user gets it on agenda also on following days:
            datetimestamp = datetimestamp[:-1] + ' +1d>'

            outputhandle.write(u"\n** " +
                               datetimestamp +
                               " lazyblorg " + level.upper() + ": " +
                               message +
                               "\n")

    @staticmethod
    def __generate_checksum_for_blog_entry(title, content):
        """

        Creates a hash value which should be unique to the most
        important identifiers of content of a single blog entry.

        @param title: string of the blog entry title
        @param content: array of arrays containing the content of the blog entry
        @param return: hexadecimal value of the hash
        """

        return md5(str([title, content])).hexdigest()

    @staticmethod
    def _add_entry_to_entries_timeline_by_published(
            entries_timeline_by_published, entry):
        """
        Adds entry metadata to dict entries_timeline_by_published.

        The dict format is:
        - dict with year (int) as key, value = list of 12 MONTH
        - MONTH: list of 28-31 DAY
        - DAY: list of 0 to many entry-IDs

        : for year in sorted(entries_timeline_by_published.keys()):
        :     print year  ## 2008 = year
        :     for month in enumerate(entries_timeline_by_published[year], start=1):
        :         ## month = tuple(index, list of days)
        :         print month[0]  ## 1 = Jan
        :         for day in enumerate(month[1], start=1):
        :             ## day = tuple(index, list of IDs)
        :             print day[0]  ## 1 = Jan 1st
        :             for blogentry in day[1]:
        :                 print blogentry  ## id:2008-01-01-happy-new-year-entry, ...

        @param entries_timeline_by_published: dict as described above, status before adding new entry
        @param entry: data of a blog entry
        @param return dict as described above, status after adding new entry
        """

        # entry example:
        # {'category': 'TEMPORAL',
        #  'level': 2,
        #  'latestupdateTS': datetime.datetime(2013, 8, 24, 22, 49),
        #  'usertags': [],
        #  'title': u'Case5: not changed since 1st generation',
        #  'lbtags': [u'blog'],
        #  'content': [['par', u'known and matching previous run: ID, CREATED, checksum; differs: timestamp -> generate']],
        #  'created': datetime.datetime(2013, 8, 24, 22, 42),
        #  'rawcontent': u'CLOSED: [2013-08-24 Sat 22:49]\n:LOGBOOK:\n- State "DONE"       from ""           [2013-08-24 Sat 22:49]\n:END:\n:PROPERTY [...]\n\n',
        #  'finished-timestamp-history': [datetime.datetime(2013, 8, 24, 22, 49)],
        #  'id': u'case5'}

        # get oldest time-stamp out of finished_timestamp_history
        published = Utils.get_oldest_timestamp_for_entry(entry)
        # extract year, month, day
        year = published[0].year
        month = published[0].month
        day = published[0].day

        if year not in entries_timeline_by_published.keys():
            # initialize a new year when its first entry is found:
            entries_timeline_by_published[year] = [
                [],  # ignore month 0
                # January - with an additional day to ignore day 0 each month
                [[] for i in range(32)],
                [[] for i in range(30)],  # February
                [[] for i in range(32)],  # March
                [[] for i in range(31)],  # April
                [[] for i in range(32)],  # May
                [[] for i in range(31)],  # June
                [[] for i in range(32)],  # July
                [[] for i in range(32)],  # August
                [[] for i in range(31)],  # September
                [[] for i in range(32)],  # October
                [[] for i in range(31)],  # November
                [[] for i in range(32)]]  # December

        entries_timeline_by_published[year][month][day].append(entry['id'])

        return entries_timeline_by_published

    @staticmethod
    def get_year_of_first_entry(entries_timeline_by_published):
        """
        Returns int of year of first published non-hidden blog entry.

        @param entries_timeline_by_published: dict as described in documentation
        @param return: int of year of None
        """

        assert isinstance(entries_timeline_by_published, dict)

        if entries_timeline_by_published:
            return sorted(entries_timeline_by_published.keys())[0]
        else:
            return None

    @staticmethod
    def get_year_of_last_entry(entries_timeline_by_published):
        """
        Returns int of year of last published non-hidden blog entry.

        @param entries_timeline_by_published: dict as described in documentation
        @param return: int of year of None
        """

        assert isinstance(entries_timeline_by_published, dict)

        if entries_timeline_by_published:
            return sorted(entries_timeline_by_published.keys())[-1]
        else:
            return None

    @staticmethod
    def get_entries_of_published_date(
            entries_timeline_by_published,
            year=False,
            month=False,
            day=False):
        """
        Returns a list of non-hidden entries that were published. Optionally filtered by year, month, day.

        @param entries_timeline_by_published: dict as described in documentation
        @param return: list of ids
        """

        assert isinstance(entries_timeline_by_published, dict)

        if not entries_timeline_by_published:
            return []
        else:
            if day:
                assert(month)
                assert(year)
                return sorted(entries_timeline_by_published[year][month][day])
            elif month:
                assert(year)
                return sorted([item for monthlist in entries_timeline_by_published[
                              year][month] for item in monthlist])
            elif year:
                return sorted([item for yearlist in [item for monthlist in entries_timeline_by_published[
                              year] for item in monthlist] for item in yearlist])
            else:
                # this is really getting nasty here. Could not make it work
                # using another layer of [item for...]
                all_entries = []
                for year in entries_timeline_by_published.keys():
                    all_entries.extend(
                        Utils.get_entries_of_published_date(
                            entries_timeline_by_published, year))
                return sorted(all_entries)

    @staticmethod
    def generate_metadata_from_blogdata(blogdata):
        """
        Parses blogdata list and extracts ID, CREATED time-stamp, most
        current time-stamp, and generates a check-sum for the
        entry. The result is written in a dict.

        @param blogdata: array of entries as described in
        "dev/lazyblorg.org > Notes > Representation of blog data"
        @param return: array containing a dict with entries like: {
        <ID>: {created: <timestamp>, timestamp: <timestamp>, checksum:
        <checksum>}, ...}

        @param blogdata: content of the blog data
        @param return metadata: metadata content so far
        @param entries_timeline_by_published: dict of years with list of lists for each day with IDs to entries        """

        # metadata example:
        # {u'case5': {'category': 'TEMPORAL', 'latestupdateTS': datetime.datetime(2013, 8, 24, 22, 49), 'checksum': '511251b0827', 'created': datetime.datetime(2013, 8, 24, 22, 42)},
        # u'case4': {'category': 'TEMPORAL', 'latestupdateTS':
        # datetime.datetime(2013, 8, 24, 22, 49), 'checksum': '0b178606638',
        # 'created': datetime.datetime(2013, 8, 24, 22, 42)}}
        metadata = {}

        for entry in blogdata:

            # entry example:
            #{'category': 'TEMPORAL',
            # 'level': 2,
            # 'latestupdateTS': datetime.datetime(2013, 8, 24, 22, 49),
            # 'usertags': [],
            # 'title': u'Case5: not changed since 1st generation',
            # 'lbtags': [u'blog'],
            # 'content': [['par', u'known and matching previous run: ID, CREATED, checksum; differs: timestamp -> generate']],
            # 'created': datetime.datetime(2013, 8, 24, 22, 42),
            # 'rawcontent': u'CLOSED: [2013-08-24 Sat 22:49]\n:LOGBOOK:\n- State "DONE"       from ""           [2013-08-24 Sat 22:49]\n:END:\n:PROPERTY [...]\n\n',
            # 'finished-timestamp-history': [datetime.datetime(2013, 8, 24, 22, 49)],
            # 'id': u'case5'}

            entries_timeline_by_published = {}

            checksum = Utils.__generate_checksum_for_blog_entry(
                entry['title'], entry['content'])

            if entry['id'] in metadata.keys():
                logging.error("We got a duplicate ID in blogdata: \"" +
                              str(entry['id']) +
                              "\". Please correct it and re-run this tool.")
                #   [x['id'] for x in blogdata]
                Utils.error_exit(30)
            else:
                assert('created' in entry.keys())
                assert('latestupdateTS' in entry.keys())
                assert('title' in entry.keys())
                metadata[entry['id']] = {'created': entry['created'],
                                         'latestupdateTS': entry['latestupdateTS'],
                                         'checksum': checksum,
                                         'title': entry['title'],
                                         'category': entry['category']}
                if config.TAG_FOR_HIDDEN not in entry['usertags']:
                    entries_timeline_by_published = Utils._add_entry_to_entries_timeline_by_published(
                        entries_timeline_by_published, entry)
                    logging.debug(
                        'added entry to entries_timeline_by_published')
                else:
                    logging.debug(
                        'found hidden entry ' +
                        entry['id'] +
                        ', not adding to entries_timeline_by_published')

        return metadata, entries_timeline_by_published

    @staticmethod
    def OLDgenerate_metadata_from_blogdata(blogdata):
        """

        Parses blogdata list and extracts ID, CREATED time-stamp, most
        current time-stamp, and generates a check-sum for the
        entry. The result is written in a dict.

        @param blogdata: array of entries as described in
        "dev/lazyblorg.org > Notes > Representation of blog data"
        @param return: array containing a dict with entries like: {
        <ID>: {created: <timestamp>, timestamp: <timestamp>, checksum:
        <checksum>}, ...}
        """

        # FIXXME: ??? separate metadata according to TEMPORAL, ...
        metadata = {}

        for entry in blogdata[config.TEMPORAL]:
            metadata.update(
                Utils.__generate_metadata_from_blogdata_core(
                    metadata, entry, config.TEMPORAL))
        for entry in blogdata[config.TEMPLATES]:
            metadata += Utils.__generate_metadata_from_blogdata_core(
                metadata, entry, config.TEMPLATES)
        for entry in blogdata[config.PERSISTENT]:
            metadata += Utils.__generate_metadata_from_blogdata_core(
                metadata, entry, config.PERSISTENT)
        for entry in blogdata[config.TAGS]:
            metadata += Utils.__generate_metadata_from_blogdata_core(
                metadata, entry, config.TAGS)

        return metadata

    @staticmethod
    def list_of_dicts_are_equal(list1, list2, ignoreorder=False):
        """

        Dicts in Python are not sorted. So there is no simple
        comparison of dicts. This method compares two list containing
        dicts entry by entry.

        @param list1: a list containing dicts with key/value-pairs
        @param list2: a list containing dicts with key/value-pairs
        @param ignoreorder: consider two lists with different order but same content as equal
        @param return: True (if list1 equals list2) or False (otherwise)
        """

        logger = logging.getLogger('lazyblorg.Utils.list_of_dicts_are_equal')
        logger.debug("list_of_dicts_are_equal called")

        assert isinstance(list1, list)
        assert isinstance(list2, list)

        if len(list1) > 0:
            assert isinstance(list1[0], dict)
        if len(list2) > 0:
            assert isinstance(list2[0], dict)

        if len(list1) != len(list2):
            # quick check: if length differs, they are definitely different
            return False

        comparisonlist1 = list1
        comparisonlist2 = list2
        if ignoreorder:
            comparisonlist1 = sorted(list1)
            comparisonlist2 = sorted(list2)

        for entry in range(len(comparisonlist1)):
            # do the hard way: comparing content
            if not comparisonlist1[entry] == comparisonlist2[entry]:
                return False

        return True

    @staticmethod
    def __UNFINISHED_datastructs_are_equal(data1, data2, ignoreorder=False):
        """

        Comparing data structures is easy. However, if the order of
        lists is not important, there is no simple comparison. This
        method compares two data structures containing numbers, lists,
        or dicts entry by entry. Any parameter of type 'None' returns
        False.

        data1 or data2 could be of type: number, string, unicode,
        list, or dict

        NOTE: this method does NOT work properly yet. However, I do
        not need it this time. Please refer to tests/utils_test.py for
        test cases that show what is working or not.

        @param data1: first data structure to compare
        @param data2: second data structure to compare
        @param ignoreorder: consider two items with different order but same content as equal
        @param return: True (if data1 equals data2) or False (otherwise)
        """

        if not ignoreorder:
            return data1 == data2

        if data1 is None or data2 is None:
            # both arguments should exist
            return False

        elif not isinstance(data1, type(data2)):
            return False

        elif type(data1) in [int, float, long, complex, str, unicode]:
            return data1 == data2

        elif isinstance(data1, dict):

            # return Utils.dicts_are_equal(data1, data2, ignoreorder)
            # -> if dicts contain lists, this does not compare the list content!

            # check for trivial cases:
            if len(data1.keys()) != len(data2.keys()):
                return False
            if len(data1.keys()) == 0:
                return True

            # FIXXME: sorting the dict might be unnecessary since: {3:4, 'b':2} == {'b':2, 3:4}
            # dicts don't keep the order (unless using Ordered....)
            sorted1 = sorted(data1.items(), key=lambda t: t[0])
            sorted2 = sorted(data2.items(), key=lambda t: t[0])
            if sorted1 == sorted2:
                # if this is true, we do not have to walk through the content
                return True
            else:
                # sorted1/2 are lists of tuples now. Compare them:
                Utils.datastructs_are_equal(sorted1, sorted2, ignoreorder)

        elif isinstance(data1, list):

            # check for trivial cases:
            if len(data1) != len(data2):
                return False
            if len(data1) == 0:
                return True

            sorted1 = sorted(data1)
            sorted2 = sorted(data2)
            if sorted1 == sorted2:
                # if this is true, we do not have to walk through the content
                return True
            else:
                for element in range(len(sorted1)):
                    Utils.datastructs_are_equal(
                        sorted1[element], sorted2[element], ignoreorder)

        else:
            logger = logging.getLogger('lazyblorg.Utils.datastructs_are_equal')
            logger.error(
                "datastructs_are_equal() does not support parameters of type \"%s\" yet." %
                type(data1))
            return False

    @staticmethod
    def append_lists_in_dict(source, destination):
        """
        source = {'foo':[], 'bar':[42, 13]} and
        destination = {'foo':[1, 3], 'bar':[5]} will be merged to
        {'foo':[1, 3], 'bar':[5, 42, 13]} according to the keys defined in source.

        @param source: dict whose entries are lists which will be
        appended to the ones in destination.

        @param destination: dict whose entries are lists which will be
        extended by those of source.

        @return: dict destination whose entries are lists are extended
        by those of source. Returns False if source has a key which
        can not be found in destination.
        """

        result = destination

        for key in source:
            if key in result.keys():
                for element in source[key]:
                    result[key].append(element)
            else:
                # there is a key in source which can not be found in destination (yet).
                # create new key in destination containing the list of
                # source[key]:
                result[key] = source[key]

        return result

    @staticmethod
    def guess_language_from_stopword_percentages(textlist):
        """Returns a string of a language from STOPWORDS which is the best
        guess for the language of the text given by textlist.

        This method works with at least two languages up to many as
        long as the percentages of the stopwords differ enough
        (dominant language twice as much as the second one).

        @param textlist: list of strings with text that has to be
        looked at in order to guess its language according to the data
        stored in STOPWORDS.

        @return: either or False if the language could not be guessed clearly

        """

        # this does not make sense for only one language
        assert(len(Utils.STOPWORDS) > 1)
        assert(len(Utils.STOPWORDS[0]) == 2)  # just test first language

        # combine list of strings and split on whitespaces:
        textlist = " ".join(textlist).split()

        result = []  # example result: [['english', 40], ['deutsch', 0]]

        # determine stopword percentages of all given languages:
        for language in Utils.STOPWORDS:
            languagename = language[0]
            languagestopwords = language[1]
            stopwordpercentage = 100 * \
                len([word for word in textlist if word in languagestopwords]) / len(textlist)
            result.append([languagename, stopwordpercentage])

        sorted_result = sorted(result, key=itemgetter(
            1), reverse=True)  # sort according to percentage

        # dominant language has to have at least twice the stopword percentage
        # from the second one:
        if sorted_result[0][1] > 2 * sorted_result[1][1]:
            return sorted_result[0][0]
        else:
            logger = logging.getLogger(
                'lazyblorg.Utils.guess_language_from_stopword_percentages')
            logger.warning(
                "percentage of stopwords do not differ much: English: %s; German: %s" %
                (str(
                    sorted_result[0][1]), str(
                    sorted_result[1][1])))
            return False

    @staticmethod
    def normalize_lineendings(mystring):
        """
        The line ending of mystring will be changed to simple newlines
        """

        return mystring.replace('\r\n', '\n').replace('\r', '\n')

    @staticmethod
    def diff_two_lists(list1, list2, normalize_lineendings=False):
        """
        Compares two lists, visually printing first difference.
        Returns True, if lists are same; False otherwise.
        """

        if list1 == list2:
            return True

        for currentitem in range(len(list1)):
            if normalize_lineendings:
                string1 = Utils.normalize_lineendings(list1[currentitem])
                string2 = Utils.normalize_lineendings(list2[currentitem])
            else:
                string1 = list1[currentitem]
                string2 = list2[currentitem]
            if string1 != string2:
                print "=================  first difference  ===================== in line " + str(currentitem)
                print "       [" + str(list1[currentitem - 1]).rstrip() + "]"
                print "found  [" + str(list1[currentitem]).rstrip() + "]"
                print "       [" + str(list1[currentitem + 1]).rstrip() + "]"
                print "    ---------------  comparison data:  --------------------"
                print "       [" + str(list2[currentitem - 1]).rstrip() + "]"
                print "should [" + str(list2[currentitem]).rstrip() + "]"
                print "       [" + str(list2[currentitem + 1]).rstrip() + "]"
                print "=================                    ====================="
                return False

        logger = logging.getLogger('lazyblorg.Utils.diff_two_lists')
        if normalize_lineendings:
            logger.info(
                "Internal error: The two lists are not equal but I can't find the difference. They might differ in line ending format.")
            return True
        else:
            logger.error(
                "Internal error: The two lists are not equal but I can't find the difference.")

    @staticmethod
    def get_newest_timestamp_for_entry(entry):
        """
        Reads data of entry and returns datetime object of the newest
        time-stamp of the finished-timestamp-history.

        Example result: datetime(2013, 8, 29, 19, 40)

        Implicit assumptions:
        - newest: no blog article is from before 1970-01-01

        @param entry: data of a blog entry
        @param return: datetime object of its oldest time-stamp within finished-timestamp-history
        @param return: year: four digit year as string
        @param return: month: two digit month as string
        @param return: day: two digit day as string
        @param return: hours: two digit hours as string
        @param return: minutes: two digit minutes as string
        """

        return Utils.get_oldest_or_newest_timestamp_for_entry(entry, "NEWEST")

    @staticmethod
    def get_oldest_timestamp_for_entry(entry):
        """
        Reads data of entry and returns datetime object of the oldest
        time-stamp of the finished-timestamp-history.

        Example result: datetime(2013, 8, 29, 19, 40)

        Implicit assumptions:
        - no blog article is from the future (comparison to now)

        @param entry: data of a blog entry
        @param return: datetime object of its oldest time-stamp within finished-timestamp-history
        @param return: year: four digit year as string
        @param return: month: two digit month as string
        @param return: day: two digit day as string
        @param return: hours: two digit hours as string
        @param return: minutes: two digit minutes as string
        """

        return Utils.get_oldest_or_newest_timestamp_for_entry(entry, "OLDEST")

    @staticmethod
    def get_oldest_or_newest_timestamp_for_entry(entry, search_for):
        """
        Reads data of entry and returns datetime object of the oldest or newest
        time-stamp of the finished-timestamp-history.

        Example result: datetime(2013, 8, 29, 19, 40)

        Implicit assumptions:
        - oldest: no blog article is from the future (comparison to now)
        - newest: no blog article is from before 1970-01-01

        @param entry: data of a blog entry
        @param search_for: string "OLDEST" or "NEWEST"
        @param return: datetime object of its oldest time-stamp within finished-timestamp-history
        @param return: year: four digit year as string
        @param return: month: two digit month as string
        @param return: day: two digit day as string
        @param return: hours: two digit hours as string
        @param return: minutes: two digit minutes as string
        """

        assert(entry)
        assert(isinstance(entry, dict))
        assert('finished-timestamp-history' in entry.keys())
        assert(search_for == "OLDEST" or search_for == "NEWEST")

        returntimestamp = False
        if search_for == "OLDEST":
            oldesttimestamp = datetime.datetime.now()
            for timestamp in entry['finished-timestamp-history']:
                if timestamp < oldesttimestamp:
                    oldesttimestamp = timestamp
            returntimestamp = oldesttimestamp
        elif search_for == "NEWEST":
            newesttimestamp = datetime.datetime(1970, 1, 1)
            for timestamp in entry['finished-timestamp-history']:
                if timestamp > newesttimestamp:
                    newesttimestamp = timestamp
            returntimestamp = newesttimestamp

        return returntimestamp, Utils.get_YY_MM_DD_HH_MM_from_datetime(returntimestamp)

    @staticmethod
    def get_YY_MM_DD_HH_MM_from_datetime(timestamp):
        """
        Returns zfilled strings of a datetime.datetime object as a tuple

        @param timestamp: datetime object
        @param return: year: four digit year as string
        @param return: month: two digit month as string
        @param return: day: two digit day as string
        @param return: hours: two digit hours as string
        @param return: minutes: two digit minutes as string
        """

        assert(type(timestamp) == datetime.datetime)

        return str(timestamp.year).zfill(2), str(
            timestamp.month).zfill(2), str(
            timestamp.day).zfill(2), str(
                timestamp.hour).zfill(2), str(
                    timestamp.minute).zfill(2)

# Local Variables:
# mode: flyspell
# eval: (ispell-change-dictionary "en_US")
# End:
