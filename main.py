#!/usr/bin/env python3
"""
Main Copycat program.

To run it, type at the terminal:

    > python main.py abc abd ppqqrr --interations 10

The script takes three to five arguments. The first two are a pair of strings
with some change, for example "abc" and "abd". The third is a string which the
script should try to change analogously. The fourth (which defaults to "1") is
a number of iterations. One can also specify a defined seed falue for the
random number generator.

The above might produce output such as

    ppqqss: 6 (avg time 869.0, avg temp 23.4)
    ppqqrs: 4 (avg time 439.0, avg temp 37.3)

The first number indicates how many times Copycat chose that string as its
answer; higher means "more obvious". The last number indicates the average
final temperature of the workspace; lower means "more elegant".
"""

import argparse
import logging

from copycat import Copycat, Reporter


class SimpleReporter(Reporter):
    def report_answer(self, answer):
        print('Answered %s (time %d, final temperature %.1f)' % (
            answer['answer'], answer['time'], answer['temp'],
        ))


def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s', filename='./copycat.log', filemode='w')

    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=None, help='Provide a deterministic seed for the RNG.')
    parser.add_argument('--iterations', type=int, default=1, help='Run the given case this many times.')
    parser.add_argument('initial', type=str, help='A...')
    parser.add_argument('modified', type=str, help='...is to B...')
    parser.add_argument('target', type=str, help='...as C is to... what?')
    options = parser.parse_args()

    copycat = Copycat(reporter=SimpleReporter(), rng_seed=options.seed)
    answers = copycat.run(options.initial, options.modified, options.target, options.iterations)

    for answer, d in sorted(iter(answers.items()), key=lambda kv: kv[1]['avgtemp']):
        print('%s: %d (avg time %.1f, avg temp %.1f)' % (answer, d['count'], d['avgtime'], d['avgtemp']))


if __name__ == '__main__':
    main()
