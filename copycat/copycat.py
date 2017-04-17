import logging

from workspace import workspace
from slipnet import slipnet
from temperature import temperature
from coderack import coderack
from coderackPressure import coderackPressures


def updateEverything():
    workspace.updateEverything()
    coderack.updateCodelets()
    slipnet.update()
    workspace.updateTemperature()
    coderackPressures.calculatePressures()


def mainLoop(lastUpdate):
    temperature.tryUnclamp()
    result = lastUpdate
    if not coderack.codeletsRun:
        updateEverything()
        result = coderack.codeletsRun
    elif coderack.codeletsRun - lastUpdate >= slipnet.timeStepLength:
        updateEverything()
        result = coderack.codeletsRun
    logging.debug('Number of codelets: %d', len(coderack.codelets))
    coderack.chooseAndRunCodelet()
    return result


def runTrial(answers):
    """Run a trial of the copycat algorithm"""
    slipnet.reset()
    workspace.reset()
    coderack.reset()
    lastUpdate = 0
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
