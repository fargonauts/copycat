import bisect
import math
import random


def accumulate(iterable):
    total = 0
    for v in iterable:
        total += v
        yield total


class Randomness(object):
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def coinFlip(self, p=0.5):
        return self.rng.random() < p

    def choice(self, seq):
        return self.rng.choice(seq)

    def weighted_choice(self, seq, weights):
        if not seq:
            # Many callers rely on this behavior.
            return None
        else:
            cum_weights = list(accumulate(weights))
            total = cum_weights[-1]
            return seq[bisect.bisect_left(cum_weights, self.rng.random() * total)]

    def weighted_greater_than(self, first, second):
        total = first + second
        if total == 0:
            return False
        return self.coinFlip(float(first) / total)

    def sqrtBlur(self, value):
        # This is exceedingly dumb, but it matches the Java code.
        root = math.sqrt(value)
        if self.coinFlip():
            return value + root
        return value - root
