
def any(things):
    """Return True if any of the things are True.

    things should be iterable.

    If the things are empty, then we can't say any are True
    >>> any([])
    False

    If all the things are False, then we can't say any are True
    >>> any([False,False,False])
    False

    If all the things are equivalent to False, then we can't say any are True
    >>> any([0,[],''])
    False

    The type of the true thing should not matter
    >>> any([1,[],''])
    True
    >>> any([0,(2,),''])
    True
    >>> any([0,[],'foo'])
    True
    >>> any([0,[],True,''])
    True

    It should not matter where the True thing is
    >>> any((True,False,False,False,False,))
    True
    >>> any((False,False,True,False,False,))
    True
    >>> any((False,False,False,False,True,))
    True

    The size of the sequence should not matter
    >>> True == any((True,)) == any((True,True,)) == any((True,True,True,True,))
    True

    Any string is True
    >>> any('foo')
    True

    Except an empty string
    >>> any('')
    False

    The function cannot be applied to ints
    >>> any(7)
    Traceback (most recent call last):
        ...
    TypeError: iteration over non-sequence
    """
    for thing in things:
        if thing:
            return True
    return False

def all(things):
    """Return True if all of the things are True.

    things should be iterable.

    If the things are empty, then we can't say all are True
    >>> all([])
    False

    If all the things are False, then we can't say all are True
    >>> all([False,False,False])
    False

    If all the things are equivalent to False, then we can't say all are True
    >>> all([0,[],''])
    False

    The type of the false thing should not matter
    >>> all([0,True,True,])
    False
    >>> all([True,(),True,])
    False
    >>> all([True,True,'',])
    False

    Position of the false thing should not matter
    >>> all((False,True,True,))
    False
    >>> all((True,False,True,))
    False
    >>> all((True,True,False,))
    False

    any string is True
    >>> all('foo')
    True

    Except an empty string
    >>> all('')
    False

    The function cannot be applied to ints
    >>> all(7)
    Traceback (most recent call last):
        ...
    TypeError: iteration over non-sequence
    """
    for thing in things:
        if not thing:
            return False
    return len(things) > 0

import logging

seed = 999.0
count = 0
testably_random = True
def random():
    global testably_random
    if testably_random:
        from random import random
        return random()
    global seed
    global count
    seed += 1.0
    count += 1
    if seed > 1999:
        seed = 0.0
    logging.info("count: %d" % count)
    #if seed == 998:
    #   sys.exit(1)
    return seed / 2000.0

def choice(aList):
    i = int(random() * len(aList))
    return aList[i]

if __name__ == '__main__':
    import doctest
    doctest.testmod()

