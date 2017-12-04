#!/usr/bin/env python3
import argparse
import logging

from copycat import Copycat, Reporter

class SimpleReporter(Reporter):
    def report_answer(self, answer):
        print('Answered %s (time %d, final temperature %.1f)' % (
            answer['answer'], answer['time'], answer['temp'],
        ))

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s', filename='./output/copycat.log', filemode='w')

    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=None, help='Provide a deterministic seed for the RNG.')
    options = parser.parse_args()

    copycat = Copycat(reporter=SimpleReporter(), rng_seed=options.seed, gui=True)
    copycat.runGUI()

if __name__ == '__main__':
    main()
