import logging
logging.basicConfig(level=logging.INFO, format='%(message)s',
                    filename='./copycat.log', filemode='w')


from workspace import workspace
from workspaceFormulas import workspaceFormulas
from slipnet import slipnet
from temperature import temperature
from coderack import coderack
from coderackPressure import coderackPressures


def updateEverything():
    workspace.updateEverything()
    coderack.updateCodelets()
    slipnet.update()
    workspaceFormulas.updateTemperature()
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


def runTrial():
    """Run a trial of the copycat algorithm"""
    answers = {}
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
    print '%d: %s' % (coderack.codeletsRun, answer)
    answers[answer] = answers.get(answer, 0) + 1
    logging.debug('codelets used:')
    for answer, count in answers.iteritems():
        print '%s:%d' % (answer, count)


def run(initial, modified, target):
    workspace.setStrings(initial, modified, target)
    runTrial()
