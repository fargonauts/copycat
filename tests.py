import unittest
import os.path
import pickle
import argparse
import sys

from pprint  import pprint
from copycat import Problem
from copycat.statistics import iso_chi_squared

# TODO: update test cases to use entropy

def generate():
    print('Generating distributions for new file')
    iterations = 1000
    problems = [
            Problem('abc', 'abd', 'efg',    iterations),
            Problem('abc', 'abd', 'ijk',    iterations),
            Problem('abc', 'abd', 'xyz',    iterations),
            Problem('abc', 'abd', 'ijkk',   iterations),
            Problem('abc', 'abd', 'mrrjjj', iterations)]

    with open(TestCopycat.Filename, 'wb') as outfile:
        pickle.dump(problems, outfile)
    return problems

class TestCopycat(unittest.TestCase):
    Filename = None

    def setUp(self):
        self.longMessage = True  # new in Python 2.7

    def test(self):
        print('Testing copycat with input file: {}'.format(TestCopycat.Filename))
        try:
            with open(TestCopycat.Filename, 'rb') as infile:
                problems = pickle.load(infile)
        except Exception as e:
            print('Generating due to error:')
            print(e)
            problems = generate()

        for problem in problems:
            problem.test(iso_chi_squared)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('filename', default='.distributions', nargs='?')
    parser.add_argument('unittest_args', default=[], nargs='?')

    args = parser.parse_args()
    # TODO: Go do something with args.input and args.filename

    TestCopycat.Filename = args.filename

    if args.generate:
        generate()

    # Now set the sys.argv to the unittest_args (leaving sys.argv[0] alone)
    sys.argv[1:] = args.unittest_args
    unittest.main()
