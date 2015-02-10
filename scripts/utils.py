# coding: utf-8
from pymorphy2 import MorphAnalyzer
from pymorphy2.tokenizers import simple_word_tokenize


def read_lemmas(fileobj):
    # здесь на каждой строчке по предложению (токенизованному)
    m = MorphAnalyzer()
    for line in fileobj:
        yield [m.parse(t)[0].normal_form for t in line.decode('utf-8').split()[1:]]


def read_text_lemmas(fileobj):
    m = MorphAnalyzer()
    for line in fileobj:
        yield ' '.join((m.parse(t)[0].normal_form for t in simple_word_tokenize(line.decode('utf-8'))))


def read_corpus(fileobj, m=None):
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
        s.append(Token(line, m))


class Token():
    def __init__(self, line, m=None):
        if not m:
            if len(line) < 2:
                self.text = ''
                self.lemmas = ['']
            else:
                self.text = line[1]
                self.interp = line[2:]
                self.lemmas = [i.split()[1] for i in self.interp]
        else:
            try:
                self.text = line[1]
                self.lemmas = [p.normal_form for p in m.parse(self.text)]
            except:
                self.text = ''
                self.lemmas = ['']

    def add_interp(self):
        pass


class Sentence(list):
    def __init__(self):
        pass

if __name__ == '__main__':
    import sys
    for s in read_text_lemmas(sys.stdin):
#        print ' '.join((t.text for t in s)).encode('utf-8')
        print s.encode('utf-8')
