import logging

from workspace import workspace
from slipnet import slipnet
from temperature import temperature
from coderack import Coderack


coderack = Coderack()


def mainLoop(lastUpdate):
    currentTime = coderack.codeletsRun
    temperature.tryUnclamp(currentTime)
    # Every 15 codelets, we update the workspace.
    if currentTime >= lastUpdate + 15:
        workspace.updateEverything()
        coderack.updateCodelets()
        slipnet.update()
        workspace.updateTemperature()
        coderack.pressures.calculatePressures()
        lastUpdate = currentTime
    logging.debug('Number of codelets: %d', len(coderack.codelets))
    coderack.chooseAndRunCodelet()
    return lastUpdate


def runTrial(answers):
    """Run a trial of the copycat algorithm"""
    slipnet.reset()
    workspace.reset()
    coderack.reset()
    lastUpdate = float('-inf')
    while not workspace.foundAnswer:
        lastUpdate = mainLoop(lastUpdate)
    if workspace.rule:
        answer = workspace.rule.finalAnswer
    else:
        answer = None
    finalTemperature = temperature.value
    finalTime = coderack.codeletsRun
    print 'Answered %s (time %d, final temperature %.1f)' % (answer, finalTime, finalTemperature)
    answers[answer] = answers.get(answer, {'count': 0, 'tempsum': 0, 'timesum': 0})
    answers[answer]['count'] += 1
    answers[answer]['tempsum'] += finalTemperature
    answers[answer]['timesum'] += finalTime


def run(initial, modified, target, iterations):
    workspace.setStrings(initial, modified, target)
    answers = {}
    for i in xrange(iterations):
        runTrial(answers)
    for answer, d in answers.iteritems():
        d['avgtemp'] = d.pop('tempsum') / d['count']
        d['avgtime'] = d.pop('timesum') / d['count']
    return answers
