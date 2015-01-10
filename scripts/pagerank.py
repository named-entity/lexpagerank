# -*- coding: utf-8 -*-
from collections import Counter, defaultdict
from itertools import combinations
from random import sample

import matplotlib.pyplot as plt
import matplotlib
import networkx as nx
import re
import sys
from networkx.algorithms.components.connected import number_connected_components, connected_components
from networkx.classes.multigraph import MultiGraph
from utils import read_lemmas


class Scorer(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass


class CGraph(MultiGraph):
    def load(self, w, sentences):
        # сюда будем для каждого общего слова писать номера предложений
        wpairs = {}
        ss = {}
        f = open('%s.txt' % w, 'w')
        for i, s in enumerate(sentences):
            # лемматизация уже есть
            if w in s:
                print >> f, i, ' '.join(s).encode('utf-8')
                ss[i] = ' '.join(s).encode('utf-8')
                for w1, w2 in combinations(filter(lambda x: x != w and re.match(u'\w+', x, re.U), set(s)), 2):
                    if w1 == w2:
                        continue
                    try:
                        if i not in wpairs[(w1, w2)]:
                            wpairs[(w1, w2)].append(i)
                    except:
                        wpairs[(w1, w2)] = [i]
        for w1, w2 in wpairs.iterkeys():
            if len(set(wpairs[(w1, w2)])) > 1:
                self.add_edge(w1, w2)
        print len(self.nodes())
#                for j in set(wpairs[(w1, w2)]):
#                    print w1.encode('utf-8'), w2.encode('utf-8'), j
#                    self.add_edge(w1, w2, label=j, key=j, weight=1.0)
        f.close()
        return ss

# тут будем удалять вершины по списку
    def cut(self, common_words):
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
    g = CGraph()
    sentences = g.load(w, sentences)
    return g, sentences


def rank(g):
    pr = nx.pagerank(g)
    return sorted(pr.iteritems(), key=lambda x: x[1])


def plot_graph(G):
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos)
#    nx.draw_networkx_labels(G, pos)
#    nx.draw_networkx_edge_labels(G, pos, edge_labels=dict(zip(G.edges(), (d['label'] for (u, v, d) in G.edges(data=True)))),
#                                 label_pos=0.3)
    plt.show()


if __name__ == '__main__':
    matplotlib.rc('font', **{'sans-serif': 'Arial',
                           'family': 'sans-serif'})
    # в функции build_sentence_graph можно заменить CGraph на SGraph
    g, ss = build_sentence_graph(u'замок', read_lemmas(sys.stdin))
    print number_connected_components(g)
    # тут удаление рёбер для SGraph'ов
    """for w, c in sorted(words, key=lambda x: x[1], reverse=True)[:10]:
        for u, v in g.edges_iter():
            if g.has_edge(u, v, key=w):
                g.remove_edge(u, v, key=w)
    print number_connected_components(g)"""
    # удалим вершины степени 1 и остальные сложим в словарь со степенями. нужно в 1 строчку
    ndeg = {}
    for n in g.nodes()[:]:
        if g.degree(n) < 2:
            print >> sys.stderr, n
            g.remove_node(n)
        else:
            ndeg[n] = g.degree(n)
    print len(ndeg)
# рисуем распределение степеней
#    plt.plot(range(len(ndeg)), sorted(ndeg.values(), reverse=True))
#    plt.show()
    # удаление вершин для CGraph'ов
    for n, d in sorted(ndeg.iteritems(), key=lambda x: x[1], reverse=True)[:60]:
        g.remove_node(n)
        print n.encode('utf-8'), d, number_connected_components(g)
    sg = connected_components(g)
    # для десяти самых больших связных компонент выпишем предложения
#    for c in sorted(sg, key=len, reverse=True)[:10]:
#        cs = set((x[2]['label'] for x in g.edges(c, data=True)))
#        for s in cs:
#            print ss[s]
#        print