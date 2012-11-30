import logging

from description import Description
from slipnet import slipnet
from workspaceStructure import WorkspaceStructure

class WorkspaceObject(WorkspaceStructure):
    def __init__(self,workspaceString):
        WorkspaceStructure.__init__(self)
        self.string = workspaceString
        #self.string.objects += [ self ]
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
        self.rightStringPosition = 0
        self.leftStringPosition = 0
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

    def addDescription(self,descriptionType,descriptor):
        description = Description(self,descriptionType,descriptor)
        logging.info("Adding description: %s to %s" % (description,self))
        self.descriptions += [ description ]

    def addDescriptions(self,descriptions):
        #print 'addDescriptions 1'
        #print 'add %d to %d of %s' % (len(descriptions),len(self.descriptions), self.string.string)
        copy = descriptions[:] # in case we add to our own descriptions, which turns the loop infinite
        for description in copy:
            #print '%d addDescriptions 2 %s ' % (len(descriptions),description)
            logging.info('might add: %s' % description)
            if not self.containsDescription(description):
                #print '%d addDescriptions 3 %s ' % (len(descriptions),description)
                self.addDescription(description.descriptionType,description.descriptor)
                #print '%d addDescriptions 4 %s ' % (len(descriptions),description)
            else:
                logging.info("Won't add it")
        #print '%d added, have %d ' % (len(descriptions),len(self.descriptions))
        from workspace import workspace
        workspace.buildDescriptions(self)

    def __calculateIntraStringHappiness(self):
        if self.spansString():
            return 100.0
        if self.group:
            return self.group.totalStrength
        bondStrength = 0.0
        for bond in self.bonds:
            bondStrength += bond.totalStrength
        divisor = 6.0
        if self.spansString(): # XXX then we have already returned
            divisor = 3.0
        return bondStrength / divisor

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
        #logging.info("Unhappy: %s"%self.interStringUnhappiness)

        averageHappiness = ( intraStringHappiness + interStringHappiness ) / 2
        self.totalUnhappiness = 100.0 - averageHappiness

        if self.clampSalience:
            self.intraStringSalience = 100.0
            self.interStringSalience = 100.0
        else:
            from formulas import weightedAverage
            self.intraStringSalience = weightedAverage( ((self.relativeImportance,0.2), (self.intraStringUnhappiness,0.8)) )
            self.interStringSalience = weightedAverage( ((self.relativeImportance,0.8), (self.interStringUnhappiness,0.2)) )
        self.totalSalience = (self.intraStringSalience + self.interStringSalience) / 2.0
        logging.info('Set salience of %s to %f = (%f + %f)/2' % (
            self.__str__(),self.totalSalience, self.intraStringSalience, self.interStringSalience))

    def isWithin(self,other):
        return self.leftStringPosition >= other.leftStringPosition and self.rightStringPosition <= other.rightStringPosition

    def relevantDescriptions(self):
        return [ d for d in self.descriptions if d.descriptionType.fully_active() ]

    def morePossibleDescriptions(self,node):
        return []

    def getPossibleDescriptions(self,descriptionType):
        logging.info('getting possible descriptions for %s' % self)
        descriptions = [ ]
        from group import Group
        for link in descriptionType.instanceLinks:
            node = link.destination
            if node == slipnet.first and self.hasDescription(slipnet.letters[0]):
                descriptions += [ node ]
            if node == slipnet.last and self.hasDescription(slipnet.letters[-1]):
                descriptions += [ node ]
            i = 1
            for number in slipnet.numbers:
                if node == number and isinstance(self,Group) and len(self.objectList) == i:
                    descriptions += [ node ]
                i += 1
            if node == slipnet.middle and self.middleObject():
                descriptions += [ node ]
        s = ''
        for d in descriptions:
            s = '%s, %s' % (s,d.get_name())
        logging.info(s)
        return descriptions

    def containsDescription(self,sought):
        soughtType = sought.descriptionType
        soughtDescriptor = sought.descriptor
        for d in self.descriptions:
            if soughtType == d.descriptionType and soughtDescriptor == d.descriptor:
                return True
        return False

    def hasDescription(self,slipnode):
        return [ d for d in self.descriptions if d.descriptor == slipnode ] and True or False

    def middleObject(self):
        # XXX only works if string is 3 chars long
        # as we have access to the string, why not just " == len / 2" ?
        objectOnMyRightIsRightmost = objectOnMyLeftIsLeftmost = False
        for objekt in self.string.objects:
            if objekt.leftmost and objekt.rightStringPosition == self.leftStringPosition - 1:
                objectOnMyLeftIsLeftmost = True
            if objekt.rightmost and objekt.leftStringPosition == self.rightStringPosition + 1:
                objectOnMyRightIsRightmost = True
        return objectOnMyRightIsRightmost and objectOnMyLeftIsLeftmost

    def distinguishingDescriptor(self,descriptor):
        """Whether no other object of the same type (ie. letter or group) has the same descriptor"""
        if descriptor == slipnet.letter:
            return False
        if descriptor == slipnet.group:
            return False
        for number in slipnet.numbers:
            if number == descriptor:
                return False
        return True

    def relevantDistinguishingDescriptors(self):
        return [ d.descriptor for d in self.relevantDescriptions() if self.distinguishingDescriptor(d.descriptor) ]

    def getDescriptor(self,descriptionType):
        """The description attached to this object of the specified description type."""
        descriptor = None
        logging.info("\nIn %s, trying for type: %s" % (self,descriptionType.get_name()))
        for description in self.descriptions:
            logging.info("Trying description: %s" % description)
            if description.descriptionType == descriptionType:
                return description.descriptor
        return descriptor

    def getDescriptionType(self,sought_description):
        """The description_type attached to this object of the specified description"""
        for description in self.descriptions:
            if description.descriptor == sought_description:
                return description.descriptionType
        description = None
        return description

    def getCommonGroups(self,other):
        return  [ o for o in self.string.objects if self.isWithin(o) and other.isWithin(o) ]

    def letterDistance(self,other):
        if other.leftStringPosition > self.rightStringPosition:
            return other.leftStringPosition - self.rightStringPosition
        if self.leftStringPosition > other.rightStringPosition:
            return self.leftStringPosition - other.rightStringPosition
        return 0

    def letterSpan(self):
        return self.rightStringPosition - self.leftStringPosition + 1

    def beside(self,other):
        if self.string != other.string:
            return False
        if self.leftStringPosition == other.rightStringPosition + 1:
            return True
        return other.leftStringPosition == self.rightStringPosition + 1

