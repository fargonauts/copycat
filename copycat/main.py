"""Run the copycat program"""

import logging
import sys

import copycat


def main(program, args):
    """Run the program"""
    logging.basicConfig(level=logging.WARN, format='%(message)s',
                        filename='./copycat.log', filemode='w')

    try:
        if len(args) == 4:
            initial, modified, target = args[:-1]
            iterations = int(args[-1])
        else:
            initial, modified, target = args
            iterations = 1
        answers = copycat.run(initial, modified, target, iterations)
        for answer, d in sorted(answers.iteritems(), key=lambda kv: kv[1]['avgtemp']):
            print '%s: %d (avg time %.1f, avg temp %.1f)' % (answer, d['count'], d['avgtime'], d['avgtemp'])
        return 0
    except ValueError:
        print >> sys.stderr, 'Usage: %s initial modified target [iterations]' % program
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[0], sys.argv[1:]))
