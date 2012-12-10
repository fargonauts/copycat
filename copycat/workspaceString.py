import logging
from letter import Letter
from slipnet import slipnet


class WorkspaceString(object):
    def __init__(self, s):
        self.string = s
        self.bonds = []
        self.objects = []
        self.letters = []
        self.length = len(s)
        self.intraStringUnhappiness = 0.0
        if not self.length:
            return
        position = 0
        from workspace import workspace

        for c in self.string.upper():
            value = ord(c) - ord('A')
            letter = Letter(self, position + 1, self.length)
            letter.workspaceString = self
            letter.addDescription(slipnet.objectCategory, slipnet.letter)
            letter.addDescription(slipnet.letterCategory, slipnet.letters[value])
            letter.describe(position + 1, self.length)
            workspace.buildDescriptions(letter)
            self.letters += [letter]
            position += 1

    def __repr__(self):
        return '<WorkspaceString: %s>' % self.string

    def __str__(self):
        return '%s with %d letters, %d objects, %d bonds' % (self.string, len(self.letters), len(self.objects), len(self.bonds))

    def log(self, heading):
        s = '%s: %s - ' % (heading, self)
        for l in self.letters:
            s += ' %s' % l
        s += '; '
        for o in self.objects:
            s += ' %s' % o
        s += '; '
        for b in self.bonds:
            s += ' %s' % b
        s += '.'
        logging.info(s)

    def __len__(self):
        return len(self.string)

    def __getitem__(self, i):
        return self.string[i]

    def updateRelativeImportance(self):
        """Update the normalised importance of all objects in the string"""
        total = sum([o.rawImportance for o in self.objects])
        if not total:
            for o in self.objects:
                o.relativeImportance = 0.0
        else:
            for o in self.objects:
                logging.info('object: %s, relative: %d = raw: %d / total: %d' % (
                o, o.relativeImportance * 1000, o.rawImportance, total))
                o.relativeImportance = o.rawImportance / total

    def updateIntraStringUnhappiness(self):
        if not len(self.objects):
            self.intraStringUnhappiness = 0.0
            return
        total = sum([o.intraStringUnhappiness for o in self.objects])
        self.intraStringUnhappiness = total / len(self.objects)

    def equivalentGroup(self, sought):
        from group import Group

        for objekt in self.objects:
            if isinstance(objekt, Group):
                if objekt.sameGroup(sought):
                    return objekt
        return None
