#!/usr/bin/env python3
import sys
import pickle

from pprint import pprint

from copycat import Problem
from copycat.statistics import cross_chi_squared, cross_chi_squared_table

def compare_sets():
    pass

def main(args):
    branchProblemSets = dict()
    problemSets = []
    for filename in args:
        with open(filename, 'rb') as infile:
            pSet = pickle.load(infile)
            branchProblemSets[filename] = pSet
            problemSets.append((filename, pSet))
    pprint(problemSets)
    pprint(cross_chi_squared(problemSets))
    '''
    crossTable = cross_chi_squared_table(problemSets)
    key_sorted_items = lambda d : sorted(d.items(), key=lambda t:t[0])

    tableItems = key_sorted_items(crossTable)
    assert len(tableItems) > 0, 'Empty table'

    with open('output/cross_compare.csv', 'w') as outfile:
        headKey, headSubDict = tableItems[0]
        cells = ['problems x variants']
        for subkey, subsubdict in key_sorted_items(headSubDict):
            for subsubkey, result in key_sorted_items(subsubdict):
                cells.append('{} x {} for {} x {}'.format(*subkey, *subsubkey))
        outfile.write(','.join(cells) + '\n')

        for key, subdict in tableItems:
            cells = []
            problem = '{}:{}::{}:_'.format(*key)
            cells.append(problem)
            for subkey, subsubdict in key_sorted_items(subdict):
                for subsubkey, result in key_sorted_items(subsubdict):
                    cells.append(str(result))
            outfile.write(','.join(cells) + '\n')
    return 0
    '''

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
