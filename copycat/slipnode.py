import math
import logging
import random


def full_activation():
    return 100


def jump_threshold():
    return 55.0


class Slipnode(object):
    def __init__(self, name, depth, length=0.0):
    #       logging.info('depth to %s for %s' % (depth,name))
        self.conceptualDepth = depth
        self.usualConceptualDepth = depth
        self.name = name
        self.intrinsicLinkLength = length
        self.shrunkLinkLength = length * 0.4

        self.activation = 0.0
        self.buffer = 0.0
        self.clamped = False
        self.bondFacetFactor = 0.0
        self.categoryLinks = []
        self.instanceLinks = []
        self.propertyLinks = []
        self.lateralSlipLinks = []
        self.lateralNonSlipLinks = []
        self.incomingLinks = []
        self.outgoingLinks = []
        self.codelets = []
        self.clampBondDegreeOfAssociation = False

    def __repr__(self):
        return '<Slipnode: %s>' % self.name

    def reset(self):
        self.buffer = 0.0
        self.activation = 0.0

    def clampHigh(self):
        self.clamped = True
        self.activation = 100.0

    def unclamp(self):
        self.clamped = False

    def setConceptualDepth(self, depth):
        logging.info('set depth to %s for %s' % (depth, self.name))
        self.conceptualDepth = depth

    def category(self):
        if not len(self.categoryLinks):
            return None
        link = self.categoryLinks[0]
        return link.destination

    def fully_active(self):
        """Whether this node has full activation"""
        return self.activation > full_activation() - 0.00001  # allow a little leeway for floats

    def activate_fully(self):
        """Make this node fully active"""
        self.activation = full_activation()

    def bondDegreeOfAssociation(self):
        linkLength = self.intrinsicLinkLength
        if (not self.clampBondDegreeOfAssociation) and self.fully_active():
            linkLength = self.shrunkLinkLength
        result = math.sqrt(100 - linkLength) * 11.0
        return min(100.0, result)

    def degreeOfAssociation(self):
        linkLength = self.intrinsicLinkLength
        if self.fully_active():
            linkLength = self.shrunkLinkLength
        return 100.0 - linkLength

    def update(self):
        act = self.activation
        self.oldActivation = act
        self.buffer -= self.activation * (100.0 - self.conceptualDepth) / 100.0

    def linked(self, other):
        """Whether the other is among the outgoing links"""
        return self.points_at(self.outgoingLinks, other)

    def slipLinked(self, other):
        """Whether the other is among the lateral links"""
        return self.points_at(self.lateralSlipLinks, other)

    def points_at(self, links, other):
        """Whether any of the links points at the other"""
        return any([l.points_at(other) for l in links])

    def related(self, other):
        """Same or linked"""
        return self == other or self.linked(other)

    def applySlippages(self, slippages):
        for slippage in slippages:
            if self == slippage.initialDescriptor:
                return slippage.targetDescriptor
        return self

    def getRelatedNode(self, relation):
        """Return the node that is linked to this node via this relation.

        If no linked node is found, return None
        """
        from slipnet import slipnet

        if relation == slipnet.identity:
            return self
        destinations = [l.destination for l in self.outgoingLinks if l.label == relation]
        if destinations:
            return destinations[0]
        node = None
        return node

    def getBondCategory(self, destination):
        """Return the label of the link between these nodes if it exists.

        If it does not exist return None
        """
        from slipnet import slipnet

        result = None
        if self == destination:
            result = slipnet.identity
        else:
            for link in self.outgoingLinks:
                if link.destination == destination:
                    result = link.label
                    break
        if result:
            logging.info('Got bond: %s' % result.name)
        else:
            logging.info('Got no bond')
        return result

    def spread_activation(self):
        if self.fully_active():
            [link.spread_activation() for link in self.outgoingLinks]

    def addBuffer(self):
        if not self.clamped:
            self.activation += self.buffer
        self.activation = min(self.activation, 100)
        self.activation = max(self.activation, 0)

    def jump(self):
        value = (self.activation / 100.0) ** 3
        #logging.info('jumping for %s at activation %s' % (self.name,self.activation))
        if self.activation > jump_threshold() and random.random() < value and not self.clamped:
            self.activate_fully()

    def get_name(self):
        if len(self.name) == 1:
            return self.name.upper()
        return self.name
