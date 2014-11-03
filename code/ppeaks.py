__author__ = 'mariosky'

import random
import operator
from itertools import imap


def get_peaks(number, bits, seed = None):
    if seed:
        random.seed(seed)
    return [[random.randint(0,1) for _ in range(bits)] for _ in range(number)]


def p_peaks(individual , peaks):
    return max([len(individual) - hamming_distance(individual,peak) for peak in peaks ]) * 1.0/len(individual)


def hamming_distance(str1, str2):
    assert len(str1) == len(str2)
    ne = operator.ne
    return sum(imap(ne, str1, str2))