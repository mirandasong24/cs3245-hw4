class TermIdMap:
    """
    Two-way map of term <-> Id
    """

    def __init__(self):
        self.termToId = {}
        self.idToTerm = {}
        self.termIdUniqueNum = 0

    # Add term to mapping
    # returns `termID`
    def add(self, term):
        if term not in self.termToId:
            self.termToId[term] = self.termIdUniqueNum
            self.idToTerm[self.termIdUniqueNum] = term
            self.termIdUniqueNum += 1
        return self.termToId[term]

    # returns term with given Id
    def getID(self, term):
        return self.termToId[term]

    # returns Id given term
    def getTerm(self, ID):
        return self.idToTerm[ID]
