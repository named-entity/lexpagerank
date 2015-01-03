# -*- coding: utf-8 -*-
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import re
import sys
from networkx.algorithms.components.connected import number_connected_components
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
        # сюда будем для каждого общего слова писать номера предложений
        words = defaultdict(list)
        for i, s in enumerate(sentences):
            # лемматизация
            s = [t.lemmas[0] for t in s]
            if w in s:
                # добавили предложение в граф
                self.add_node(i, data=s)
                # сюда будем записывать общие с предыдущими предложениями слова
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
        return map(lambda x: (x[0], len(x[1])), filter(lambda x: len(x[1]) > 1, words.iteritems()))

# тут будем удалять ребра, на которых есть слова из заданного списка
    def cut(self, common_words):
        pass


def build_sentence_graph(w, sentences):
    # связываем предложения, в которых есть интересующее нас слово
    g = SGraph()
    words = g.load(w, sentences)
    return g, words


def rank(g):
    pr = nx.pagerank(g)
    return sorted(pr.iteritems(), key=lambda x: x[1])


def plot_graph(G):
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=dict(zip(G.edges(), (d['label'] for (u, v, d) in G.edges(data=True)))),
                                 label_pos=0.3)
    plt.show()


if __name__ == '__main__':
    matplotlib.rc('font', **{'sans-serif': 'Arial',
                           'family': 'sans-serif'})
    s = list(read_corpus(sys.stdin))
    print len(s)
    g, words = build_sentence_graph(u'замок', s)
    print number_connected_components(g)
    for w, c in sorted(words, key=lambda x: x[1], reverse=True)[:10]:
        for u, v in g.edges_iter():
            if g.has_edge(u, v, key=w):
                g.remove_edge(u, v, key=w)
    print number_connected_components(g)
    plot_graph(g)
