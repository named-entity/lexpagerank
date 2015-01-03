# -*- coding: utf-8 -*-
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import re
import sys
from networkx.classes.multigraph import MultiGraph
from utils import read_corpus


class Scorer(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass


class SGraph(MultiGraph):

# собираем из всех предложений только те, в которых есть заданное слово
# и строим граф
    def load(self, w, sentences):
        c = Counter()
        words = defaultdict(list)
        for i, s in enumerate(sentences):
            s = [t.lemmas[0] for t in s]
            if w in s:
                self.add_node(i, data=s)
                common_words = defaultdict(list)
                for word in s:
                    if word != w and re.match(u'\w+', word, re.U):
                        words[word].append(i)
                        for n in set(words[word]):
                            common_words[n].append(word)
                for n in common_words.keys():
                    if n != i:
                        for word in common_words[n]:
                            self.add_edge(i, n, label=word, key=word, weight=1.0)


def build_sentence_graph(w, sentences):
    # связываем предложения, в которых есть интересующее нас слово
    g = SGraph()
    g.load(w, sentences)
    return g


def rank(g):
    pr = nx.pagerank(g)
    return sorted(pr.iteritems(), key=lambda x: x[1])


if __name__ == '__main__':
    matplotlib.rc('font', **{'sans-serif': 'Arial',
                           'family': 'sans-serif'})
    s = list(read_corpus(sys.stdin))
    g = build_sentence_graph(u'замок', s)
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos)
    nx.draw_networkx_edges(g, pos)
    nx.draw_networkx_labels(g, pos)
    nx.draw_networkx_edge_labels(g, pos, edge_labels=dict(zip(g.edges(), (d['label'] for (u, v, d) in g.edges(data=True)))),
                                 label_pos=0.3)
    plt.show()