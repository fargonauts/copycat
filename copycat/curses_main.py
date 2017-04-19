import curses
import logging
import sys

from copycat import Copycat
from curses_reporter import CursesReporter


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s', filename='./copycat.log', filemode='w')

    try:
        args = sys.argv[1:]
        initial, modified, target = args
    except ValueError:
        print >>sys.stderr, 'Usage: %s initial modified target [iterations]' % sys.argv[0]
        sys.exit(1)

    try:
        window = curses.initscr()
        copycat = Copycat(reporter=CursesReporter(window))
        copycat.run_forever(initial, modified, target)
    except KeyboardInterrupt:
        pass
    finally:
        curses.endwin()
