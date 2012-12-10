"""Run the copycat program"""


import sys

import copycat


def main(program, args):
    """Run the program"""
    try:
        initial, modified, target = args
        copycat.run(initial, modified, target)
        return 0
    except ValueError:
        print >> sys.stderr, 'Usage: %s initial modified target' % program
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[0], sys.argv[1:]))
