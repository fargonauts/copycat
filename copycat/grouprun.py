from workspace import workspace

class GroupRun(object):
    def __init__(self):
        self.name = 'xxx'
        self.maximumNumberOfRuns = 1000
        self.runStrings = []
        self.answers = []
        self.scores = [0] * 100
        self.initial = workspace.initial
        self.modified = workspace.modified
        self.target = workspace.target

groupRun = GroupRun()
