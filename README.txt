This is the README file for A0267818M-A0267993E's submission
Email(s): e1100338@u.nus.edu, e1100705@u.nus.edu

== Python Version ==

I'm (We're) using Python Version 3.9.13 for
this assignment.

== General Notes about this assignment ==

The index.py file contains the build_index function. This function first takes all the files from 
the training directory and processes each individual file. For each file, the terms in the file are 
tokenized and stemmed. Then, the term frequency is calculated in the file which is subsequently used in the 
document length calculation. At the end of each iterative loop, each document length is written into an 
external document_lengths.txt file. The words in the file are also inputted into a term-docID dictionary whose 
lifetime exists over the looping of all files in the training directory, and it maps each term to a list 
of docIDs in which it exists. To build the index, after looping through each file in the training directory,
the items from the term-docID pairs list are transferred into a python dictionary with terms and postings, 
and the dictionary and postings in the python dictionary term_and_postings_dictionary are populated 
into the corresponding file parameters.

The search.py file contains firstly the run_search function. This function handles the overall logic 
such as processing each query in the query file one by one and writing the ranked results to the output 
file. It does so by following the pseudocode given in lecture for calculating cosine scores. The query_term_vector
function calculates the vector entry for a query term using the tf.idf method. The doc_term_vector function
calculates the vector entry for a document term using the tf method. The main run_search function calls 
these two functions, multiplies the outputs together, and updates the scores for the docmuments accordingly.
We then normalize the vector entries by dividing by the document lengths found in the document_lengths file.
Finally, we sort the resulting scores by decreasing scores and increasing docID (in the case where multiple 
documents receive the same score) and write the 10 docIDs with the highest scores to the output file.

== Files included with this submission ==

README.txt - contains information about the submission
index.py - contains the logic for indexing
search.py - contains the logic for searching the index and ranking document similarity
dictionary.txt - contains the dictionary that includes each term, pointer to postings list (byte location), and doc frequency
postings.txt - contains the postings lists, one right after the other
document_lengths.txt - contains document lengths for each document

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0267818M-A0267993E, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0267818M-A0267993E, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

Stack Overflow - Looking up syntax for working with files/dictionaries in Python
Piazza - Posted questions online and used answers from prof, tutors, and peers