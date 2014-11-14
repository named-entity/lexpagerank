# coding: utf-8
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
import sys
from networkx.classes.graph import Graph
from utils import Token, Sentence


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


def build_sentence_graph(word, sentences):
    # связываем предложения, в которых есть интересующее нас слово
    c = Counter()
    g = Graph()
    for i, s in enumerate(sentences):
        ts = [t.text for t in s]
        g.add_node(i, words=ts)
        for word in ts:
            for n in g.nodes(data=True):
            # добавлять вес - количество таких слов
                if word in n[1]['words']:
                    g.add_edge(i, n[0])
    return g


def build_graph(sentences):
    # связываем слова, которые встречаются в одном предложении
    c = Counter()
    g = Graph()
    for s in sentences:
        for t in s:
            for t1 in s:
                c[(t, t1)] += 1.0
    for s in sentences:
        ts = [t.text for t in s]
        g.add_nodes_from(ts)
        for t in s:
            for t1 in s:
                g.add_edge(t.text, t1.text, weight=round(c[(t, t1)] / len(c), 4))
    return g


def rank(g):
    pr = nx.pagerank(g)
    return pr


if __name__ == '__main__':
    s = list(read_corpus(sys.stdin))
    g = build_sentence_graph(u'лицо', s)
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos)
    nx.draw_networkx_edges(g, pos)
#    nx.draw_networkx_labels(g, pos)
#    nx.draw_networkx_edge_labels(g, pos)
    plt.show()
#    print rank(g)
