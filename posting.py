# each posting contains a number (docID) and an optional skip pointer
class Posting:
    def __init__(self, docID, tf=None, positions=[]):
        self.docID = docID
        self.tf = tf
        self.positions = positions

    def __repr__(self):
        return f'({self.docID, self.tf, self.positions})'

    # def __lt__(self, other):
    #     return self.num < other.num

    # def __le__(self, other):
    #     return self.num <= other.num

    # def __repr__(self):
    #     if self.skip:
    #         return f'{self.num} (s={self.skip})'
    #     else:
    #         return f'{self.num}'

    # def __eq__(self, other):
    #     return self.num == other.num

    # def compare(ele1, ele2):
    #     return int(ele1.num) - int(ele2.num)
