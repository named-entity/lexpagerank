# coding: utf-8


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
