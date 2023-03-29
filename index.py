#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.porter import *
import pickle
from collections import defaultdict, OrderedDict
import heapq
import sys
import math
from functools import cmp_to_key
from posting import Posting
from termidmap import TermIdMap
import os
import shutil


# temp file to store full-list of docIds to be used in search
DOCIDS_FILENAME = 'doc-ids.txt'
DOC_LEN_FILENAME = 'doc-len.txt'


def usage():
    print("usage: " +
          sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def invert(block, termIdMap):
    """
    Sorts term-docID pairs, and collect all pairs with same termID into postings list
    Returns inverted index, an array of (termId, Postings list).
    """

    # collect into list of (termId, docId, termFreq)
    sorted_block = []
    for key, termFreq in block.items():
        sorted_block.append((*key, termFreq))

    # sort block by termID, then docID
    sorted_block.sort(key=lambda pair: (pair[0], pair[1]))

    # collect same termIDs into dict structure: <key=termID, value=postingsList>
    collected = defaultdict(list)
    for termID, docID, tf in sorted_block:
        collected[termID].append((int(docID), tf))

    return collected


def post_processing(termIdMap, block):

    res_dictionary = {}
    res_postings = []

    # Post Processing Steps
    for termID, posting in block.items():
        res_dictionary[termIdMap.getTerm(termID)] = posting

    od = OrderedDict(sorted(res_dictionary.items()))

    for termID, posting in od.items():
        od[termID] = len(posting)
        res_postings.append(posting)

    return od, res_postings


def calc_tf(dictionary, docIDs, docsTermToCount):
    # dictionary: <key=term, val=(df, ptr_to_postings)>
    print(f'Calculating document vectors: printing progress updates:')
    vectorDocLen = {}
    # loop through all documents
    for doc in docIDs:
        if doc % 200 == 0:
            print(f'calculating vector for document {doc}')
        # loop through vocab to create n-d vector
        vec = []
        termToCount = docsTermToCount[doc]
        for term in dictionary.keys():
            # 1 + log10(tf) if tf > 0
            if term in termToCount:
                vec.append(1 + math.log(termToCount[term], 10))
            # 0 otherwise
            else:
                vec.append(0)

        res = 0
        for i in vec:
            if i == 0:
                continue
            res += i**2

        vectorDocLen[doc] = math.sqrt(res)
        # # calculate length of vector
        # vec = [i for i in vec if i != 0]
        # vectorDocLen[doc] = math.sqrt(sum(w**2 for w in vec))

    # print(vectorDocLen)
    return vectorDocLen


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print("Indexing...")
    block = defaultdict(int)
    termIdMap = TermIdMap()
    docIDs = []                 # save full list of docIDs for NOT queries in search
    docsTermToCount = {}        # for each docID, saves the terms and counts of terms
    # to be used for computing document vector

    for docID in sorted(os.listdir(in_dir), key=int):
        docIDs.append(int(docID))
        with open(os.path.join(in_dir, docID), 'r') as f:  # open in readonly mode

            docID = int(docID)
            currDocTermToCount = defaultdict(int)
            # tokenization
            sents = nltk.sent_tokenize(f.read())         # sentence tokenizer
            sents = [s.lower() for s in sents]           # case folding

            tokens = [word_tokenize(t) for t in sents]  # word tokenizer
            # flatten array to words only
            tokens = [j for sub in tokens for j in sub]

            stemmer = PorterStemmer()                    # apply stemming
            tokens = [stemmer.stem(t) for t in tokens]

            for term in tokens:
                # add mapping of term -> termId in termIdMap
                termID = termIdMap.add(term)
                block[(termID, docID)] += 1
                currDocTermToCount[term] += 1

            docsTermToCount[docID] = currDocTermToCount

    invertedIndex = invert(block, termIdMap)

    dictionary, postings = post_processing(termIdMap, invertedIndex)

    indices = []  # store start location of each entry in pickel in dictionary

    print("Writing out postings and dictionary")
    # write out postings
    with open(out_postings, 'wb') as f:
        for entry in postings:
            indices.append(f.tell())
            pickle.dump(entry, f)

    # write out dictionary
    with open(out_dict, 'wb') as f:
        i = 0
        for key, value in dictionary.items():
            dictionary[key] = (value, indices[i])
            i += 1
        pickle.dump(dictionary, f)

    with open(DOCIDS_FILENAME, 'wb') as f:
        pickle.dump(docIDs, f)

    # calculate LENGTHS[N], which is length of each document vector
    # and write out to file for search step
    vectorDocLen = calc_tf(dictionary, docIDs, docsTermToCount)
    with open(DOC_LEN_FILENAME, 'wb') as f:
        pickle.dump(vectorDocLen, f)


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i':  # input directory
        input_directory = a
    elif o == '-d':  # dictionary file
        output_file_dictionary = a
    elif o == '-p':  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
