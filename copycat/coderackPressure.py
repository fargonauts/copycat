import logging
from formulas import Temperature
from slipnet import slipnet


class CoderackPressure(object):
    def __init__(self, name):
        self.name = name

    def reset(self):
        self.values = []
        self.codelets = []


def _codelet_index(codelet):
    name_indices = {
        'bottom-up-bond-scout': 0,
        'top-down-bond-scout--category': {
            slipnet.successor: 1,
            slipnet.predecessor: 2,
            None: 3
        },
        'top-down-bond-scout--direction': {
            slipnet.left: 4,
            slipnet.right: 5,
            None: 3,
        },
        'top-down-group-scout--category': {
            slipnet.successorGroup: 6,
            slipnet.predecessorGroup: 7,
            None: 8,
        },
        'top-down-group-scout--direction': {
            slipnet.left: 9,
            slipnet.right: 10,
            None: -1,
        },
        'group-scout--whole-string': 11,
        'replacement-finder': 12,
        'rule-scout': 13,
        'rule-translator': 14,
        'bottom-up-correspondence-scout': 15,
        'important-object-correspondence-scout': 16,
        'breaker': 17,
    }
    i = name_indices.get(codelet.name, -1)
    try:
        return int(i)
    except (TypeError, ValueError):
        try:
            node = codelet.arguments[0]
            return i[node]
        except KeyError:
            return i[None]


class CoderackPressures(object):
    def __init__(self):
        self.initialisePressures()
        self.reset()

    def initialisePressures(self):
        self.pressures = [
            CoderackPressure('Bottom Up Bonds'),
            CoderackPressure('Top Down Successor Bonds'),
            CoderackPressure('Top Down Predecessor Bonds'),
            CoderackPressure('Top Down Sameness Bonds'),
            CoderackPressure('Top Down Left Bonds'),
            CoderackPressure('Top Down Right Bonds'),
            CoderackPressure('Top Down Successor Group'),
            CoderackPressure('Top Down Predecessor Group'),
            CoderackPressure('Top Down Sameness Group'),
            CoderackPressure('Top Down Left Group'),
            CoderackPressure('Top Down Right Group'),
            CoderackPressure('Bottom Up Whole Group'),
            CoderackPressure('Replacement Finder'),
            CoderackPressure('Rule Codelets'),
            CoderackPressure('Rule Translator'),
            CoderackPressure('Bottom Up Correspondences'),
            CoderackPressure('Important Object Correspondences'),
            CoderackPressure('Breakers'),
        ]

    def calculatePressures(self):
        scale = (100.0 - Temperature + 10.0) / 15.0
        values = map(
            lambda pressure: sum(c.urgency ** scale for c in pressure.codelets),
            self.pressures
        )
        totalValue = sum(values) or 1.0
        values = [value / totalValue for value in values]
        self.maxValue = max(values)
        for pressure, value in zip(self.pressures, values):
            pressure.values += [value * 100.0]
        for codelet in self.removedCodelets:
            if codelet.pressure:
                codelet.pressure.codelets.remove(codelet)
        self.removedCodelets = []

    def reset(self):
        self.maxValue = 0.001
        self.removedCodelets = []
        for pressure in self.pressures:
            pressure.reset()

    def addCodelet(self, codelet):
        i = _codelet_index(codelet)
        if i >= 0:
            codelet.pressure = self.pressures[i]
        if codelet.pressure:
            codelet.pressure.codelets += [codelet]
        logging.info('Add %s: %d', codelet.name, i)

    def removeCodelet(self, codelet):
        self.removedCodelets += [codelet]

    def numberOfPressures(self):
        return len(self.pressures)
