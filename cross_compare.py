#!/usr/bin/env python3
import sys
import pickle

from pprint import pprint
from collections import defaultdict

from copycat import Problem
from copycat.statistics import cross_table

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
    crossTable = cross_table(problemSets, probs=True)
    key_sorted_items = lambda d : sorted(d.items(), key=lambda t:t[0])

    tableItems = key_sorted_items(crossTable)
    assert len(tableItems) > 0, 'Empty table'

    headKey, headSubDict = tableItems[0]
    # Create table and add headers
    table = [['source', 'compare', 'source formula', 'compare formula']]
    for key, _ in tableItems:
        problem = '{}:{}::{}:_'.format(*key)
        table[-1].append(problem)

    # Arranged results in terms of copycat variants and formulas
    arranged = defaultdict(list)
    for key, subdict in tableItems:
        for subkey, subsubdict in key_sorted_items(subdict):
            for subsubkey, result in key_sorted_items(subsubdict):
                arranged[subkey + subsubkey].append((key, result))

    # Add test results to table
    for key, results in arranged.items():
        table.append(list(map(str, [*key])))
        for _, result in results:
            table[-1].append(str(result))

    with open('output/cross_compare.csv', 'w') as outfile:
        outfile.write('\n'.join(','.join(row) for row in table) + '\n')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
