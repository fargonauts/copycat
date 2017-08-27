from . import formulas


class WorkspaceStructure(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.string = None
        self.internalStrength = 0.0
        self.externalStrength = 0.0
        self.totalStrength = 0.0

    def updateStrength(self):
        self.updateInternalStrength()
        self.updateExternalStrength()
        self.updateTotalStrength()

    def updateTotalStrength(self):
        """Recalculate the strength from internal and external strengths"""
        weights = ((self.internalStrength, self.internalStrength),
                   (self.externalStrength, 100 - self.internalStrength))
        strength = formulas.weightedAverage(weights)
        self.totalStrength = strength

    def totalWeakness(self):
        return 100 - self.totalStrength ** 0.95

    def updateInternalStrength(self):
        raise NotImplementedError()

    def updateExternalStrength(self):
        raise NotImplementedError()

    def break_the_structure(self):
        """Break this workspace structure (Bond, Correspondence, or Group)"""
        raise NotImplementedError()
