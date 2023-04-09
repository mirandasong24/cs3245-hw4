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
import shlex


DOC_LEN_FILENAME = 'doc-len.txt'
DOCIDS_FILENAME = 'doc-ids.txt'
DOC_VECTORS_FILENAME = 'doc-vector.txt'


class Search:
    # define common variables that are accessed in search
    def __init__(self, dictionary, filename_postings, doc_vectors=None, docIDs=None, length=None):
        self.dictionary = dictionary
        self.FILENAME_POSTINGS = filename_postings
        self.doc_vectors = doc_vectors
        self.docIDs = docIDs
        self.length = length


def usage():
    print("usage: " +
          sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")
    
    
def boolean_retrieval(query, s):
    # returns list of docIDs that satisfy the boolean query
    tokens = shlex.split(query) # tokenize the query, i.e. get all phrases and words

    postings = []

    # obtain array of postings lists to merge
    for token in tokens:
        if len(token.split()) > 1:
            postings.append(phrasal_query(token)) # get docIDs for phrasal query
        elif token != "AND":
            token = token.lower()
            stemmer = PorterStemmer()
            token = stemmer.stem(token)

            # fetch postings list for token
            _, pos = s.dictionary[token]
            with open(s.FILENAME_POSTINGS, 'rb') as f:
                f.seek(pos)
                postings.append(pickle.load(f))
        else:
            continue # if token is "AND", skip it
    
    # merge all postings lists using "AND" operator
    while len(postings) > 1:
        postings_1 = postings.pop()
        postings_2 = postings.pop()
        postings.append(logical_and(postings_1, postings_2))

    return postings


def phrasal_query(query, s): # takes as input the phrasal query and returns list of docIDs containing that phrase
    pass


def logical_and(postings_one, postings_two):
    # returns the merged postings lists using the and operator

    result = []
    p1 = 0
    p2 = 0

    while p1 != len(postings_one) and p2 != len(postings_two):
        docID_1 = postings_one[p1].docID
        docID_2 = postings_two[p2].docID

        if docID_1 == docID_2:
            result.append(docID_1)
            p1 += 1
            p2 += 1
        elif docID_1 < docID_2:
            p1 += 1
        else:
            p2 += 1

    return result


def get_w_tq(t, count, s):
    # calculate w(t,q)

    tf = count[t]                        # frequency of term in query
    log_tf = 1 + math.log(tf, 10)

    df, _ = s.dictionary[t]
    N = len(s.docIDs)
    idf = math.log(N/df, 10)

    w_tq = log_tf * idf
    return w_tq


def cosine_score(query_vec, s):
    scores = defaultdict(float)
    uniqueTokens = query_vec.keys()

    # loop through all query terms
    for t in uniqueTokens:
        if t not in s.dictionary:
            # if term not found, continue to next term
            continue

        # fetch postings list for t
        _, pos = s.dictionary[t]
        with open(s.FILENAME_POSTINGS, 'rb') as f:
            f.seek(pos)
            posting = pickle.load(f)

        # take care of zone weighting here (check if title_pos or zone_pos is empty)
            for doc, tf, title_pos, zone_pos in posting:
                w_td = 1 + math.log(tf, 10)     # calculate log tf for document
                scores[doc] += (w_td * query_vec[t])

    for d, score in scores.items():
        scores[d] = score/s.length[d]

    # sort by decreasing value (score) and then increasing key (docID)
    res = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
    res2 = [] # get all docIDs with scores > 0

    for docID, score in res:
        if score == 0:
            break
        else:
            res2.append(docID)

    # for d in res:
    #     print(f'document {d} has score {scores[d]}')
    return res2


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

    # load document vectors (map of document: document vector)
    with open(DOC_VECTORS_FILENAME, 'rb') as f:
        search.doc_vectors = pickle.load(f)


    # output file for writing
    r = open(results_file, 'w')

    with open(queries_file, 'r') as f:
        # read query
        query = f.readline()
        relevant_docs = f.readlines()
        results = []

        # check if query is boolean or free text
        if "AND" in query:
            results = boolean_retrieval(query, search)
        else:
            # compute centroid of relevant documents
            centroid_vec = {}

            for doc in relevant_docs:
                for term, weight in search.doc_vectors[int(doc.strip())].items():
                    centroid_vec.update({term: centroid_vec.get(term, 0) + weight}) 
            
            # divide centroid term weights by number of relevant docs
            for term, weight in centroid_vec:
                centroid_vec[term] = weight / len(relevant_docs)
        
            # compute initial query vector 
            query_vec = {}

            # split query by whitespace
            terms = query.split()
            tokens = []

            # apply stemming as documents
            for term in terms:
                term = term.lower()
                stemmer = PorterStemmer()                           # apply stemming
                tokens.append(stemmer.stem(term))
            
            count = collections.Counter(tokens) # get term frequency in query
            # try:
            
            for term in tokens:
                query_vec[term] = get_w_tq(term, count, search)

            # compute modified query based on rocchio formula
            modified_query_vec = {}

            for term in set().union(query_vec, centroid_vec): # union of terms in query and centroid vectors
                modified_query_vec[term] = (query_vec.get(term, 0) * 0.7) + (centroid_vec.get(term, 0) * 0.3)

            results = cosine_score(modified_query_vec, search)

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
