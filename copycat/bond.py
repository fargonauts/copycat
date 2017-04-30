from workspaceStructure import WorkspaceStructure


class Bond(WorkspaceStructure):
    # pylint: disable=too-many-arguments
    def __init__(self, ctx, source, destination, bondCategory, bondFacet,
                 sourceDescriptor, destinationDescriptor):
        WorkspaceStructure.__init__(self, ctx)
        slipnet = self.ctx.slipnet
        self.source = source
        self.string = self.source.string
        self.destination = destination
        self.leftObject = self.source
        self.rightObject = self.destination
        self.directionCategory = slipnet.right
        if self.source.leftIndex > self.destination.rightIndex:
            self.leftObject = self.destination
            self.rightObject = self.source
            self.directionCategory = slipnet.left
        self.facet = bondFacet
        self.sourceDescriptor = sourceDescriptor
        self.destinationDescriptor = destinationDescriptor
        self.category = bondCategory

        self.destinationIsOnRight = self.destination == self.rightObject
        self.bidirectional = (self.sourceDescriptor ==
                              self.destinationDescriptor)
        if self.bidirectional:
            self.directionCategory = None

    def flippedVersion(self):
        slipnet = self.ctx.slipnet
        return Bond(
            self.ctx,
            self.destination, self.source,
            self.category.getRelatedNode(slipnet.opposite),
            self.facet, self.destinationDescriptor, self.sourceDescriptor
        )

    def __repr__(self):
        return '<Bond: %s>' % self.__str__()

    def __str__(self):
        return '%s bond between %s and %s' % (
            self.category.name, self.leftObject, self.rightObject,
        )

    def buildBond(self):
        workspace = self.ctx.workspace
        workspace.structures += [self]
        self.string.bonds += [self]
        self.category.buffer = 100.0
        if self.directionCategory:
            self.directionCategory.buffer = 100.0
        self.leftObject.rightBond = self
        self.rightObject.leftBond = self
        self.leftObject.bonds += [self]
        self.rightObject.bonds += [self]

    def break_the_structure(self):
        self.breakBond()

    def breakBond(self):
        workspace = self.ctx.workspace
        if self in workspace.structures:
            workspace.structures.remove(self)
        if self in self.string.bonds:
            self.string.bonds.remove(self)
        self.leftObject.rightBond = None
        self.rightObject.leftBond = None
        if self in self.leftObject.bonds:
            self.leftObject.bonds.remove(self)
        if self in self.rightObject.bonds:
            self.rightObject.bonds.remove(self)

    def getIncompatibleCorrespondences(self):
        # returns a list of correspondences that are incompatible with
        # self bond
        workspace = self.ctx.workspace
        incompatibles = []
        if self.leftObject.leftmost and self.leftObject.correspondence:
            correspondence = self.leftObject.correspondence
            if self.string == workspace.initial:
                objekt = self.leftObject.correspondence.objectFromTarget
            else:
                objekt = self.leftObject.correspondence.objectFromInitial
            if objekt.leftmost and objekt.rightBond:
                if (
                    objekt.rightBond.directionCategory and
                    objekt.rightBond.directionCategory != self.directionCategory
                ):
                    incompatibles += [correspondence]
        if self.rightObject.rightmost and self.rightObject.correspondence:
            correspondence = self.rightObject.correspondence
            if self.string == workspace.initial:
                objekt = self.rightObject.correspondence.objectFromTarget
            else:
                objekt = self.rightObject.correspondence.objectFromInitial
            if objekt.rightmost and objekt.leftBond:
                if (
                    objekt.leftBond.directionCategory and
                    objekt.leftBond.directionCategory != self.directionCategory
                ):
                    incompatibles += [correspondence]
        return incompatibles

    def updateInternalStrength(self):
        slipnet = self.ctx.slipnet
        # bonds between objects of same type(ie. letter or group) are
        # stronger than bonds between different types
        sourceGap = self.source.leftIndex != self.source.rightIndex
        destinationGap = (self.destination.leftIndex !=
                          self.destination.rightIndex)
        if sourceGap == destinationGap:
            memberCompatibility = 1.0
        else:
            memberCompatibility = 0.7
        # letter category bonds are stronger
        if self.facet == slipnet.letterCategory:
            facetFactor = 1.0
        else:
            facetFactor = 0.7
        strength = min(100.0, memberCompatibility * facetFactor *
                       self.category.bondDegreeOfAssociation())
        self.internalStrength = strength

    def updateExternalStrength(self):
        self.externalStrength = 0.0
        supporters = self.numberOfLocalSupportingBonds()
        if supporters > 0.0:
            density = self.localDensity() / 100.0
            density = density ** 0.5 * 100.0
            supportFactor = 0.6 ** (1.0 / supporters ** 3)
            supportFactor = max(1.0, supportFactor)
            strength = supportFactor * density
            self.externalStrength = strength

    def numberOfLocalSupportingBonds(self):
        return sum(
            1 for b in self.string.bonds if
            b.string == self.source.string and
            self.leftObject.letterDistance(b.leftObject) != 0 and
            self.rightObject.letterDistance(b.rightObject) != 0 and
            self.category == b.category and
            self.directionCategory == b.directionCategory
        )

    def sameCategories(self, other):
        return (self.category == other.category and
                self.directionCategory == other.directionCategory)

    def myEnds(self, object1, object2):
        if self.source == object1 and self.destination == object2:
            return True
        return self.source == object2 and self.destination == object1

    def localDensity(self):
        # returns a rough measure of the density in the string
        # of the same bond-category and the direction-category of
        # the given bond
        workspace = self.ctx.workspace
        slotSum = 0.0
        supportSum = 0.0
        for object1 in workspace.objects:
            if object1.string == self.string:
                for object2 in workspace.objects:
                    if object1.beside(object2):
                        slotSum += 1.0
                        for bond in self.string.bonds:
                            if (
                                bond != self and
                                self.sameCategories(bond) and
                                self.myEnds(object1, object2)
                            ):
                                supportSum += 1.0
        try:
            return 100.0 * supportSum / slotSum
        except ZeroDivisionError:
            return 0.0

    def sameNeighbors(self, other):
        if self.leftObject == other.leftObject:
            return True
        return self.rightObject == other.rightObject

    def getIncompatibleBonds(self):
        return [b for b in self.string.bonds if self.sameNeighbors(b)]

    def set_source(self, value):
        self.source = value

    def possibleGroupBonds(self, bonds):
        result = []
        slipnet = self.ctx.slipnet
        for bond in bonds:
            if (
                bond.category == self.category and
                bond.directionCategory == self.directionCategory
            ):
                result += [bond]
            else:
                # a modified bond might be made
                if bond.category == self.category:
                    return []  # a different bond cannot be made here
                if bond.directionCategory == self.directionCategory:
                    return []  # a different bond cannot be made here
                if slipnet.sameness in [self.category, bond.category]:
                    return []
                bond = Bond(
                    bond.ctx, bond.destination, bond.source, self.category,
                    self.facet, bond.destinationDescriptor,
                    bond.sourceDescriptor
                )
                result += [bond]
        return result
