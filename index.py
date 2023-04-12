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
import csv
from enum import Enum
from itertools import islice


# temp file to store full-list of docIds to be used in search
DOCIDS_FILENAME = 'doc-ids.txt'
DOC_LEN_FILENAME = 'doc-len.txt'
DOC_VECTORS_FILENAME = 'doc-vector.txt'
ID_TERM_MAP_FILENAME = 'id-term-map.txt'


class Zone(Enum):
    TITLE = 1
    CONTENT = 2


def usage():
    print("usage: " +
          sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


def invert(block, termIdMap):
    """
    Sorts term-docID pairs, and collect all pairs with same termID into postings list
    Returns inverted index, an array of (termId, Postings list).
    """
    # block = (termId, docID, title pos, content pos)
    # -1 if not a title, -1 if not a content

    # sort block by termID, then docID
    block.sort(key=lambda pair: (pair[0], pair[1]))

    # squash twice, first squash by positions
    collected = OrderedDict()
    for termId, docID, titlePos, contentPos in block:
        if (termId, docID) not in collected:
            collected[(termId, docID)] = defaultdict(list)

        if titlePos != -1:
            collected[(termId, docID)][Zone.TITLE].append(titlePos)
        elif contentPos != -1:
            collected[(termId, docID)][Zone.CONTENT].append(contentPos)

    # squash by term-id
    # collect same termIDs into dict structure: <key=termID, value=[docID, tf, [positions]]>
    res = defaultdict(list)
    for (termID, docID), positions in collected.items():
        df = len(positions[Zone.TITLE]) + len(positions[Zone.CONTENT])

        res[termID].append(
            (int(docID), df,
             tuple(positions[Zone.TITLE]) if positions[Zone.TITLE] else None,
             tuple(positions[Zone.CONTENT]) if positions[Zone.CONTENT] else None))

    return res


def post_processing(termIdMap, block):

    res_dictionary = {}
    res_postings = []

    # Post Processing Steps
    for termID, plist in block.items():
        res_dictionary[termIdMap.getTerm(termID)] = plist

    od = OrderedDict(sorted(res_dictionary.items()))

    for termID, plist in od.items():
        od[termID] = len(plist)
        res_postings.append(plist)

    return od, res_postings


def calc_tf(dictionary, docIDs, docsTermToCount, termIdMap):
    # dictionary: <key=term, val=(df, ptr_to_postings)>
    print(f'Calculating document vectors: printing progress updates:')
    vectorDocLen = {}
    docVec = {}                     # document vector for RF calc
    # loop through all documents
    for doc in docIDs:
        if doc % 200 == 0:
            print(f'calculating vector for document {doc}')
        # loop through vocab to create n-d vector
        vec = {}
        termToCount = docsTermToCount[doc]
        for term in dictionary.keys():
            # 1 + log10(tf) if tf > 0
            if term in termToCount:
                vec[termIdMap.getID(term)] = 1 + \
                    math.log(termToCount[term], 10)
            # 0 otherwise, don't add to vec

        res = 0
        for i in vec.values():
            res += i**2

        vectorDocLen[doc] = math.sqrt(res)
        docVec[doc] = vec

    # print(vectorDocLen)
    return (vectorDocLen, docVec)


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print("Indexing...")
    csv.field_size_limit(sys.maxsize)
    block = []
    termIdMap = TermIdMap()
    docIDs = []                 # save full list of docIDs for NOT queries in search
    docsTermToCount = {}        # for each docID, saves the terms and counts of terms
    # to be used for computing document vector

    doc = []
    # parse csv
    with open(in_dir) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        i = 0
        for row in csv_reader:
            if i > 10:            # DEBUG: change for however many documents
                break
            doc.append(row)
            i += 1
        print(f'Processed {i} lines.')

    print(doc[0])
    # assume is just name of file for now..

    for entry in doc:
        # "document_id","title","content","date_posted","court"
        docID, title, content, _, _ = entry
        zones = {Zone.TITLE: title, Zone.CONTENT: content}
        if not docID.isnumeric():
            continue
        docIDs.append(int(docID))
        docID = int(docID)

        for zone, info in zones.items():
            # if docID % 10 == 0:
            #     print(f'processing document {docID}')
            currDocTermToCount = defaultdict(int)
            # tokenization
            sents = nltk.sent_tokenize(info)         # sentence tokenizer
            sents = [s.lower() for s in sents]           # case folding

            tokens = [word_tokenize(t) for t in sents]  # word tokenizer
            # flatten array to words only
            tokens = [j for sub in tokens for j in sub]

            stemmer = PorterStemmer()                    # apply stemming
            tokens = [stemmer.stem(t) for t in tokens]

            pos = 0
            for term in tokens:
                # add mapping of term -> termId in termIdMap
                termID = termIdMap.add(term)

                if zone == Zone.TITLE:
                    block.append((termID, docID, pos, -1))
                elif zone == Zone.CONTENT:
                    block.append((termID, docID, -1, pos))

                currDocTermToCount[term] += 1
                pos += 1

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
    vectorDocLen, docVec = calc_tf(
        dictionary, docIDs, docsTermToCount, termIdMap)
    with open(DOC_LEN_FILENAME, 'wb') as f:
        pickle.dump(vectorDocLen, f)

    with open(DOC_VECTORS_FILENAME, 'wb') as f:
        pickle.dump(docVec, f)

    with open(ID_TERM_MAP_FILENAME, 'wb') as f:
        pickle.dump(termIdMap.idToTerm, f)

    # DEBUG: print postings list
    with open(out_dict, 'rb') as f:
        d = pickle.load(f)
        # print(f'loaded dictionary {d}')
        n_items = list(islice(d.items(), 10))
        print('')
        print(f'>>> Loaded dictionary sample for first 10 items{n_items}\n')
        with open(out_postings, 'rb') as f:
            print(">>> Printing first 10 loaded postings")
            i = 0
            for key, value in dictionary.items():
                if i == 10:
                    break
                f.seek(value[1])
                postings = pickle.load(f)
                seen_title = False

                print(f'term={key}, df={value[0]}, pointer={value[1]}')

                for p in postings:
                    print(p)
                print('')

                # DEBUG: print postings for title of 1st document
                # for p in postings:
                #     if p.title:
                #         seen_title = True

                # if seen_title:
                #     print(s)
                #     for p in postings:
                #         if p.docID == 246391:
                #             print(p)
                #     print('\n')
                i += 1
            # f.seek(d[1][1])
            # print(pickle.load(f))  # -> Item4

    # DEBUG: print document vectors list
    print('')
    with open(DOC_VECTORS_FILENAME, 'rb') as f:
        d = pickle.load(f)
        for k, v in d.items():
            items = list(islice(v.items(), 10))
            print(
                f'>>> Loaded doc-vector.txt sample for first 10 items in document 1: {items}')
            print('')
            break


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
