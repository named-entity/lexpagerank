# -*- coding: utf-8 -*-
from collections import Counter, defaultdict
from itertools import combinations
import random

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import re
import sys
from networkx.algorithms.approximation import clustering_coefficient
from networkx.algorithms.components.connected import number_connected_components, connected_components
from networkx.algorithms.shortest_paths import shortest_path_length, shortest_path
from networkx.algorithms.shortest_paths import all_pairs_shortest_path_length
from networkx.classes.multigraph import MultiGraph
from networkx.classes import Graph
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
        words, uwords = 0, 0
        f = open('%s.lem' % w, 'w')
        for i, s in enumerate(sentences):
            # лемматизация уже есть
            if w in s:
                print >> f, i, ' '.join(s).encode('utf-8')
                s = filter(lambda x: x != w and re.match(u'\w+', x, re.U), s)
                words += len(s)
                uwords += len(set(s))
                ss[i] = ' '.join(s).encode('utf-8')
                for w1, w2 in combinations(set(s), 2):
                    if w1 == w2:
                        continue
                    try:
                        if i not in wpairs[(w1, w2)]:
                            wpairs[(w1, w2)].append(i)
                    except:
                        wpairs[(w1, w2)] = [i]
        print words, uwords
        for w1, w2 in wpairs.iterkeys():
            if len(set(wpairs[(w1, w2)])) > 0:
                self.add_edge(w1, w2, label=set(wpairs[(w1, w2)]))
#        print len(self.nodes())
#        for j, s in wpairs.iteritems():
#            print w1.encode('utf-8'), w2.encode('utf-8'), len(set(s))
#                    self.add_edge(w1, w2, label=j, key=j, weight=1.0)
        f.close()
        return ss

# тут будем удалять вершины по списку
    def cut(self, common_words):
        pass


class SGraph(Graph):
    def load(self, w, sentences):
        for i, s in enumerate(sentences):
            if w in s:
                self.add_node(i, words=s)
                for word in s:
                    for n in self.nodes(data=True):
                    # добавлять вес - количество таких слов
                        if word in n[1]['words']:
                            self.add_edge(i, n[0])
        return w


class SMultiGraph(MultiGraph):

# собираем из всех предложений только те, в которых есть заданное слово
# и строим граф
    def load(self, w, sentences, wsize=5, freq=10):
        # сюда будем для каждого общего слова писать номера предложений
        words = defaultdict(list)
        ss = {}
        f = open('%s.lem' % w, 'w')
        for i, s in enumerate(sentences):
            # лемматизация
#            s = [t.lemmas[0] for t in s]
            ss[i] = ' '.join(s).encode('utf-8')
            if i > 4000:
                break
            if w in s:
                print >> f, i, ' '.join(s).encode('utf-8')
                # добавили предложение в граф
                self.add_node(i)
                windex = s.index(w)
                lindex = 0
                if windex - wsize > 0:
                    lindex = windex - wsize
                if windex + wsize > len(s):
                    s = s[lindex:windex + wsize + 1]
                else:
                    s = s[lindex:]
                for word in set(s):
                    if word != w and re.match(u'\w+', word, re.U):
                        words[word].append(i)
                        for n in set(words[word]):
                            if not self.has_edge(i, n, key=word):
                                self.add_edge(i, n, key=word)
        self.words = map(lambda x: (x[0], len(x[1])), filter(lambda x: len(x[1]) > freq, words.iteritems()))
        return ss

# тут будем удалять ребра, на которых есть слова из заданного списка
    def cut(self, common_words):
        pass


def build_sentence_graph(w, sentences, type='s'):
    # связываем предложения, в которых есть интересующее нас слово
    if type == 'sm':
        g = SMultiGraph()
    if type == 's':
        g = SGraph()
    if type == 'c':
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
    word = u'замок'
    g, ss = build_sentence_graph(word, read_lemmas(sys.stdin), type='s')
    plot_graph(g)
    print number_connected_components(g)
    print clustering_coefficient.average_clustering(g)
    print rank(g)[:10]
    raise
    # n = random.choice(g.nodes())
    # prev = [n]
    # print n
    # for j in range(50):
    #     v = sorted(((i, g.number_of_edges(n, i)) for i in filter(lambda y: y not in prev, g.neighbors(n))), key=lambda x: x[1], reverse=True)[0]
    #     prev.append(v[0])
    #     n = v[0]
    # тут удаление рёбер для SGraph'ов
    for w, c in sorted(g.words, key=lambda x: x[1], reverse=True)[:150]:
        for u, v in g.edges_iter():
            if g.has_edge(u, v, key=w):
                g.remove_edge(u, v, key=w)
        comp = sorted([(x, len(x)) for x in connected_components(g)], key=lambda x: x[1])
        for s in comp[:-1]:
            print >> sys.stderr, w.encode('utf-8'), '\n'.join((ss[i] for i in s[0]))

    # longest_path = [0, (0, ())]
    # for n in g.nodes_iter():
    #     for t in shortest_path(g, source=n).iteritems():
    #         if len(t[1]) >= len(longest_path[1][1]):
    #             longest_path = [n, t]
    # print longest_path
    # paths = all_pairs_shortest_path_length(g)
    # longest_paths = [(i, sorted(j.iteritems(), key=lambda x: x[1], reverse=True)[0]) for i, j in paths.iteritems()]
    # s, t = sorted(longest_paths, key=lambda x: x[1][1], reverse=True)[0]
    # print s
    # print t[0]
    # print t[1]
    # удалим вершины степени 1 и остальные сложим в словарь со степенями. нужно в 1 строчку
    # ndeg = {}
    # for n in g.nodes()[:]:
    #     if g.degree(n) < 2:
#            g.remove_node(n)
#             pass
#         else:
#             ndeg[n] = g.degree(n)
#     print len(ndeg)
# рисуем распределение степеней
#    plt.plot(range(len(ndeg)), sorted(ndeg.values(), reverse=True))
#    plt.show()
    # удаление вершин для CGraph'ов
    # for n, d in sorted(ndeg.iteritems(), key=lambda x: x[1], reverse=True)[:60]:
    #     g.remove_node(n)
    #     print >> sys.stderr, n.encode('utf-8'), d, number_connected_components(g)
    # sg = connected_components(g)
    # для десяти самых больших связных компонент выпишем предложения
    # for c in sorted(sg, key=len, reverse=True)[:10]:
    #     #cs = (x[2]['label'] for x in g.edges(c, data=True))
    #     for s in g.nodes(c, data=True):
    #         print s
    #     print
