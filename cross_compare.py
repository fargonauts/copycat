#!/usr/bin/env python3
import sys
import pickle

from copycat import Problem
from copycat.statistics import cross_chi_squared

def compare_sets():
    pass

def main(args):
    branchProblemSets = dict()
    problemSets = []
    for filename in args:
        with open(filename, 'rb') as infile:
            pSet = pickle.load(infile)
            branchProblemSets[filename] = pSet
            problemSets.append(pSet)
    cross_chi_squared(problemSets)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
