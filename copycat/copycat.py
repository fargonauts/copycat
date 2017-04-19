import logging

from coderack import Coderack
from randomness import Randomness
from slipnet import Slipnet
from temperature import Temperature
from workspace import Workspace


class Reporter(object):
    """Do-nothing base class for defining new reporter types"""
    def report_answer(self, answer):
        pass

    def report_coderack(self, coderack):
        pass

    def report_slipnet(self, slipnet):
        pass

    def report_temperature(self, temperature):
        pass


class Copycat(object):
    def __init__(self, rng_seed=None, reporter=None):
        self.coderack = Coderack(self)
        self.random = Randomness(rng_seed)
        self.slipnet = Slipnet()
        self.temperature = Temperature()
        self.workspace = Workspace(self)
        self.reporter = reporter or Reporter()

    def mainLoop(self, lastUpdate):
        currentTime = self.coderack.codeletsRun
        self.temperature.tryUnclamp(currentTime)
        # Every 15 codelets, we update the workspace.
        if currentTime >= lastUpdate + 15:
            self.workspace.updateEverything()
            self.coderack.updateCodelets()
            self.slipnet.update(self.random)
            self.temperature.update(self.workspace.getUpdatedTemperature())
            lastUpdate = currentTime
            self.reporter.report_slipnet(self.slipnet)
        self.coderack.chooseAndRunCodelet()
        self.reporter.report_coderack(self.coderack)
        self.reporter.report_temperature(self.temperature)
        return lastUpdate

    def runTrial(self, answers):
        """Run a trial of the copycat algorithm"""
        self.coderack.reset()
        self.slipnet.reset()
        self.temperature.reset()
        self.workspace.reset()
        lastUpdate = float('-inf')
        while not self.workspace.foundAnswer:
            lastUpdate = self.mainLoop(lastUpdate)
        if self.workspace.rule:
            answer = self.workspace.rule.finalAnswer
        else:
            answer = None
        finalTemperature = self.temperature.last_unclamped_value
        finalTime = self.coderack.codeletsRun
        logging.info('Answered %s (time %d, final temperature %.1f)' % (answer, finalTime, finalTemperature))
        self.reporter.report_answer({
            'answer': answer,
            'temp': finalTemperature,
            'time': finalTime,
        })
        d = answers.setdefault(answer, {
            'count': 0,
            'sumtemp': 0,
            'sumtime': 0
        })
        d['count'] += 1
        d['sumtemp'] += finalTemperature
        d['sumtime'] += finalTime

    def run(self, initial, modified, target, iterations):
        self.workspace.resetWithStrings(initial, modified, target)
        answers = {}
        for i in xrange(iterations):
            self.runTrial(answers)
        for answer, d in answers.iteritems():
            d['avgtemp'] = d.pop('sumtemp') / d['count']
            d['avgtime'] = d.pop('sumtime') / d['count']
        return answers
