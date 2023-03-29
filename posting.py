# each posting contains a number (docID) and an optional skip pointer
class Posting:
    def __init__(self, num, termFreq=None, skip=None):
        self.num = num
        self.termFreq = termFreq
        self.skip = skip

    def __lt__(self, other):
        return self.num < other.num

    def __le__(self, other):
        return self.num <= other.num

    def __repr__(self):
        if self.skip:
            return f'{self.num} (s={self.skip})'
        else:
            return f'{self.num}'

    def __eq__(self, other):
        return self.num == other.num

    def compare(ele1, ele2):
        return int(ele1.num) - int(ele2.num)
