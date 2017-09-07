import unittest

from .copycat import Copycat


def pnormaldist(p):
    table = {
        0.80: 1.2815,
        0.90: 1.6448,
        0.95: 1.9599,
        0.98: 2.3263,
        0.99: 2.5758,
        0.995: 2.8070,
        0.998: 3.0902,
        0.999: 3.2905,
        0.9999: 3.8905,
        0.99999: 4.4171,
        0.999999: 4.8916,
        0.9999999: 5.3267,
        0.99999999: 5.7307,
        0.999999999: 6.1094,
    }
    return max(v for k, v in table.items() if k <= p)


def lower_bound_on_probability(hits, attempts, confidence=0.95):
    if attempts == 0:
        return 0
    z = pnormaldist(confidence)
    zsqr = z * z
    phat = 1.0 * hits / attempts
    under_sqrt = (phat * (1 - phat) + zsqr / (4 * attempts)) / attempts
    denominator = (1 + zsqr / attempts)
    return (phat + zsqr / (2 * attempts) - z * (under_sqrt ** 0.5)) / denominator


def upper_bound_on_probability(hits, attempts, confidence=0.95):
    misses = attempts - hits
    return 1.0 - lower_bound_on_probability(misses, attempts, confidence)


class TestCopycat(unittest.TestCase):
    def setUp(self):
        self.longMessage = True  # new in Python 2.7

    def assertProbabilitiesLookRoughlyLike(self, actual, expected):
        actual_count = 0.0 + sum(d['count'] for d in list(actual.values()))
        expected_count = 0.0 + sum(d['count'] for d in list(expected.values()))
        self.assertGreater(actual_count, 1)
        self.assertGreater(expected_count, 1)
        for k in set(list(actual.keys()) + list(expected.keys())):
            if k not in expected:
                self.fail('Key %s was produced but not expected! %r != %r' % (k, actual, expected))
            expected_probability = expected[k]['count'] / expected_count
            if k in actual:
                actual_lo = lower_bound_on_probability(actual[k]['count'], actual_count)
                actual_hi = upper_bound_on_probability(actual[k]['count'], actual_count)
                if not (actual_lo <= expected_probability <= actual_hi):
                    print('Failed (%s <= %s <= %s)' % (actual_lo, expected_probability, actual_hi))
                    self.fail('Count ("obviousness" metric) seems way off! %r != %r' % (actual, expected))
                if abs(actual[k]['avgtemp'] - expected[k]['avgtemp']) >= 10.0 + (10.0 / actual[k]['count']):
                    print('Failed (%s - %s >= %s)' % (actual[k]['avgtemp'], expected[k]['avgtemp'], 10.0 + (10.0 / actual[k]['count'])))
                    self.fail('Temperature ("elegance" metric) seems way off! %r != %r' % (actual, expected))
            else:
                actual_hi = upper_bound_on_probability(0, actual_count)
                if not (0 <= expected_probability <= actual_hi):
                    self.fail('No instances of expected key %s were produced! %r != %r' % (k, actual, expected))

    def run_testcase(self, initial, modified, target, iterations, expected):
        actual = Copycat().run(initial, modified, target, iterations)
        self.assertEqual(sum(a['count'] for a in list(actual.values())), iterations)
        self.assertProbabilitiesLookRoughlyLike(actual, expected)

    def test_simple_cases(self):
        self.run_testcase('abc', 'abd', 'efg', 50, {
            'efd': {'count': 1, 'avgtemp': 16},
            'efh': {'count': 99, 'avgtemp': 19},
        })
        self.run_testcase('abc', 'abd', 'ijk', 50, {
            'ijd': {'count': 4, 'avgtemp': 24},
            'ijl': {'count': 96, 'avgtemp': 20},
        })

    def test_abc_xyz(self):
        self.run_testcase('abc', 'abd', 'xyz', 20, {
            'xyd': {'count': 100, 'avgtemp': 19},
        })

    def test_ambiguous_case(self):
        self.run_testcase('abc', 'abd', 'ijkk', 50, {
            'ijkkk': {'count': 7, 'avgtemp': 21},
            'ijll': {'count': 47, 'avgtemp': 28},
            'ijkl': {'count': 44, 'avgtemp': 32},
            'ijkd': {'count': 2, 'avgtemp': 65},
        })

    def test_mrrjjj(self):
        self.run_testcase('abc', 'abd', 'mrrjjj', 50, {
            'mrrjjjj': {'count': 4, 'avgtemp': 16},
            'mrrkkk': {'count': 31, 'avgtemp': 47},
            'mrrjjk': {'count': 64, 'avgtemp': 51},
            'mrrjkk': {'count': 1, 'avgtemp': 52},
            'mrrjjd': {'count': 1, 'avgtemp': 54},
        })

    def test_elongation(self):
        # This isn't remotely what a human would say.
        self.run_testcase('abc', 'aabbcc', 'milk', 50, {
            'milj': {'count': 85, 'avgtemp': 55},
            'mikj': {'count': 10, 'avgtemp': 56},
            'milk': {'count': 1, 'avgtemp': 56},
            'lilk': {'count': 1, 'avgtemp': 57},
            'milb': {'count': 3, 'avgtemp': 57},
        })

    def test_repairing_successor_sequence(self):
        # This isn't remotely what a human would say.
        self.run_testcase('aba', 'abc', 'xyx', 50, {
            'xc': {'count': 9, 'avgtemp': 57},
            'xyc': {'count': 82, 'avgtemp': 59},
            'cyx': {'count': 7, 'avgtemp': 68},
            'xyx': {'count': 2, 'avgtemp': 69},
        })

    def test_nonsense(self):
        self.run_testcase('cat', 'dog', 'cake', 10, {
            'cakg': {'count': 99, 'avgtemp': 70},
            'gake': {'count': 1, 'avgtemp': 59},
        })
        self.run_testcase('cat', 'dog', 'kitten', 10, {
            'kitteg': {'count': 96, 'avgtemp': 66},
            'kitten': {'count': 4, 'avgtemp': 68},
        })


if __name__ == '__main__':
    unittest.main()
