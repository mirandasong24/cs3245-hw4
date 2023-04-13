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
ID_TERM_MAP_FILENAME = 'id-term-map.txt'


class Search:
    # define common variables that are accessed in search
    def __init__(self, dictionary, filename_postings, doc_vectors=None, term_map=None, docIDs=None, length=None):
        self.dictionary = dictionary
        self.FILENAME_POSTINGS = filename_postings
        self.doc_vectors = doc_vectors
        self.term_map = term_map
        self.docIDs = docIDs
        self.length = length


def usage():
    print("usage: " +
          sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")
    
    
def fetch_postings(token, s):
    _, pos = s.dictionary[token]
    with open(s.FILENAME_POSTINGS, 'rb') as f:
        f.seek(pos)
            
        return pickle.load(f)
    
    
def boolean_retrieval(query, s):
    # returns list of docIDs that satisfy the boolean query
    tokens = shlex.split(query) # tokenize the query, i.e. get all phrases and words

    postings = []

    # obtain array of postings lists to merge
    for token in tokens:
        if token == "AND":
            continue

        individual_terms = token.split()
        all_in_dictionary = True

        for i in range(len(individual_terms)):
            term = individual_terms[i].lower()
            stemmer = PorterStemmer()
            term = stemmer.stem(term)
            individual_terms[i] = term

            if term not in s.dictionary:
                all_in_dictionary = False

        if all_in_dictionary:
            if len(individual_terms) == 2:
                postings.append(find_title_and_content_docIDs_for_two_way_merge(fetch_postings(individual_terms[0], s), fetch_postings(individual_terms[1], s))[1])
            elif len(individual_terms) == 3:
                postings.append(find_title_and_content_docIDs_for_three_way_merge(fetch_postings(individual_terms[0], s), fetch_postings(individual_terms[1], s), fetch_postings(individual_terms[2], s))[1])
            else:
                postings.append(fetch_postings(term, s))
    
    # merge all postings lists using "AND" operator
    while len(postings) > 1:
        postings_1 = postings.pop()
        postings_2 = postings.pop()
        postings.append(logical_and(postings_1, postings_2))

    return postings[0]


def logical_and(postings_one, postings_two):
    # returns the merged postings lists using the and operator

    result = []
    p1 = 0
    p2 = 0

    while p1 != len(postings_one) and p2 != len(postings_two):
        docID_1 = postings_one[p1]
        docID_2 = postings_two[p2]

        if type(docID_1) != int: # postings list is of the form [(docID, tf, (title_pos), (content_pos))]
            docID_1 = postings_one[p1][0]

        if type(docID_2) != int: # postings list is of the form [(docID, tf, (title_pos), (content_pos))]
            docID_2 = postings_two[p2][0]

        if docID_1 == docID_2:
            result.append(docID_1)
            p1 += 1
            p2 += 1
        elif docID_1 < docID_2:
            p1 += 1
        else:
            p2 += 1

    return result


# Finds title and content docIDs for two-way merge of two lists of postings lists
def find_title_and_content_docIDs_for_two_way_merge(lst1, lst2):
    common_title_docIDs = []
    common_content_docIDs = []
    filtered_lists = filter_two_lists_by_common_docIDs(lst1, lst2)
    modified_lst1 = filtered_lists[0]
    modified_lst2 = filtered_lists[1]
    for item1, item2 in zip(modified_lst1, modified_lst2):
        merged_title_lst = []
        merged_content_lst = []

        if item1[2] != None and item2[2] != None:
            merged_title_lst = merge_two_positional_lists(item1[2], item2[2])
        if item1[3] != None and item2[3] != None:
            merged_content_lst = merge_two_positional_lists(item1[3], item2[3])

        if merged_title_lst != []:
            common_title_docIDs.append(item1[0])
        if merged_content_lst != []:
            common_content_docIDs.append(item1[0])

    return [common_title_docIDs, common_content_docIDs]


# Filters two lists by common docIDs and returns type [list[Posting], list[Posting]]
def filter_two_lists_by_common_docIDs(lst1, lst2):
    modified_lst1 = []
    modified_lst2 = []
    for item1 in lst1:
        for item2 in lst2:
            if item1[0] == item2[0]:  # Assuming docID is type int 
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
def find_title_and_content_docIDs_for_three_way_merge(lst1, lst2, lst3):
    common_title_docIDs = []
    common_content_docIDs = []
    filtered_lists = filter_three_lists_by_common_docIDs(lst1, lst2, lst3)
    modified_lst1 = filtered_lists[0]
    modified_lst2 = filtered_lists[1]
    modified_lst3 = filtered_lists[2]
    for item1, item2, item3 in zip(modified_lst1, modified_lst2, modified_lst3):
        merged_title_lst = []
        merged_content_lst = []

        if item1[2] != None and item2[2] != None and item3[2] != None:
            merged_title_lst = merge_three_positional_lists(item1[2], item2[2], item3[2])
        if item1[3] != None and item2[3] != None and item3[3] != None:
            merged_content_lst = merge_three_positional_lists(item1[3], item2[3], item3[3])

        if merged_title_lst != []:
            common_title_docIDs.append(item1[0])
        if merged_content_lst != []:
            common_content_docIDs.append(item1[0])

    return [common_title_docIDs, common_content_docIDs]


# Filters three lists by common docIDs and returns type [list[Posting], list[Posting], list[Posting]]
def filter_three_lists_by_common_docIDs(lst1, lst2, lst3):
    modified_lst1 = []
    modified_lst2 = []
    modified_lst3 = []
    for item1 in lst1:
        for item2 in lst2:
            for item3 in lst3:
                if item1[0] == item2[0] and item2[0] == item3[0]:  # Assuming docID is type int 
                    modified_lst1.append(item1)
                    modified_lst2.append(item2)
                    modified_lst3.append(item3)
    return [modified_lst1, modified_lst2, modified_lst3]


# Merge three positional index lists and return a list of positional indices that have three consecutive terms
def merge_three_positional_lists(lst1, lst2, lst3):
    result1 = merge_two_positional_lists(lst1, lst2)
    result2 = merge_two_positional_lists(result1, lst3)
    return result2


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

        posting = fetch_postings(t,s)

        for doc, tf, title_pos, content_pos in posting:
            # check if term is in title, content, or both
            if title_pos == None:
                multiplier = 1
            elif content_pos == None:
                multiplier = 0.8
            else:
                multiplier = 1.3

            w_td = (1 + math.log(tf, 10)) * multiplier     # calculate log tf for document and multiply by zone factor
            scores[doc] += (w_td * query_vec[t])

    for d, score in scores.items():
        scores[d] = score/s.length[d]

    # sort by decreasing value (score) and then increasing key (docID)
    res = sorted(scores.items(), key=lambda x: (-x[1], x[0]))

    # for d in res:
    #     print(f'document {d} has score {scores[d]}')
    res = [docID for docID, score in res]
    return res


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """

    # load dictionary into memory2
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

    # load termID-term mapping (map of termID: term)
    with open(ID_TERM_MAP_FILENAME, 'rb') as f:
        search.term_map = pickle.load(f)


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
                for termID, weight in search.doc_vectors[int(doc.strip())].items():
                    term = search.term_map[termID]
                    centroid_vec.update({term: centroid_vec.get(term, 0) + weight}) 
            
            # divide centroid term weights by number of relevant docs
            for term, weight in centroid_vec.items():
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
