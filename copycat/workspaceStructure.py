import formulas


def abstract_call(objekt, name):
    raise NotImplementedError('call of abstract method: %s.%s()' %
                              (objekt.__class__.__name__, name))


class WorkspaceStructure(object):
    def __init__(self):
        from context import context as ctx
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
        """The total weakness is derived from total strength"""
        return 100 - self.totalStrength ** 0.95

    def updateInternalStrength(self):
        """How internally cohesive the structure is"""
        abstract_call(self, 'updateInternalStrength')

    def updateExternalStrength(self):
        abstract_call(self, 'updateExternalStrength')

    def break_the_structure(self):
        """Break this workspace structure

        Exactly what is broken depends on sub-class
        """
        abstract_call(self, 'break_the_structure')
