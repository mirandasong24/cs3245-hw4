This is the README file for A0267818M-A0267993E-A0267998W's submission
Email(s): e1100338@u.nus.edu, e1100705@u.nus.edu, e1100710@u.nus.edu

== Python Version ==

We're using Python Version 3.8.10 for
this assignment.

== General Notes about this assignment ==

The main parts of the project are indexing, search, and query refinement.

1. Indexing
The main indexing algorithm follows from hw3, where we collect 
(term-id, doc-id) pairs to create a dictionary and postings file.
One major change is the format of the postings list. 
In order to store positional indexing for phrasal queries as well as 
encode zone information regarding `Title` and `Content`, each entry in the
postings list is a tuple of (docID, df, tuple of positional indices where term is in zone `Title`, 
tuple of positional indices where term is in zone `Content`).

Compression:
To shrink the size of the indexing output files, the postings list used 
tuples instead of lists and the dictionary used term-id as the key instead of the whole term.

2. Search
For search, both free text and boolean queries are handled the same way, specifically,
tokens are extracted from the query, and the TF×IDF score is calculated. Zone information in regards to Title 
and Content is handled here by using a multiplier on each w_td, where a term in both Title and Content is given
a higher multiplier than term in Title, followed by term in Content. 

Previously, boolean retrieval and positional indices was implemented for boolean queries
(see `boolean_retrieval()` in search.py). However, we found that this implementation did not
outperform treating boolean queries as a free text query.

3. Query Refinement (RF)
Two query refinement techniques, the Rocchio formula and manually compiled ontology (Wordnet) were tested
in our implementation to potentially improve the results of searching. Our final implementation uses Wordnet 
to perform query refinement instead of the Rocchio formula. More information can be found in our BONUS.docx file.

Work Allocation:
A0267998W was responsible for modifying the code in index.py to support the change in input format (csv) as
well as ensuring that the zone information (title and content) and term positions were captured in the new 
postings list format. They also worked on achieving a reasonable index size through index compression.

A0267993E worked on handling phrasal queries by using the information in the positional indices in the
postings list to merge and return a list of document IDs with the phrase in the title or content of
the document.

A0267818M was responsible for query refinement. They modified code from hw3 to support the new index
format, modified code from hw2 to handle boolean queries (this was later commented out as treating boolean
queries as free text instead of in a strict boolean sense performed better) and tested several query refinement 
techniques, namely using the Rocchio formula and manually created ontology (Wordnet). 


== Files included with this submission ==

README.txt - contains information about the submission
index.py - contains the logic for indexing
search.py - contains the logic for searching the index and processing queries
dictionary.txt - contains the dictionary that includes each term, pointer to postings list (byte location), and doc frequency
postings.txt - contains the postings lists, one right after the other
doc-len.txt - contains document lengths for each document
doc-vector.txt - contains document vector for each document, used for Relevant Feedback
id-term-map.txt - contains mapping of term id -> term.


== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0267818M-A0267993E-A0267998W, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0267818M-A0267993E-A0267998W, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

Stack Overflow - Looking up syntax for working with files/dictionaries in Python
nltk.org - Wordnet documentation
Piazza - Posted questions online and used answers from prof, tutors, and peers
