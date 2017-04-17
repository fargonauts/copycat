
class Context(object):
    def __init__(self):
        self.temperature = None
        self.coderack = None
        self.workspace = None
        self.slipnet = None

    def mainLoop(self, lastUpdate):
        currentTime = coderack.codeletsRun
        temperature.tryUnclamp(currentTime)
        # Every 15 codelets, we update the workspace.
        if currentTime >= lastUpdate + 15:
            self.workspace.updateEverything()
            self.coderack.updateCodelets()
            self.slipnet.update()
            self.temperature.update(self.workspace.getUpdatedTemperature())
            lastUpdate = currentTime
        logging.debug('Number of codelets: %d', len(self.coderack.codelets))
        self.coderack.chooseAndRunCodelet()
        return lastUpdate

    def runTrial(self, answers):
        """Run a trial of the copycat algorithm"""
        self.slipnet.reset()
        self.workspace.reset()
        self.coderack.reset()
        lastUpdate = float('-inf')
        while not self.workspace.foundAnswer:
            lastUpdate = self.mainLoop(lastUpdate)
        if self.workspace.rule:
            answer = self.workspace.rule.finalAnswer
        else:
            answer = None
        finalTemperature = self.temperature.last_unclamped_value
        finalTime = self.coderack.codeletsRun
        print 'Answered %s (time %d, final temperature %.1f)' % (answer, finalTime, finalTemperature)
        answers[answer] = answers.get(answer, {'count': 0, 'tempsum': 0, 'timesum': 0})
        answers[answer]['count'] += 1
        answers[answer]['tempsum'] += finalTemperature
        answers[answer]['timesum'] += finalTime

    def run(self, initial, modified, target, iterations):
        self.workspace.setStrings(initial, modified, target)
        answers = {}
        for i in xrange(iterations):
            self.runTrial(answers)
        for answer, d in answers.iteritems():
            d['avgtemp'] = d.pop('tempsum') / d['count']
            d['avgtime'] = d.pop('timesum') / d['count']
        return answers


context = Context()
