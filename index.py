#!/usr/bin/python3
import nltk
import sys
import getopt
import os
import string
from nltk.stem.porter import *
import math

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    files = sorted(os.listdir(in_dir), key=int) # grab all filenames in in_directory in sorted order
    term_and_postings_dictionary = {}
    document_lengths_file = open('document_lengths.txt', 'a')
    term_docID_pairs_lst = []
    document_lengths_dict = {}

    for filename in files[:]: # grab all filenames in in_directory
        with open(os.path.join(in_dir, filename), 'r') as f: # open each file
            content = (f.read()).lower() # apply case-folding
            content = content.translate(str.maketrans('', '', string.punctuation)) # remove punctuation
            words = nltk.tokenize.word_tokenize(content) # tokenize into words

            stemmer = PorterStemmer()
            words = [stemmer.stem(word) for word in words] # apply stemming

            term_frequency = {}
            doc_length = 0

            # Calculate term frequency to be used in document length calculation
            for word in words:
                term_frequency[word] = term_frequency.get(word, 0) + 1

            for word, freq in term_frequency.items():
                doc_length += (1 + math.log(freq, 10))**2
                term_docID_pairs_lst.append((word, int(filename), freq))
            
            # Update document lengths dictionary with calculated document lengths
            document_lengths_dict.update({filename: math.sqrt(doc_length)})

    # Write document lengths dictionary into external document_lengths.txt file
    document_lengths_file.write(str(document_lengths_dict))
    term_docID_pairs_lst = list(dict.fromkeys(term_docID_pairs_lst)) # remove duplicates from list of term-docID pairs
    sorted_lst = sorted(term_docID_pairs_lst)

    # Transfer items from the term-docID pairs list to a python dictionary with terms and postings
    for (term, docID, term_freq) in sorted_lst:
        if term not in term_and_postings_dictionary:
            term_and_postings_dictionary[term] = [(docID, term_freq)]
        else:
            term_and_postings_dictionary[term].append((docID, term_freq))

    # Populate file parameters for the dictionary and postings with the term_and_postings_dictionary
    sorted_dict = dict(sorted(term_and_postings_dictionary.items()))
    with open(out_dict, 'a') as f1:
        with open(out_postings, 'a') as f2:
            dictionary = {}
            for term, postings in sorted_dict.items():
                dictionary.update({term: (f2.tell(), len(postings))})
                f2.write(str(postings))
            f1.write(str(dictionary))

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
