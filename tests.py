import unittest
import os.path
import pickle
import argparse
import sys

from pprint  import pprint
from copycat import Copycat

# TODO: update test cases to use entropy

# CHI2 values for n degrees freedom
_chiSquared_table = {
        1:3.841,
        2:5.991,
        3:7.815,
        4:9.488,
        5:11.071,
        6:12.592,
        7:14.067,
        8:15.507,
        9:16.919,
        10:18.307
        }

class ChiSquaredException(Exception):
    pass

def chi_squared(actual, expected):
    answerKeys = set(list(actual.keys()) + list(expected.keys()))
    degreesFreedom = len(answerKeys)
    chiSquared = 0

    get_count = lambda k, d : d[k]['count'] if k in d else 0

    for k in answerKeys:
        E = get_count(k, expected)
        O = get_count(k, actual)
        if E == 0:
            print('Warning! Expected 0 counts of {}, but got {}'.format(k, O))
        else:
            chiSquared += (O - E) ** 2 / E

    if chiSquared >= _chiSquared_table[degreesFreedom]:
        raise ChiSquaredException('Significant difference between expected and actual answer distributions: \n' +
            'Chi2 value: {} with {} degrees of freedom'.format(chiSquared, degreesFreedom))

class AnswerDistribution:
    def __init__(self, initial, modified, target, iterations, distribution):
        self.initial  = initial
        self.modified = modified
        self.target   = target
        self.iterations   = iterations
        self.distribution = distribution

    def test(self):
        print('expected:')
        pprint(self.distribution)
        actual = Copycat().run(self.initial,
                self.modified,
                self.target,
                self.iterations)
        print('actual:')
        pprint(actual)
        chi_squared(actual, self.distribution)

    def generate(self):
        self.distribution = Copycat().run(self.initial,
                self.modified,
                self.target,
                self.iterations)

def generate(self):
    print('Generating distributions for new file')
    iterations = 30
    distributions = [
            AnswerDistribution('abc', 'abd', 'efg',    iterations, None),
            AnswerDistribution('abc', 'abd', 'ijk',    iterations, None),
            AnswerDistribution('abc', 'abd', 'xyz',    iterations, None),
            AnswerDistribution('abc', 'abd', 'ijkk',   iterations, None),
            AnswerDistribution('abc', 'abd', 'mrrjjj', iterations, None)]

    for distribution in distributions:
        distribution.generate()

    with open(TestCopycat.Filename, 'wb') as outfile:
        pickle.dump(distributions, outfile)
    return distributions
        
class TestCopycat(unittest.TestCase):

    Filename = None

    def setUp(self):
        self.longMessage = True  # new in Python 2.7

    def test(self):
        print(TestCopycat.Filename)
        try:
            with open(TestCopycat.Filename, 'rb') as infile:
                distributions = pickle.load(infile)
        except Exception as e:
            print('Generating due to error:')
            print(e)
            distributions = generate()

        for distribution in distributions:
            distribution.test()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('filename', default='.distributions', nargs='?')
    parser.add_argument('unittest_args', default=[], nargs='?')

    args = parser.parse_args()
    # TODO: Go do something with args.input and args.filename

    if args.generate:
        generate()

    TestCopycat.Filename = args.filename

    # Now set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
    sys.argv[1:] = args.unittest_args
    unittest.main()
