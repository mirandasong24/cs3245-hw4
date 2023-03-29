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

    # hello

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
