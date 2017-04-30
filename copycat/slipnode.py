import math


def jump_threshold():
    return 55.0


class Slipnode(object):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, slipnet, name, depth, length=0.0):
        self.slipnet = slipnet
        self.name = name
        self.conceptualDepth = depth
        self.intrinsicLinkLength = length
        self.shrunkLinkLength = length * 0.4

        self.activation = 0.0
        self.buffer = 0.0
        self.clamped = False
        self.categoryLinks = []
        self.instanceLinks = []
        self.propertyLinks = []
        self.lateralSlipLinks = []
        self.lateralNonSlipLinks = []
        self.incomingLinks = []
        self.outgoingLinks = []
        self.codelets = []

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

    def unclamped(self):
        return not self.clamped

    def category(self):
        if not len(self.categoryLinks):
            return None
        link = self.categoryLinks[0]
        return link.destination

    def fully_active(self):
        """Whether this node has full activation"""
        float_margin = 0.00001
        return self.activation > 100.0 - float_margin

    def bondDegreeOfAssociation(self):
        linkLength = self.intrinsicLinkLength
        if self.fully_active():
            linkLength = self.shrunkLinkLength
        result = math.sqrt(100 - linkLength) * 11.0
        return min(100.0, result)

    def degreeOfAssociation(self):
        linkLength = self.intrinsicLinkLength
        if self.fully_active():
            linkLength = self.shrunkLinkLength
        return 100.0 - linkLength

    def linked(self, other):
        """Whether the other is among the outgoing links"""
        return any(l.points_at(other) for l in self.outgoingLinks)

    def slipLinked(self, other):
        """Whether the other is among the lateral links"""
        return any(l.points_at(other) for l in self.lateralSlipLinks)

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
        slipnet = self.slipnet
        if relation == slipnet.identity:
            return self
        destinations = [l.destination
                        for l in self.outgoingLinks if l.label == relation]
        if destinations:
            return destinations[0]
        return None

    def getBondCategory(self, destination):
        """Return the label of the link between these nodes if it exists.

        If it does not exist return None
        """
        slipnet = self.slipnet
        if self == destination:
            return slipnet.identity
        else:
            for link in self.outgoingLinks:
                if link.destination == destination:
                    return link.label
        return None

    def update(self):
        self.oldActivation = self.activation
        self.buffer -= self.activation * (100.0 - self.conceptualDepth) / 100.0

    def spread_activation(self):
        if self.fully_active():
            for link in self.outgoingLinks:
                link.spread_activation()

    def addBuffer(self):
        if self.unclamped():
            self.activation += self.buffer
        self.activation = min(max(0, self.activation), 100)

    def jump(self, random):
        if self.clamped or self.activation <= jump_threshold():
            return
        value = (self.activation / 100.0) ** 3
        if random.coinFlip(value):
            self.activation = 100.0

    def get_name(self):
        if len(self.name) == 1:
            return self.name.upper()
        return self.name
