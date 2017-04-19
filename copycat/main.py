import logging
import sys

from copycat import Copycat, Reporter


class SimpleReporter(Reporter):
    def report_answer(self, answer):
        print 'Answered %s (time %d, final temperature %.1f)' % (
            answer['answer'], answer['time'], answer['temp'],
        )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s', filename='./copycat.log', filemode='w')

    try:
        args = sys.argv[1:]
        if len(args) == 4:
            initial, modified, target = args[:-1]
            iterations = int(args[-1])
        else:
            initial, modified, target = args
            iterations = 1
    except ValueError:
        print >>sys.stderr, 'Usage: %s initial modified target [iterations]' % sys.argv[0]
        sys.exit(1)

    copycat = Copycat(reporter=SimpleReporter())
    answers = copycat.run(initial, modified, target, iterations)

    for answer, d in sorted(answers.iteritems(), key=lambda kv: kv[1]['avgtemp']):
        print '%s: %d (avg time %.1f, avg temp %.1f)' % (answer, d['count'], d['avgtime'], d['avgtemp'])
