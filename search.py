#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import pickle
from collections import defaultdict
import collections
import math
from nltk.stem.porter import *

DOC_LEN_FILENAME = 'doc-len.txt'
DOCIDS_FILENAME = 'doc-ids.txt'
K = 10


class Search:
    # define common variables that are accessed in search
    def __init__(self, dictionary, filename_postings, docIDs=None, length=None):
        self.dictionary = dictionary
        self.FILENAME_POSTINGS = filename_postings
        self.docIDs = docIDs
        self.length = length


def usage():
    print("usage: " +
          sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def get_w_tq(t, count, s):
    # calculate w(t,q)

    tf = count[t]                        # frequency of term in query
    log_tf = 1 + math.log(tf, 10)

    df, _ = s.dictionary[t]
    N = len(s.docIDs)
    idf = math.log(N/df, 10)

    w_tq = log_tf * idf
    return w_tq


def cosine_score(tokens, s):
    scores = defaultdict(float)
    uniqueTokens = set(tokens)
    count = collections.Counter(tokens)

    # loop through all query terms
    for t in uniqueTokens:
        if t not in s.dictionary:
            # if term not found, continue to next term
            continue

        # calculate w(t,q)
        w_tq = get_w_tq(t, count, s)

        # fetch postings list for t
        _, pos = s.dictionary[t]
        with open(s.FILENAME_POSTINGS, 'rb') as f:
            f.seek(pos)
            posting = pickle.load(f)

            for doc, tf in posting:
                w_td = 1 + math.log(tf, 10)     # calculate log tf for document
                scores[doc] += (w_td * w_tq)

    for d, score in scores.items():
        scores[d] = score/s.length[d]

    # sort by decreasing value (score) and then increasing key (docID)
    res = sorted(scores.items(), key=lambda x: (-x[1], x[0]))

    res = [x[0] for x in res[:K]]
    # for d in res:
    #     print(f'document {d} has score {scores[d]}')
    return res


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """

    # load dictionary into memory
    with open(dict_file, 'rb') as f:
        dictionary = pickle.load(f)

        # add constants into Search
        search = Search(dictionary, postings_file)

    # load full list of doc ids from index stage
    with open(DOCIDS_FILENAME, 'rb') as f:
        search.docIDs = pickle.load(f)

    # load Length[N] (map of document: vector length of document)
    with open(DOC_LEN_FILENAME, 'rb') as f:
        search.length = pickle.load(f)

    # output file for writing
    r = open(results_file, 'w')

    with open(queries_file, 'r') as f:
        # read each query
        for line in f:
            # split line by whitespace
            terms = line.split()
            tokens = []

            # apply stemming as documents
            for term in terms:
                term = term.lower()
                stemmer = PorterStemmer()                           # apply stemming
                tokens.append(stemmer.stem(term))

            results = []
            # try:
            results = cosine_score(tokens, search)
            # except KeyError as err:
            #     # invalid query
            #     r.write(f'\n')
            #     continue

            # format output postings list
            resStr = ' '.join([str(x) for x in results])
            r.write(f'{resStr}\n')

# Finds title and content docIDs for two-way merge of two lists of postings lists
def find_title_and_content_docIDs_for_two_way_merge(lst1: list[Posting], lst2: list[Posting]):
    common_title_docIDs = []
    common_content_docIDs = []
    filtered_lists = filter_two_lists_by_common_docIDs(lst1, lst2)
    modified_lst1 = filtered_lists[0]
    modified_lst2 = filtered_lists[1]
    for item1, item2 in zip(modified_lst1, modified_lst2):
        merged_title_lst = merge_two_positional_lists(item1.title, item2.title)
        merged_content_lst = merge_two_positional_lists(item1.content, item2.content)
        if merged_title_lst != []:
            common_title_docIDs.append(item1.docID)
        if merged_content_lst != []:
            common_content_docIDs.append(item1.docID)
    return [common_title_docIDs, common_content_docIDs]

# Filters two lists by common docIDs and returns type [list[Posting], list[Posting]]
def filter_two_lists_by_common_docIDs(lst1: list[Posting], lst2: list[Posting]):
    modified_lst1 = []
    modified_lst2 = []
    for item1 in lst1:
        for item2 in lst2:
            if item1.docID == item2.docID:  # Assuming docID is type int 
                modified_lst1.append(item1)
                modified_lst2.append(item2)
    return [modified_lst1, modified_lst2]

# Merge two positional index lists and return a list of positional indices that have two consecutive terms
def merge_two_positional_lists(lst1, lst2):
    result = []
    for item1 in lst1:
        for item2 in lst2:
            if item2 == item1 + 1:      # If the positional index in lst2 is exactly one after a positional index 
                result.append(item2)    # in lst1, then add the second positional index to the result list
    return result

# Finds title and content docIDs for three-way merge of two lists of postings lists
def find_title_and_content_docIDs_for_three_way_merge(lst1: list[Posting], lst2: list[Posting], lst3: list[Posting]):
    common_title_docIDs = []
    common_content_docIDs = []
    filtered_lists = filter_three_lists_by_common_docIDs(lst1, lst2, lst3)
    modified_lst1 = filtered_lists[0]
    modified_lst2 = filtered_lists[1]
    modified_lst3 = filtered_lists[2]
    for item1, item2, item3 in zip(modified_lst1, modified_lst2, modified_lst3):
        merged_title_lst = merge_three_positional_lists(item1.title, item2.title, item3.title)
        merged_content_lst = merge_three_positional_lists(item1.content, item2.content, item3.content)
        if merged_title_lst != []:
            common_title_docIDs.append(item1.docID)
        if merged_content_lst != []:
            common_content_docIDs.append(item1.docID)
    return [common_title_docIDs, common_content_docIDs]

# Filters three lists by common docIDs and returns type [list[Posting], list[Posting], list[Posting]]
def filter_three_lists_by_common_docIDs(lst1: list[Posting], lst2: list[Posting], lst3: list[Posting]):
    modified_lst1 = []
    modified_lst2 = []
    modified_lst3 = []
    for item1 in lst1:
        for item2 in lst2:
            for item3 in lst3:
                if item1.docID == item2.docID and item2.docID == item3.docID:  # Assuming docID is type int 
                    modified_lst1.append(item1)
                    modified_lst2.append(item2)
                    modified_lst3.append(item3)
    return [modified_lst1, modified_lst2, modified_lst3]

# Merge three positional index lists and return a list of positional indices that have three consecutive terms
def merge_three_positional_lists(lst1, lst2, lst3):
    result1 = merge_two_positional_lists(lst1, lst2)
    result2 = merge_two_positional_lists(result1, lst3)
    return result2

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None:
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
