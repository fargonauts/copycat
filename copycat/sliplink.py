#from slipnode import Slipnode


class Sliplink(object):
    def __init__(self, source, destination, label=None, length=0.0):
        self.source = source
        self.destination = destination
        self.label = label
        self.fixedLength = length
        source.outgoingLinks += [self]
        destination.incomingLinks += [self]

    def degreeOfAssociation(self):
        if self.fixedLength > 0 or not self.label:
            return 100.0 - self.fixedLength
        return self.label.degreeOfAssociation()

    def intrinsicDegreeOfAssociation(self):
        if self.fixedLength > 1:
            return 100.0 - self.fixedLength
        if self.label:
            return 100.0 - self.label.intrinsicLinkLength
        return 0.0

    def spread_activation(self):
        self.destination.buffer += self.intrinsicDegreeOfAssociation()

    def points_at(self, other):
        return self.destination == other
