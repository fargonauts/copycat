import logging

from description import Description
from formulas import weightedAverage
from workspaceStructure import WorkspaceStructure


class WorkspaceObject(WorkspaceStructure):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, workspaceString):
        WorkspaceStructure.__init__(self)
        self.string = workspaceString
        self.descriptions = []
        self.extrinsicDescriptions = []
        self.incomingBonds = []
        self.outgoingBonds = []
        self.bonds = []
        self.group = None
        self.changed = None
        self.correspondence = None
        self.clampSalience = False
        self.rawImportance = 0.0
        self.relativeImportance = 0.0
        self.leftBond = None
        self.rightBond = None
        self.newAnswerLetter = False
        self.name = ''
        self.replacement = None
        self.rightIndex = 0
        self.leftIndex = 0
        self.leftmost = False
        self.rightmost = False
        self.intraStringSalience = 0.0
        self.interStringSalience = 0.0
        self.totalSalience = 0.0
        self.intraStringUnhappiness = 0.0
        self.interStringUnhappiness = 0.0
        self.totalUnhappiness = 0.0

    def __str__(self):
        return 'object'

    def spansString(self):
        return self.leftmost and self.rightmost

    def addDescription(self, descriptionType, descriptor):
        description = Description(self, descriptionType, descriptor)
        logging.info("Adding description: %s to %s", description, self)
        self.descriptions += [description]

    def addDescriptions(self, descriptions):
        workspace = self.ctx.workspace
        copy = descriptions[:]  # in case we add to our own descriptions
        for description in copy:
            logging.info('might add: %s', description)
            if not self.containsDescription(description):
                self.addDescription(description.descriptionType,
                                    description.descriptor)
            else:
                logging.info("Won't add it")
        workspace.buildDescriptions(self)

    def __calculateIntraStringHappiness(self):
        if self.spansString():
            return 100.0
        if self.group:
            return self.group.totalStrength
        bondStrength = sum(bond.totalStrength for bond in self.bonds)
        return bondStrength / 6.0

    def __calculateRawImportance(self):
        """Calculate the raw importance of this object.

        Which is the sum of all relevant descriptions"""
        result = 0.0
        for description in self.descriptions:
            if description.descriptionType.fully_active():
                result += description.descriptor.activation
            else:
                result += description.descriptor.activation / 20.0
        if self.group:
            result *= 2.0 / 3.0
        if self.changed:
            result *= 2.0
        return result

    def updateValue(self):
        self.rawImportance = self.__calculateRawImportance()
        intraStringHappiness = self.__calculateIntraStringHappiness()
        self.intraStringUnhappiness = 100.0 - intraStringHappiness

        interStringHappiness = 0.0
        if self.correspondence:
            interStringHappiness = self.correspondence.totalStrength
        self.interStringUnhappiness = 100.0 - interStringHappiness

        averageHappiness = (intraStringHappiness + interStringHappiness) / 2
        self.totalUnhappiness = 100.0 - averageHappiness

        if self.clampSalience:
            self.intraStringSalience = 100.0
            self.interStringSalience = 100.0
        else:
            self.intraStringSalience = weightedAverage((
                (self.relativeImportance, 0.2),
                (self.intraStringUnhappiness, 0.8)))
            self.interStringSalience = weightedAverage((
                (self.relativeImportance, 0.8),
                (self.interStringUnhappiness, 0.2)))
        self.totalSalience = (self.intraStringSalience +
                              self.interStringSalience) / 2.0
        logging.info('Set salience of %s to %f = (%f + %f)/2',
                     self.__str__(), self.totalSalience,
                     self.intraStringSalience, self.interStringSalience)

    def isWithin(self, other):
        return (self.leftIndex >= other.leftIndex and
                self.rightIndex <= other.rightIndex)

    def relevantDescriptions(self):
        return [d for d in self.descriptions
                if d.descriptionType.fully_active()]

    def getPossibleDescriptions(self, descriptionType):
        from group import Group  # gross, TODO FIXME
        slipnet = self.ctx.slipnet
        logging.info('getting possible descriptions for %s', self)
        descriptions = []
        for link in descriptionType.instanceLinks:
            node = link.destination
            if node == slipnet.first and self.described(slipnet.letters[0]):
                descriptions += [node]
            if node == slipnet.last and self.described(slipnet.letters[-1]):
                descriptions += [node]
            for i, number in enumerate(slipnet.numbers, 1):
                if node == number and isinstance(self, Group):
                    if len(self.objectList) == i:
                        descriptions += [node]
            if node == slipnet.middle and self.middleObject():
                descriptions += [node]
        s = ''
        for d in descriptions:
            s = '%s, %s' % (s, d.get_name())
        logging.info(s)
        return descriptions

    def containsDescription(self, sought):
        soughtType = sought.descriptionType
        soughtDescriptor = sought.descriptor
        for d in self.descriptions:
            if soughtType == d.descriptionType:
                if soughtDescriptor == d.descriptor:
                    return True
        return False

    def described(self, slipnode):
        return any(d.descriptor == slipnode for d in self.descriptions)

    def middleObject(self):
        # only works if string is 3 chars long
        # as we have access to the string, why not just " == len / 2" ?
        objectOnMyRightIsRightmost = objectOnMyLeftIsLeftmost = False
        for objekt in self.string.objects:
            if objekt.leftmost and objekt.rightIndex == self.leftIndex - 1:
                objectOnMyLeftIsLeftmost = True
            if objekt.rightmost and objekt.leftIndex == self.rightIndex + 1:
                objectOnMyRightIsRightmost = True
        return objectOnMyRightIsRightmost and objectOnMyLeftIsLeftmost

    def distinguishingDescriptor(self, descriptor):
        slipnet = self.ctx.slipnet
        return slipnet.isDistinguishingDescriptor(descriptor)

    def relevantDistinguishingDescriptors(self):
        slipnet = self.ctx.slipnet
        return [d.descriptor
                for d in self.relevantDescriptions()
                if slipnet.isDistinguishingDescriptor(d.descriptor)]

    def getDescriptor(self, descriptionType):
        """The description attached to this object of the description type."""
        logging.info("\nIn %s, trying for type: %s",
                     self, descriptionType.get_name())
        for description in self.descriptions:
            logging.info("Trying description: %s", description)
            if description.descriptionType == descriptionType:
                return description.descriptor
        return None

    def getDescriptionType(self, sought_description):
        """The description_type attached to this object of that description"""
        for description in self.descriptions:
            if description.descriptor == sought_description:
                return description.descriptionType
        return None

    def getCommonGroups(self, other):
        return [o for o in self.string.objects
                if self.isWithin(o) and other.isWithin(o)]

    def letterDistance(self, other):
        if other.leftIndex > self.rightIndex:
            return other.leftIndex - self.rightIndex
        if self.leftIndex > other.rightIndex:
            return self.leftIndex - other.rightIndex
        return 0

    def letterSpan(self):
        return self.rightIndex - self.leftIndex + 1

    def beside(self, other):
        if self.string != other.string:
            return False
        if self.leftIndex == other.rightIndex + 1:
            return True
        return other.leftIndex == self.rightIndex + 1
