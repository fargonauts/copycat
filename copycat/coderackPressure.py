import logging
from formulas import Temperature
from slipnet import slipnet


class CoderackPressure(object):
    def __init__(self, name):
        self.name = name

    def reset(self):
        self.unmodifedValues = []
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
    except ValueError:
        try:
            node = codelet.arguments[0]
            return i[node]
        except KeyError:
            return i[None]


class CoderackPressures(object):
    def __init__(self):
        #logging.debug('coderackPressures.__init__()')
        self.initialisePressures()
        self.reset()

    def initialisePressures(self):
        #logging.debug('coderackPressures.initialisePressures()')
        self.pressures = []
        self.pressures += [CoderackPressure('Bottom Up Bonds')]
        self.pressures += [CoderackPressure('Top Down Successor Bonds')]
        self.pressures += [CoderackPressure('Top Down Predecessor Bonds')]
        self.pressures += [CoderackPressure('Top Down Sameness Bonds')]
        self.pressures += [CoderackPressure('Top Down Left Bonds')]
        self.pressures += [CoderackPressure('Top Down Right Bonds')]
        self.pressures += [CoderackPressure('Top Down Successor Group')]
        self.pressures += [CoderackPressure('Top Down Predecessor Group')]
        self.pressures += [CoderackPressure('Top Down Sameness Group')]
        self.pressures += [CoderackPressure('Top Down Left Group')]
        self.pressures += [CoderackPressure('Top Down Right Group')]
        self.pressures += [CoderackPressure('Bottom Up Whole Group')]
        self.pressures += [CoderackPressure('Replacement Finder')]
        self.pressures += [CoderackPressure('Rule Codelets')]
        self.pressures += [CoderackPressure('Rule Translator')]
        self.pressures += [CoderackPressure('Bottom Up Correspondences')]
        self.pressures += [CoderackPressure(
            'Important Object Correspondences')]
        self.pressures += [CoderackPressure('Breakers')]

    def calculatePressures(self):
        #logging.debug('coderackPressures.calculatePressures()')
        scale = (100.0 - Temperature + 10.0) / 15.0
        values = []
        for pressure in self.pressures:
            value = sum([c.urgency ** scale for c in pressure.codelets])
            values += [value]
        totalValue = sum(values)
        if not totalValue:
            totalValue = 1.0
        values = [value / totalValue for value in values]
        self.maxValue = max(values)
        for pressure, value in zip(self.pressures, values):
            pressure.values += [value * 100.0]
        for codelet in self.removedCodelets:
            if codelet.pressure:
                codelet.pressure.codelets.removeElement(codelet)
        self.removedCodelets = []

    def reset(self):
        #logging.debug('coderackPressures.reset()')
        self.maxValue = 0.001
        for pressure in self.pressures:
            pressure.reset()
        self.removedCodelets = []

    def addCodelet(self, codelet):
        node = None
        i = _codelet_index(codelet)
        if i >= 0:
            self.pressures[i].codelets += [codelet]
        if codelet.pressure:
            codelet.pressure.codelets += [codelet]
        if i >= 0:
            codelet.pressure = self.pressures[i]
        logging.info('Add %s: %d', codelet.name, i)
        if node:
            logging.info('Node: %s', node.name)

    def removeCodelet(self, codelet):
        self.removedCodelets += [codelet]

    def numberOfPressures(self):
        return len(self.pressures)

coderackPressures = CoderackPressures()
