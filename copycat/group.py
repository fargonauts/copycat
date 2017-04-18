import logging

from description import Description
from workspaceObject import WorkspaceObject
import formulas


class Group(WorkspaceObject):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, string, groupCategory, directionCategory, facet,
                 objectList, bondList):
        # pylint: disable=too-many-arguments
        WorkspaceObject.__init__(self, string)
        slipnet = self.ctx.slipnet
        self.groupCategory = groupCategory
        self.directionCategory = directionCategory
        self.facet = facet
        self.objectList = objectList
        self.bondList = bondList
        self.bondCategory = self.groupCategory.getRelatedNode(
            slipnet.bondCategory)

        leftObject = objectList[0]
        rightObject = objectList[-1]
        self.leftIndex = leftObject.leftIndex
        self.leftmost = self.leftIndex == 1
        self.rightIndex = rightObject.rightIndex
        self.rightmost = self.rightIndex == len(self.string)

        self.descriptions = []
        self.bondDescriptions = []
        self.extrinsicDescriptions = []
        self.outgoingBonds = []
        self.incomingBonds = []
        self.bonds = []
        self.leftBond = None
        self.rightBond = None
        self.correspondence = None
        self.changed = False
        self.newAnswerLetter = False
        self.clampSalience = False
        self.name = ''

        if self.bondList and len(self.bondList):
            firstFacet = self.bondList[0].facet
            self.addBondDescription(
                Description(self, slipnet.bondFacet, firstFacet))
        self.addBondDescription(
            Description(self, slipnet.bondCategory, self.bondCategory))

        self.addDescription(slipnet.objectCategory, slipnet.group)
        self.addDescription(slipnet.groupCategory, self.groupCategory)
        if not self.directionCategory:
            # sameness group - find letterCategory
            letter = self.objectList[0].getDescriptor(self.facet)
            self.addDescription(self.facet, letter)
        if self.directionCategory:
            self.addDescription(slipnet.directionCategory,
                                self.directionCategory)
        if self.spansString():
            self.addDescription(slipnet.stringPositionCategory, slipnet.whole)
        elif self.leftIndex == 1:
            self.addDescription(
                slipnet.stringPositionCategory, slipnet.leftmost)
        elif self.rightIndex == self.string.length:
            self.addDescription(
                slipnet.stringPositionCategory, slipnet.rightmost)
        elif self.middleObject():
            self.addDescription(
                slipnet.stringPositionCategory, slipnet.middle)
        self.add_length_description_category()

    def add_length_description_category(self):
        #check whether or not to add length description category
        random = self.ctx.random
        slipnet = self.ctx.slipnet
        probability = self.lengthDescriptionProbability()
        if random.coinFlip(probability):
            length = len(self.objectList)
            if length < 6:
                self.addDescription(slipnet.length,
                                    slipnet.numbers[length - 1])

    def __str__(self):
        s = self.string.__str__()
        l = self.leftIndex - 1
        r = self.rightIndex
        return 'group[%d:%d] == %s' % (l, r - 1, s[l:r])

    def getIncompatibleGroups(self):
        result = []
        for objekt in self.objectList:
            while objekt.group:
                result += [objekt.group]
                objekt = objekt.group
        return result

    def addBondDescription(self, description):
        self.bondDescriptions += [description]

    def singleLetterGroupProbability(self):
        slipnet = self.ctx.slipnet
        temperature = self.ctx.temperature
        numberOfSupporters = self.numberOfLocalSupportingGroups()
        if not numberOfSupporters:
            return 0.0
        if numberOfSupporters == 1:
            exp = 4.0
        elif numberOfSupporters == 2:
            exp = 2.0
        else:
            exp = 1.0
        support = self.localSupport() / 100.0
        activation = slipnet.length.activation / 100.0
        supportedActivation = (support * activation) ** exp
        return temperature.getAdjustedProbability(supportedActivation)

    def flippedVersion(self):
        slipnet = self.ctx.slipnet
        flippedBonds = [b.flippedversion() for b in self.bondList]
        flippedGroup = self.groupCategory.getRelatedNode(slipnet.flipped)
        flippedDirection = self.directionCategory.getRelatedNode(
            slipnet.flipped)
        return Group(self.string, flippedGroup, flippedDirection,
                     self.facet, self.objectList, flippedBonds)

    def buildGroup(self):
        workspace = self.ctx.workspace
        workspace.objects += [self]
        workspace.structures += [self]
        self.string.objects += [self]
        for objekt in self.objectList:
            objekt.group = self
        workspace.buildDescriptions(self)
        self.activateDescriptions()

    def activateDescriptions(self):
        for description in self.descriptions:
            logging.info('Activate: %s', description)
            description.descriptor.buffer = 100.0

    def lengthDescriptionProbability(self):
        slipnet = self.ctx.slipnet
        temperature = self.ctx.temperature
        length = len(self.objectList)
        if length > 5:
            return 0.0
        cubedlength = length ** 3
        fred = cubedlength * (100.0 - slipnet.length.activation) / 100.0
        probability = 0.5 ** fred
        value = temperature.getAdjustedProbability(probability)
        if value < 0.06:
            value = 0.0  # otherwise 1/20 chance always
        return value

    def break_the_structure(self):
        self.breakGroup()

    def breakGroup(self):
        workspace = self.ctx.workspace
        while len(self.descriptions):
            description = self.descriptions[-1]
            description.breakDescription()
        for objekt in self.objectList:
            objekt.group = None
        if self.group:
            self.group.breakGroup()
        if self in workspace.structures:
            workspace.structures.remove(self)
        if self in workspace.objects:
            workspace.objects.remove(self)
        if self in self.string.objects:
            self.string.objects.remove(self)
        if self.correspondence:
            self.correspondence.breakCorrespondence()
        if self.leftBond:
            self.leftBond.breakBond()
        if self.rightBond:
            self.rightBond.breakBond()

    def updateInternalStrength(self):
        slipnet = self.ctx.slipnet
        relatedBondAssociation = self.groupCategory.getRelatedNode(
            slipnet.bondCategory).degreeOfAssociation()
        bondWeight = relatedBondAssociation ** 0.98
        length = len(self.objectList)
        if length == 1:
            lengthFactor = 5.0
        elif length == 2:
            lengthFactor = 20.0
        elif length == 3:
            lengthFactor = 60.0
        else:
            lengthFactor = 90.0
        lengthWeight = 100.0 - bondWeight
        weightList = ((relatedBondAssociation, bondWeight),
                      (lengthFactor, lengthWeight))
        self.internalStrength = formulas.weightedAverage(weightList)

    def updateExternalStrength(self):
        if self.spansString():
            self.externalStrength = 100.0
        else:
            self.externalStrength = self.localSupport()

    def localSupport(self):
        numberOfSupporters = self.numberOfLocalSupportingGroups()
        if numberOfSupporters == 0:
            return 0.0
        supportFactor = min(1.0, 0.6 ** (1 / (numberOfSupporters ** 3)))
        densityFactor = 100.0 * ((self.localDensity() / 100.0) ** 0.5)
        return densityFactor * supportFactor

    def numberOfLocalSupportingGroups(self):
        count = 0
        for objekt in self.string.objects:
            if isinstance(objekt, Group):
                if  (objekt.rightIndex < self.leftIndex or
                     objekt.leftIndex > self.rightIndex):
                    if  (objekt.groupCategory == self.groupCategory and
                         objekt.directionCategory == self.directionCategory):
                        count += 1
        return count

    def localDensity(self):
        numberOfSupporters = self.numberOfLocalSupportingGroups()
        halfLength = len(self.string) / 2.0
        return 100.0 * numberOfSupporters / halfLength

    def sameGroup(self, other):
        if self.leftIndex != other.leftIndex:
            return False
        if self.rightIndex != other.rightIndex:
            return False
        if self.groupCategory != other.groupCategory:
            return False
        if self.directionCategory != other.directionCategory:
            return False
        if self.facet != other.facet:
            return False
        return True

    def morePossibleDescriptions(self, node):
        slipnet = self.ctx.slipnet
        result = []
        for i, number in enumerate(slipnet.numbers, 1):
            if node == number and len(self.objects) == i:
                result += [node]
        return result

    def distinguishingDescriptor(self, descriptor):
        """Whether no other object of the same type has the same descriptor"""
        if not WorkspaceObject.distinguishingDescriptor(self, descriptor):
            return False
        for objekt in self.string.objects:
            # check to see if they are of the same type
            if isinstance(objekt, Group) and objekt != self:
                # check all descriptions for the descriptor
                for description in objekt.descriptions:
                    if description.descriptor == descriptor:
                        return False
        return True
