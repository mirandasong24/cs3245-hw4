#!/usr/bin/python3
import re
import nltk
import sys
import getopt
from nltk.stem.porter import *
import ast
import math
import operator
import string

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    f2 = open(results_file, "w")

    with open(dict_file) as f:
        dictionary = f.read() # load dictionary into memory
        dictionary = ast.literal_eval(dictionary) # parse the file into a python dictionary
    
    with open("document_lengths.txt") as f:
        doc_lengths = f.read() # load document lengths into memory
        doc_lengths = ast.literal_eval(doc_lengths) # parse the file into a python dictionary

    # open queries file and process each query
    with open(queries_file) as f1:
        lines = f1.readlines()

        for query in lines:
            scores = {}
            processed_query = query.translate(str.maketrans('', '', string.punctuation)) # remove punctuation

            # get list of docIDs sorted by cosine similarity and write the top 10 to the output file
            for term in processed_query.split():
                term_vector = query_term_vector(query, term, len(doc_lengths), dictionary)
                postings_list = get_postings_list(term, dict_file, postings_file)

                for pair in postings_list: # update only scores of docIDs in postings list, other doc scores will be unaffected
                    scores.update({pair[0]: scores.get(pair[0], 0) + (term_vector * doc_term_vector(pair))}) 

            # perform normalization
            for docID, score in scores.items():
                scores[docID] = score / doc_lengths[str(docID)]
            
            scores = list(sorted(scores.items(), key=lambda x: (x[1], -x[0]) , reverse=True)) # sort by decreasing score, increasing docID
            line = ""

            if len(scores) < 10: # write every docID to output file if less than 10 valid results
                for pair in scores:
                    line += str(pair[0]) + " "
            else:
                for i in range(10): # write top 10 results to output file if more than 10 valid results
                    line += str(scores[i][0]) + " "
            
            line.strip()
            line += "\n"

            f2.write(line)
            
    f2.close()
    
def get_postings_list(term, dict_file, postings_file):
    # returns list of docIDs
    postings = ""
    num = 0

    with open(dict_file) as f:
        dictionary = f.read() # load dictionary into memory
        dictionary = ast.literal_eval(dictionary) # parse the file into a python dictionary
        stemmer = PorterStemmer()
        term = stemmer.stem(term.lower()) # normalize the term to be consistent with the dictionary
    
    if term not in dictionary:
        return [] 

    byte_location = dictionary[term][0] # move to beginning of postings list of that term

    with open(postings_file) as f:
        f.seek(byte_location)
        char = f.read(1) # skip the "[" character
        char = f.read(1) # read first postings list char

        while char != "]":
            if char == "(":
                num += 1
            postings += char
            char = f.read(1)
    
    if num > 1:
        postings_list = list(ast.literal_eval(postings))
    else:
        postings_list = [tuple(ast.literal_eval(postings))] # need to use different logic to process postings lists with only one entry

    return postings_list

def query_term_vector(query, term, collection_size, dictionary):
    # returns weighted vector entry for term

    stemmer = PorterStemmer()
    processed_query = query.translate(str.maketrans('', '', string.punctuation))

    tf = 1 + math.log(processed_query.count(term), 10) # perform tf

    term = stemmer.stem(term.lower())

    # perform idf
    if term in dictionary:
        idf = math.log(collection_size / dictionary[term][1], 10)
    else:
        idf = 0
    
    return tf * idf

def doc_term_vector(docID_tf_pair):
    # returns weighted vector entry for term with that specific docID_tf pair
    term_frequency = docID_tf_pair[1]
    
    return 1 + math.log(term_frequency, 10)

dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
