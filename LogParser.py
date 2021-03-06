import sys
import operator
from misc import check_keys
from datetime import datetime
from collections import defaultdict


class LogParser(object):
    """LogParser class
       It passes the servicelog, stats frequency of all call trasactions.
       The stat result will be output into a file
    """
    def __init__(self, service_log, filter_str = ""):
        check_keys(["file_name", "start_date", "end_date"], service_log, 'service_log', basestring)
        check_keys(["date_index", "trans_id_index", "trans_code_index"], service_log, 'service_log', int)
        self._service_log = service_log
        self._filter = filter_str
        self._trans = defaultdict(list)
        self._trans_sorted = []
        self._code_2_meaning = {}

    def process_and_store(self, file_name):
        self._read_file()
        self._make_trans_and_sort()
        self._store_result(file_name)

    def _store_result(self, file_name):
        with open(file_name, 'w') as f:
            for one_trans in self._trans_sorted:
                f.write("{0}\t{1}\n".format(one_trans[0], one_trans[1]))

    def _read_file(self):
        current_date = datetime.strptime(self._service_log["start_date"], '%Y-%m-%d')
        with open(self._service_log['file_name'], 'r') as f:
            start_date = datetime.strptime(self._service_log["start_date"], '%Y-%m-%d')
            end_date = datetime.strptime(self._service_log["end_date"], '%Y-%m-%d')
            total_days = (end_date - start_date).days
            for line in f:
                items = line.split('\t')
                trans_id = items[self._service_log["trans_id_index"]]
                if self._filter != "" and trans_id[:len(self._filter)] != self._filter:
                    continue
                trans_code = items[self._service_log["trans_code_index"]]
                date_str = items[self._service_log["date_index"]]
                date = None
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    raise Exception('Invalid date {0}'.format(date_str))
                #new day
                if current_date != date:
                    current_date = date
                    percentage = str(100*(current_date - start_date).days/total_days)+'%'
                    sys.stdout.write('Processing data on {0}... {1} accomplished\r'\
                        .format(current_date.strftime('%Y-%m-%d'), percentage)) 
                self._trans[trans_id].append(trans_code)
        sys.stdout.write('\n')
        print "transaction number: ", len(self._trans)

    def _make_trans_and_sort(self):
    	trans_stat = defaultdict(int)
        for trans_items in self._trans.itervalues():
            itemset = []
            for one_item in trans_items:
                itemset.append(one_item)
            trans_key = '\t'.join(itemset)
            trans_stat[trans_key] += 1
        print "transaction types: ", len(trans_stat)
        self._trans_sorted = sorted(trans_stat.items(), key=operator.itemgetter(1), reverse=True)
            