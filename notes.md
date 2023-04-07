### dictionary format
term-id: (pointer, df)


### posting list

'bill': 
[
    (doc-id, termID, [title: 1,2,171,200 (positional indices)], [content:300,450 (positional indices)]),
    (doc-id, termID, [title: 1,45,59,100 (positional indices)], [content:300,450 (positional indices)]),
    (doc-id, termID, [title: 1,2,171,599 (positional indices)], [content:300,450 (positional indices)])
]

'gates':
[
    (doc-id, termID, [title: 1,45,59,100 (positional indices)], [content:32,450 (positional indices)]),
    (doc-id, termID, [title: 1,45,59,100 (positional indices)], [content:4,450 (positional indices)]),
    (doc-id, termID, [title: 1,45,59,100 (positional indices)], [content:97,450 (positional indices)]),
    (doc-id, termID, [title: 1,45,59,100 (positional indices)], [content:300,450 (positional indices)])
]

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