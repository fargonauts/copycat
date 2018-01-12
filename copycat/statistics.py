from collections import defaultdict
from pprint      import pprint
from math        import log

# comparison values for n degrees freedom
# These values are useable for both the chi^2 and G tests

_ptable = {
        1:3.841,
        2:5.991,
        3:7.815,
        4:9.488,
        5:11.071,
        6:12.592,
        7:14.067,
        8:15.507,
        9:16.919,
        10:18.307,
        11:19.7,
        12:21,
        13:22.4,
        14:23.7,
        15:25,
        16:26.3
        }

def g_value(actual, expected):
    # G = 2 * sum(Oi * ln(Oi/Ei))
    answerKeys = set(list(actual.keys()) + list(expected.keys()))
    degreesFreedom = len(answerKeys)
    G = 0

    get_count = lambda k, d : d[k]['count'] if k in d else 0

    for k in answerKeys:
        E = get_count(k, expected)
        O = get_count(k, actual)
        if E == 0:
            print('    Warning! Expected 0 counts of {}, but got {}'.format(k, O))
        elif O == 0:
            print('    Warning! O = {}'.format(O))
        else:
            G += O * log(O/E)
    G *= 2
    return degreesFreedom, G

def chi_value(actual, expected):
    answerKeys = set(list(actual.keys()) + list(expected.keys()))
    degreesFreedom = len(answerKeys)
    chiSquared = 0

    get_count = lambda k, d : d[k]['count'] if k in d else 0

    for k in answerKeys:
        E = get_count(k, expected)
        O = get_count(k, actual)
        if E == 0:
            print('    Warning! Expected 0 counts of {}, but got {}'.format(k, O))
        else:
            chiSquared += (O - E) ** 2 / E
    return degreesFreedom, chiSquared

def dist_test(actual, expected, calculation):
    df, p = calculation(actual, expected)
    if df not in _ptable:
        raise Exception('{} degrees of freedom does not have a corresponding chi squared value.' + \
                        ' Please look up the value and add it to the table in copycat/statistics.py'.format(df))
    return (p < _ptable[df])

def cross_formula_table(actualDict, expectedDict, calculation):
    data = dict()
    for ka, actual in actualDict.items():
        for ke, expected in expectedDict.items():
            data[(ka, ke)] = dist_test(actual, expected, calculation)
    return data

def cross_table(problemSets, calculation=g_value):
    table = defaultdict(dict)
    for i, (a, problemSetA) in enumerate(problemSets):
        for b, problemSetB in problemSets[i + 1:]:
            for problemA in problemSetA:
                for problemB in problemSetB:
                    if (problemA.initial  == problemB.initial and
                        problemA.modified == problemB.modified and
                        problemA.target   == problemB.target):
                        answersA = problemA.distributions
                        answersB = problemB.distributions
                        table[(problemA.initial,
                               problemA.modified,
                               problemA.target)][(a, b)] = (
                                       cross_formula_table(
                                       answersA, answersB, calculation))
    return table

def iso_chi_squared(actualDict, expectedDict):
    for key in expectedDict.keys():
        assert key in actualDict, 'The key {} was not tested'.format(key)
        actual   = actualDict[key]
        expected = expectedDict[key]
        if not dist_test(actual, expected, g_value):
            raise Exception('Value of G higher than expected')

