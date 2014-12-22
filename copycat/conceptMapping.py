import logging
from slipnet import slipnet


class ConceptMapping(object):
    def __init__(self, initialDescriptionType, targetDescriptionType,
                 initialDescriptor, targetDescriptor,
                 initialObject, targetObject):
        logging.info('make a map: %s-%s' % (initialDescriptionType.get_name(),
                                            targetDescriptionType.get_name()))
        self.initialDescriptionType = initialDescriptionType
        self.targetDescriptionType = targetDescriptionType
        self.initialDescriptor = initialDescriptor
        self.targetDescriptor = targetDescriptor
        self.initialObject = initialObject
        self.targetObject = targetObject
        self.label = initialDescriptor.getBondCategory(targetDescriptor)

    def __repr__(self):
        return '<ConceptMapping: %s from %s to %s>' % (
            self.__str__(), self.initialDescriptor, self.targetDescriptor)

    def __str__(self):
        return self.label and self.label.name or 'anonymous'

    def slipability(self):
        association = self.__degreeOfAssociation()
        if association == 100.0:
            return 100.0
        depth = self.__conceptualDepth() / 100.0
        return association * (1 - depth * depth)

    def __degreeOfAssociation(self):
        # Assumes the 2 descriptors are connected in the slipnet by <= 1 link
        if self.initialDescriptor == self.targetDescriptor:
            return 100.0
        for link in self.initialDescriptor.lateralSlipLinks:
            if link.destination == self.targetDescriptor:
                return link.degreeOfAssociation()
        return 0.0

    def strength(self):
        association = self.__degreeOfAssociation()
        if association == 100.0:
            return 100.0
        depth = self.__conceptualDepth() / 100.0
        return association * (1 + depth * depth)

    def __conceptualDepth(self):
        return (self.initialDescriptor.conceptualDepth +
                self.targetDescriptor.conceptualDepth) / 2.0

    def distinguishing(self):
        if self.initialDescriptor == slipnet.whole:
            if self.targetDescriptor == slipnet.whole:
                return False
        if not self.initialObject.distinguishingDescriptor(
                self.initialDescriptor):
            return False
        return self.targetObject.distinguishingDescriptor(
            self.targetDescriptor)

    def sameInitialType(self, other):
        return self.initialDescriptionType == other.initialDescriptionType

    def sameTargetType(self, other):
        return self.targetDescriptionType == other.targetDescriptionType

    def sameTypes(self, other):
        return self.sameInitialType(other) and self.sameTargetType(other)

    def sameInitialDescriptor(self, other):
        return self.initialDescriptor == other.initialDescriptor

    def sameTargetDescriptor(self, other):
        return self.targetDescriptor == other.targetDescriptor

    def sameDescriptors(self, other):
        if self.sameInitialDescriptor(other):
            return self.sameTargetDescriptor(other)

    def sameKind(self, other):
        return self.sameTypes(other) and self.sameDescriptors(other)

    def nearlySameKind(self, other):
        return self.sameTypes(other) and self.sameInitialDescriptor(other)

    def isContainedBy(self, mappings):
        return any([self.sameKind(mapping) for mapping in mappings])

    def isNearlyContainedBy(self, mappings):
        return any([self.nearlySameKind(mapping) for mapping in mappings])

    def related(self, other):
        if self.initialDescriptor.related(other.initialDescriptor):
            return True
        return self.targetDescriptor.related(other.targetDescriptor)

    def incompatible(self, other):
        # Concept-mappings (a -> b) and (c -> d) are incompatible if a is
        # related to c or if b is related to d, and the a -> b relationship is
        # different from the c -> d relationship. E.g., rightmost -> leftmost
        # is incompatible with right -> right, since rightmost is linked
        # to right, but the relationships (opposite and identity) are different
        # Notice that slipnet distances are not looked at, only slipnet links.
        # This should be changed eventually.
        if not self.related(other):
            return False
        if not self.label or not other.label:
            return False
        return self.label != other.label

    def supports(self, other):
        # Concept-mappings (a -> b) and (c -> d) support each other if a is
        # related to c and if b is related to d and the a -> b relationship is
        # the same as the c -> d relationship.  E.g., rightmost -> rightmost
        # supports right -> right and leftmost -> leftmost.
        # Notice that slipnet distances are not looked at, only slipnet links.
        # This should be changed eventually.

        # If the two concept-mappings are the same, then return t.  This
        # means that letter->group supports letter->group, even though these
        # concept-mappings have no label.

        if self.initialDescriptor == other.initialDescriptor:
            if self.targetDescriptor == other.targetDescriptor:
                return True
        # if the descriptors are not related return false
        if not self.related(other):
            return False
        if not self.label or not other.label:
            return False
        return self.label == other.label

    def relevant(self):
        if self.initialDescriptionType.fully_active():
            return self.targetDescriptionType.fully_active()

    def slippage(self):
        if self.label != slipnet.sameness:
            return self.label != slipnet.identity

    def symmetricVersion(self):
        if not self.slippage():
            return self
        bond = self.targetDescriptor.getBondCategory(self.initialDescriptor)
        if bond == self.label:
            return self
        return ConceptMapping(
            self.targetDescriptionType,
            self.initialDescriptionType,
            self.targetDescriptor,
            self.initialDescriptor1,
            self.initialObject,
            self.targetObject
        )
