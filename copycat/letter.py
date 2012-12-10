from workspaceObject import WorkspaceObject
from slipnet import slipnet


class Letter(WorkspaceObject):
    def __init__(self, string, position, length):
        WorkspaceObject.__init__(self, string)
        from workspace import workspace
        workspace.objects += [self]
        string.objects += [self]
        self.leftStringPosition = position
        self.leftmost = self.leftStringPosition == 1
        self.rightStringPosition = position
        self.rightmost = self.rightStringPosition == length

    def describe(self, position, length):
        if length == 1:
            self.addDescription(slipnet.stringPositionCategory, slipnet.single)
        if self.leftmost and length > 1:  # ? why check length ?
            self.addDescription(slipnet.stringPositionCategory, slipnet.leftmost)
        if self.rightmost and length > 1:  # ? why check length ?
            self.addDescription(slipnet.stringPositionCategory, slipnet.rightmost)
        if length > 2 and position * 2 == length + 1:
            self.addDescription(slipnet.stringPositionCategory, slipnet.middle)

    def __repr__(self):
        return '<Letter: %s>' % self.__str__()

    def __str__(self):
        if not self.string:
            return ''
        i = self.leftStringPosition - 1
        if len(self.string) <= i:
            raise ValueError('len(self.string) <= self.leftStringPosition :: %d <= %d' % (len(self.string), self.leftStringPosition))
        return self.string[i]

    def distinguishingDescriptor(self, descriptor):
        """Whether no other object of the same type (letter) has the same descriptor"""
        if not WorkspaceObject.distinguishingDescriptor(self, descriptor):
            return False
        for objekt in self.string.objects:
            # check to see if they are of the same type
            if isinstance(objekt, Letter) and objekt != self:
                # check all descriptions for the descriptor
                for description in objekt.descriptions:
                    if description.descriptor == descriptor:
                        return False
        return True
