import codecs
from math import log
import json

import numpy as np

try:
    from .text_transform import get_progressbar
except (ModuleNotFoundError, ImportError):
    from text_transform import get_progressbar


class ProbabilisticModel:
    def __init__(self) -> None:
        self.corpus = []
        self.inverted_index = {}
        self.term_to_index = {}
        self.N = 0
        self.pi = []

    def __add_ii__(self, dj, term):
        try:
            self.inverted_index[term].add(dj)
        except KeyError:
            self.inverted_index[term] = set([dj])

    def computing_independent_values(self):
        self.pi = [0.5] * len(self.inverted_index)
        self.document_w_vector = np.zeros((self.N, len(self.inverted_index)))
        # self.document_w_vector = [
        #     [0] * len(self.inverted_index) for _ in range(self.N)]
        bar = get_progressbar(self.N, ' precomputing weights ')
        bar.start()

        for key in self.inverted_index:
            l = len(self.inverted_index[key])
            for i in self.inverted_index[key]:
                pi, ri = self.pi[self.term_to_index[key]], log(
                    self.N/l, self.N + 1)

                value = log(
                    (pi*(1-ri) + 1)/(ri*(1-pi) + 1))
                self.document_w_vector[i][self.term_to_index[key]] = value

            bar.update(i + 1)
        bar.finish()

    def fit(self, texts):
        self.N = len(texts)
        bar = get_progressbar(len(texts), ' precomputing all values ')
        bar.start()
        for i, hsh in enumerate(texts):
            for token in texts[hsh]:
                self.__add_ii__(i, token.lower())
            bar.update(i + 1)
            self.corpus.append(hsh)
        bar.finish()

        bar = get_progressbar(len(self.inverted_index),
                              ' numerate terms ')
        bar.start()
        for i, key in enumerate(self.inverted_index):
            self.term_to_index[key] = i
            bar.update(i + 1)
        bar.finish()

        self.computing_independent_values()

    def sorted_and_find(self, query, recover_len=10):
        query_term = set()
        for token in query:
            try:
                query_term.add(self.term_to_index[token.lower()])
            except:
                pass

        sim_result = []
        for i in range(self.N):
            sim_result.append(
                (i, abs(sum([self.document_w_vector[i][j] for j in query_term]))))
        sim_result.sort(key=lambda x: x[1], reverse=True)
        s = sum([v for _, v in sim_result])
        _len_ = recover_len if self.N > recover_len else self.N
        return [self.corpus[sim_result[i][0]] for i in range(_len_)]

    def dumps_path(self, path, key=""):
        return f'{path}/{key}/data_from_probabilistic_model.json'

    def save_model(self, path, k=""):
        for key in self.inverted_index:
            self.inverted_index[key] = tuple(self.inverted_index[key])

        with open(self.dumps_path(path, k), 'w+') as f:
            f.write(json.dumps({
                'ii': self.term_to_index,
                'iii': self.inverted_index,
                'corpus': self.corpus,
                'N': self.N
            }))

            f.close()

    def load_model(self, path, key=""):
        with open(self.dumps_path(path, key), 'r') as f:
            data = json.load(f)
            self.term_to_index = data['ii']
            self.inverted_index = data['iii']
            self.corpus = data['corpus']
            self.N = data['N']

# a = np.arange(10).reshape(2, 5)  # a 2 by 5 array
# b = a.tolist()  # nested lists with same data, indices
# file_path = "/path.json"  # your path variable
# json.dump(b, codecs.open(file_path, 'w', encoding='utf-8'),
#           separators=(',', ':'),
#           sort_keys=True,
#           indent=4)  # this saves the array in .json format
