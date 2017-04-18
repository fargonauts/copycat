from conceptMapping import ConceptMapping
from letter import Letter
from workspaceStructure import WorkspaceStructure
import formulas


class Correspondence(WorkspaceStructure):
    def __init__(self, objectFromInitial, objectFromTarget,
                 conceptMappings, flipTargetObject):
        from context import context as ctx
        WorkspaceStructure.__init__(self, ctx)
        self.objectFromInitial = objectFromInitial
        self.objectFromTarget = objectFromTarget
        self.conceptMappings = conceptMappings
        self.flipTargetObject = flipTargetObject
        self.accessoryConceptMappings = []

    def __repr__(self):
        return '<%s>' % self.__str__()

    def __str__(self):
        return 'Correspondence between %s and %s' % (
            self.objectFromInitial, self.objectFromTarget)

    def distinguishingConceptMappings(self):
        return [m for m in self.conceptMappings if m.distinguishing()]

    def relevantDistinguishingConceptMappings(self):
        return [m for m in self.conceptMappings
                if m.distinguishing() and m.relevant()]

    def extract_target_bond(self):
        targetBond = False
        if self.objectFromTarget.leftmost:
            targetBond = self.objectFromTarget.rightBond
        elif self.objectFromTarget.rightmost:
            targetBond = self.objectFromTarget.leftBond
        return targetBond

    def extract_initial_bond(self):
        initialBond = False
        if self.objectFromInitial.leftmost:
            initialBond = self.objectFromInitial.rightBond
        elif self.objectFromInitial.rightmost:
            initialBond = self.objectFromInitial.leftBond
        return initialBond

    def getIncompatibleBond(self):
        slipnet = self.ctx.slipnet
        initialBond = self.extract_initial_bond()
        if not initialBond:
            return None
        targetBond = self.extract_target_bond()
        if not targetBond:
            return None
        if initialBond.directionCategory and targetBond.directionCategory:
            mapping = ConceptMapping(
                slipnet.directionCategory,
                slipnet.directionCategory,
                initialBond.directionCategory,
                targetBond.directionCategory,
                None,
                None
            )
            for m in self.conceptMappings:
                if m.incompatible(mapping):
                    return targetBond
        return None

    def getIncompatibleCorrespondences(self):
        workspace = self.ctx.workspace
        return [o.correspondence for o in workspace.initial.objects
                if o and self.incompatible(o.correspondence)]

    def incompatible(self, other):
        if not other:
            return False
        if self.objectFromInitial == other.objectFromInitial:
            return True
        if self.objectFromTarget == other.objectFromTarget:
            return True
        for mapping in self.conceptMappings:
            for otherMapping in other.conceptMappings:
                if mapping.incompatible(otherMapping):
                    return True
        return False

    def supporting(self, other):
        if self == other:
            return False
        if self.objectFromInitial == other.objectFromInitial:
            return False
        if self.objectFromTarget == other.objectFromTarget:
            return False
        if self.incompatible(other):
            return False
        for mapping in self.distinguishingConceptMappings():
            for otherMapping in other.distinguishingConceptMappings():
                if mapping.supports(otherMapping):
                    return True
        return False

    def support(self):
        workspace = self.ctx.workspace
        if isinstance(self.objectFromInitial, Letter):
            if self.objectFromInitial.spansString():
                return 100.0
        if isinstance(self.objectFromTarget, Letter):
            if self.objectFromTarget.spansString():
                return 100.0
        total = sum(c.totalStrength for c in workspace.correspondences()
                    if self.supporting(c))
        return min(total, 100.0)

    def updateInternalStrength(self):
        """A function of how many concept mappings there are

        Also considered: their strength and how well they cohere"""
        distinguishingMappings = self.relevantDistinguishingConceptMappings()
        numberOfConceptMappings = len(distinguishingMappings)
        if numberOfConceptMappings < 1:
            self.internalStrength = 0.0
            return
        totalStrength = sum(m.strength() for m in distinguishingMappings)
        averageStrength = totalStrength / numberOfConceptMappings
        if numberOfConceptMappings == 1.0:
            numberOfConceptMappingsFactor = 0.8
        elif numberOfConceptMappings == 2.0:
            numberOfConceptMappingsFactor = 1.2
        else:
            numberOfConceptMappingsFactor = 1.6
        if self.internallyCoherent():
            internalCoherenceFactor = 2.5
        else:
            internalCoherenceFactor = 1.0
        internalStrength = (averageStrength * internalCoherenceFactor *
                            numberOfConceptMappingsFactor)
        self.internalStrength = min(internalStrength, 100.0)

    def updateExternalStrength(self):
        self.externalStrength = self.support()

    def internallyCoherent(self):
        """Whether any pair of distinguishing mappings support each other"""
        mappings = self.relevantDistinguishingConceptMappings()
        for i in xrange(len(mappings)):
            for j in xrange(len(mappings)):
                if i != j:
                    if mappings[i].supports(mappings[j]):
                        return True
        return False

    def slippages(self):
        mappings = [m for m in self.conceptMappings if m.slippage()]
        mappings += [m for m in self.accessoryConceptMappings if m.slippage()]
        return mappings

    def reflexive(self):
        initial = self.objectFromInitial
        if not initial.correspondence:
            return False
        if initial.correspondence.objectFromTarget == self.objectFromTarget:
            return True
        return False

    def buildCorrespondence(self):
        workspace = self.ctx.workspace
        workspace.structures += [self]
        if self.objectFromInitial.correspondence:
            self.objectFromInitial.correspondence.breakCorrespondence()
        if self.objectFromTarget.correspondence:
            self.objectFromTarget.correspondence.breakCorrespondence()
        self.objectFromInitial.correspondence = self
        self.objectFromTarget.correspondence = self
        # add mappings to accessory-concept-mapping-list
        relevantMappings = self.relevantDistinguishingConceptMappings()
        for mapping in relevantMappings:
            if mapping.slippage():
                self.accessoryConceptMappings += [mapping.symmetricVersion()]
        from group import Group
        if isinstance(self.objectFromInitial, Group):
            if isinstance(self.objectFromTarget, Group):
                bondMappings = formulas.getMappings(
                    self.objectFromInitial,
                    self.objectFromTarget,
                    self.objectFromInitial.bondDescriptions,
                    self.objectFromTarget.bondDescriptions
                )
                for mapping in bondMappings:
                    self.accessoryConceptMappings += [mapping]
                    if mapping.slippage():
                        self.accessoryConceptMappings += [
                            mapping.symmetricVersion()]
        for mapping in self.conceptMappings:
            if mapping.label:
                mapping.label.activation = 100.0

    def break_the_structure(self):
        self.breakCorrespondence()

    def breakCorrespondence(self):
        workspace = self.ctx.workspace
        workspace.structures.remove(self)
        self.objectFromInitial.correspondence = None
        self.objectFromTarget.correspondence = None
