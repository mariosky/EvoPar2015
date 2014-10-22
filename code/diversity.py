
import itertools
import math
from collections import Counter


def hamming_distance(s1, s2):
    #Return the Hamming distance between equal-length sequences
    if len(s1) != len(s2):
        raise ValueError("Undefined for sequences of unequal length")
    return sum(ch1 != ch2 for ch1, ch2 in zip(s1, s2))


def diversity_hamming(pop):
    return sum([hamming_distance(ind1,ind2) for ind1,ind2 in itertools.combinations(pop,2)])


def entropy(s):
    p, lns = Counter(s), float(len(s))
    return -sum( count/lns * math.log(count/lns, 2) for count in p.values())

def diversity_entropy(pop):
    return sum([ entropy(individual) for individual in  pop])



