#!/usr/bin/env python3
import argparse
import logging

from copycat import Copycat, Reporter, plot_answers

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

    plot_answers(answers)

if __name__ == '__main__':
    main()
