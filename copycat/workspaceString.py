from .group import Group
from .letter import Letter


class WorkspaceString(object):
    def __init__(self, ctx, s):
        slipnet = ctx.slipnet
        workspace = ctx.workspace
        self.ctx = ctx
        self.string = s
        self.bonds = []
        self.objects = []
        self.letters = []
        self.length = len(s)
        self.intraStringUnhappiness = 0.0

        for position, c in enumerate(self.string.upper(), 1):
            value = ord(c) - ord('A')
            letter = Letter(self, position, self.length)
            letter.workspaceString = self
            letter.addDescription(slipnet.objectCategory, slipnet.letter)
            letter.addDescription(slipnet.letterCategory, slipnet.letters[value])
            letter.describe(position, self.length)
            workspace.buildDescriptions(letter)
            self.letters += [letter]

    def __repr__(self):
        return '<WorkspaceString: %s>' % self.string

    def __str__(self):
        return '%s with %d letters, %d objects, %d bonds' % (
            self.string, len(self.letters), len(self.objects), len(self.bonds))

    def __len__(self):
        return len(self.string)

    def __getitem__(self, i):
        return self.string[i]

    def updateRelativeImportance(self):
        """Update the normalised importance of all objects in the string"""
        total = sum(o.rawImportance for o in self.objects)
        if not total:
            for o in self.objects:
                o.relativeImportance = 0.0
        else:
            for o in self.objects:
                o.relativeImportance = o.rawImportance / total

    def updateIntraStringUnhappiness(self):
        if not len(self.objects):
            self.intraStringUnhappiness = 0.0
            return
        total = sum(o.intraStringUnhappiness for o in self.objects)
        self.intraStringUnhappiness = total / len(self.objects)

    def equivalentGroup(self, sought):
        for objekt in self.objects:
            if isinstance(objekt, Group):
                if objekt.sameGroup(sought):
                    return objekt
        return None
