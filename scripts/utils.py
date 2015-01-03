# coding: utf-8


def read_corpus(fileobj):
    s = []
    for line in fileobj:
        line = line.rstrip('\n').decode('utf-8').split('\t')
        if not line[0]:
            continue
        if line[0] == 'sent':
            yield s
            s = []
            continue
        if line[0] == '/sent':
            continue
        s.append(Token(line))


class Token():
    def __init__(self, line):
        self.text = line[1]
        self.interp = line[2:]
        self.lemmas = [i.split()[1] for i in self.interp]

    def add_interp(self):
        pass


class Sentence(list):
    def __init__(self):
        pass
