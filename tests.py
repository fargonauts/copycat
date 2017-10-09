import unittest
from pprint import pprint

from copycat import Copycat

# TODO: update test cases to use entropy

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

    SignificantPercent = 10

    def setUp(self):
        self.longMessage = True  # new in Python 2.7

    def assertProbabilitiesLookRoughlyLike(self, actual, expected, iterations):
        significantCount = iterations / TestCopycat.SignificantPercent # The number of times a value must show up to be significant

        actual_count = 0.0 + sum(d['count'] for d in list(actual.values()))
        expected_count = 0.0 + sum(d['count'] for d in list(expected.values()))
        self.assertGreater(actual_count, 1)
        self.assertGreater(expected_count, 1)

        for k in set(list(actual.keys()) + list(expected.keys())):
            if k not in expected:
                expected_probability = 0.05
            else:
                expected_probability = expected[k]['count'] / expected_count
            '''
            if k not in expected and actual[k]['count'] >= significantCount:
                self.fail('Key %s was produced but not expected! %r != %r' % (k, actual, expected))
                expected_probability = 
            expected_probability = expected[k]['count'] / expected_count
            '''
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
        print('expected:')
        pprint(expected)
        actual = Copycat().run(initial, modified, target, iterations)
        print('actual:')
        pprint(actual)
        self.assertEqual(sum(a['count'] for a in list(actual.values())), iterations)
        self.assertProbabilitiesLookRoughlyLike(actual, expected, iterations)

    '''
    def test_simple_cases(self):
        self.run_testcase('abc', 'abd', 'efg', 30, 
	    {'dfg': {'avgtemp': 72.37092377767368, 'avgtime': 475.0, 'count': 1},
	     'efd': {'avgtemp': 49.421147725239024, 'avgtime': 410.5, 'count': 2},
	     'efh': {'avgtemp': 19.381658717913258,
		     'avgtime': 757.1851851851852,
		     'count': 27}})
        self.run_testcase('abc', 'abd', 'ijk', 30, {
            'ijl': {'count': 30, 'avgtemp': 20},
        })
    '''

    def test_abc_xyz(self):
        self.run_testcase('abc', 'abd', 'xyz', 100, 
	    {'dyz': {'avgtemp': 26.143509984937367, 'avgtime': 9866.625, 'count': 8},
	     'wyz': {'avgtemp': 12.249539212574128,
		     'avgtime': 9520.666666666666,
		     'count': 18},
	     'xyd': {'avgtemp': 38.73402068486291, 'avgtime': 7439.225, 'count': 40},
	     'xyy': {'avgtemp': 24.614440709519627, 'avgtime': 3522.625, 'count': 8},
	     'xyz': {'avgtemp': 57.674822842028945, 'avgtime': 8315.2, 'count': 5},
	     'yyz': {'avgtemp': 26.874886217740315,
		     'avgtime': 8493.142857142857,
		     'count': 21}})

    def test_ambiguous_case(self):
        self.run_testcase('abc', 'abd', 'ijkk', 100, 
	    {'ijd': {'avgtemp': 55.6767488926397, 'avgtime': 948.0, 'count': 1},
	     'ijkd': {'avgtemp': 78.09357723857647, 'avgtime': 424.5, 'count': 2},
	     'ijkk': {'avgtemp': 68.54252699118226, 'avgtime': 905.5, 'count': 2},
	     'ijkkk': {'avgtemp': 21.75444235750483,
		       'avgtime': 2250.3333333333335,
		       'count': 3},
	     'ijkl': {'avgtemp': 38.079858245918466,
		      'avgtime': 1410.2391304347825,
		      'count': 46},
	     'ijll': {'avgtemp': 27.53845719945872,
		      'avgtime': 1711.8863636363637,
		      'count': 44},
	     'jjkk': {'avgtemp': 75.76606718990365, 'avgtime': 925.0, 'count': 2}})

    '''
    def test_mrrjjj(self):
        self.run_testcase('abc', 'abd', 'mrrjjj', 30, 
	    {'drrjjj': {'avgtemp': 47.3961, 'avgtime': 1538.0, 'count': 1},
	     'mrrjjd': {'avgtemp': 70.5363, 'avgtime': 681.0, 'count': 1},
	     'mrrjjjj': {'avgtemp': 19.1294, 'avgtime': 2075.0, 'count': 1},
	     'mrrjjk': {'avgtemp': 48.0952,
			'avgtime': 2203.5714,
			'count': 14},
	     'mrrkkk': {'avgtemp': 43.6931,
			'avgtime': 2251.4615,
			'count': 13}})
    '''

    '''
    Below are examples of improvements that could be made to copycat.

    def test_elongation(self):
        # This isn't remotely what a human would say.
        self.run_testcase('abc', 'aabbcc', 'milk', 30, 
	    {'lilk': {'avgtemp': 68.18128407669258,
		      'avgtime': 1200.6666666666667,
		      'count': 3},
	     'mikj': {'avgtemp': 57.96973195905564,
		      'avgtime': 1236.888888888889,
		      'count': 9},
	     'milb': {'avgtemp': 79.98413990245763, 'avgtime': 255.0, 'count': 1},
	     'milj': {'avgtemp': 64.95289549955349, 'avgtime': 1192.4, 'count': 15},
	     'milk': {'avgtemp': 66.11387816293755, 'avgtime': 1891.5, 'count': 2}})
    def test_repairing_successor_sequence(self):
        # This isn't remotely what a human would say.
        self.run_testcase('aba', 'abc', 'xyx', 30, 
	    {'cyx': {'avgtemp': 82.10555880340601, 'avgtime': 2637.0, 'count': 2},
	     'xc': {'avgtemp': 73.98845045179358, 'avgtime': 5459.5, 'count': 2},
	     'xyc': {'avgtemp': 77.1384941639991,
		     'avgtime': 4617.434782608696,
		     'count': 23},
	     'xyx': {'avgtemp': 74.39287653046891, 'avgtime': 3420.0, 'count': 3}})
    def test_nonsense(self):
        self.run_testcase('cat', 'dog', 'cake', 10, {
            'cakg': {'count': 99, 'avgtemp': 70},
            'gake': {'count': 1, 'avgtemp': 59},
        })
        self.run_testcase('cat', 'dog', 'kitten', 10, {
            'kitteg': {'count': 96, 'avgtemp': 66},
            'kitten': {'count': 4, 'avgtemp': 68},
        })
    '''


if __name__ == '__main__':
    unittest.main()
