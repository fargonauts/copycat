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
        i = -1
        if codelet.name == 'bottom-up-bond-scout':
            i = 0
        if codelet.name == 'top-down-bond-scout--category':
            node = codelet.arguments[0]
            if node == slipnet.successor:
                i = 1
            elif node == slipnet.predecessor:
                i = 2
            else:
                i = 3
        if codelet.name == 'top-down-bond-scout--direction':
            node = codelet.arguments[0]
            if node == slipnet.left:
                i = 4
            elif node == slipnet.right:
                i = 5
            else:
                i = 3
        if codelet.name == 'top-down-group-scout--category':
            node = codelet.arguments[0]
            if node == slipnet.successorGroup:
                i = 6
            elif node == slipnet.predecessorGroup:
                i = 7
            else:
                i = 8
        if codelet.name == 'top-down-group-scout--direction':
            node = codelet.arguments[0]
            if node == slipnet.left:
                i = 9
            elif node == slipnet.right:
                i = 10
        if codelet.name == 'group-scout--whole-string':
            i = 11
        if codelet.name == 'replacement-finder':
            i = 12
        if codelet.name == 'rule-scout':
            i = 13
        if codelet.name == 'rule-translator':
            i = 14
        if codelet.name == 'bottom-up-correspondence-scout':
            i = 15
        if codelet.name == 'important-object-correspondence-scout':
            i = 16
        if codelet.name == 'breaker':
            i = 17
        if i >= 0:
            self.pressures[i].codelets += [codelet]
        if codelet.pressure:
            codelet.pressure.codelets += [codelet]  # XXX why do this
        if i >= 0:
            codelet.pressure = self.pressures[i]     # when this is next?
        logging.info('Add %s: %d' % (codelet.name, i))
        if node:
            logging.info('Node: %s' % node.name)

    def removeCodelet(self, codelet):
        self.removedCodelets += [codelet]

    def numberOfPressures(self):
        return len(self.pressures)

coderackPressures = CoderackPressures()
