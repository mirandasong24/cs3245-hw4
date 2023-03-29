### dictionary format
term-id: (pointer, df)


### posting list

(doc-id, term-freq, [title: 1,2,171,200 (positional indices)], [content:300,450 (positional indices)])


### zones/fields

title > content

ignore date_posted, court



### normal queries
see if in title/content, and calc tf-idf

###  phrasal queries
for a word in query w1, w2, w3


do some kind of merge (first 2 first, or 3-way merge)
title for w1 -> 0, 3, 30
title for w2 -> 1, 5, 7
title for w3 -> 2, 10

how to calcuate tf-idf for phrasal q?
phrasal queries in free text query??
