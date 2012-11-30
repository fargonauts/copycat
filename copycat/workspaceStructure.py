import formulas

class WorkspaceStructure(object):
    def __init__(self):
        self.string = None
        self.internalStrength = 0.0
        self.externalStrength = 0.0
        self.totalStrength = 0.0

    def updateStrength(self):
        self.updateInternalStrength()
        self.updateExternalStrength()
        self.updateTotalStrength()

    def updateTotalStrength(self):
        """Recalculate the total strength based on internal and external strengths"""
        weights = ( (self.internalStrength, self.internalStrength), (self.externalStrength, 100 - self.internalStrength) )
        strength = formulas.weightedAverage(weights)
        self.totalStrength = strength

    def totalWeakness(self):
        """The total weakness is derived from total strength"""
        return 100 - self.totalStrength ** 0.95

    def updateInternalStrength(self):
        """How internally cohesive the structure is"""
        raise NotImplementedError, 'call of abstract method: WorkspaceStructure.updateInternalStrength()'

    def updateExternalStrength(self):
        raise NotImplementedError, 'call of abstract method: WorkspaceStructure.updateExternalStrength()'

    def break_the_structure(self):
        """Break this workspace structure

        Exactly what is broken depends on sub-class
        """
        raise NotImplementedError, 'call of abstract method: WorkspaceStructure.break_the_structure()'
