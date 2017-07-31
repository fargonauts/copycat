import logging


from .workspaceStructure import WorkspaceStructure
from . import formulas


class Rule(WorkspaceStructure):
    def __init__(self, ctx, facet, descriptor, category, relation):
        WorkspaceStructure.__init__(self, ctx)
        self.facet = facet
        self.descriptor = descriptor
        self.category = category
        self.relation = relation

    def __str__(self):
        if not self.facet:
            return 'Empty rule'
        return 'replace %s of %s %s by %s' % (
            self.facet.name, self.descriptor.name,
            self.category.name, self.relation.name)

    def updateExternalStrength(self):
        self.externalStrength = self.internalStrength

    def updateInternalStrength(self):
        workspace = self.ctx.workspace
        if not (self.descriptor and self.relation):
            self.internalStrength = 50.0
            return
        averageDepth = (self.descriptor.conceptualDepth +
                        self.relation.conceptualDepth) / 2.0
        averageDepth **= 1.1
        # see if the object corresponds to an object
        # if so, see if the descriptor is present (modulo slippages) in the
        # corresponding object
        changedObjects = [o for o in workspace.initial.objects if o.changed]
        changed = changedObjects[0]
        sharedDescriptorTerm = 0.0
        if changed and changed.correspondence:
            targetObject = changed.correspondence.objectFromTarget
            slippages = workspace.slippages()
            slipnode = self.descriptor.applySlippages(slippages)
            if not targetObject.described(slipnode):
                self.internalStrength = 0.0
                return
            sharedDescriptorTerm = 100.0
        conceptual_height = (100.0 - self.descriptor.conceptualDepth) / 10.0
        sharedDescriptorWeight = conceptual_height ** 1.4
        depthDifference = 100.0 - abs(self.descriptor.conceptualDepth -
                                      self.relation.conceptualDepth)
        weights = ((depthDifference, 12),
                   (averageDepth, 18),
                   (sharedDescriptorTerm, sharedDescriptorWeight))
        self.internalStrength = formulas.weightedAverage(weights)
        if self.internalStrength > 100.0:
            self.internalStrength = 100.0

    def ruleEqual(self, other):
        if not other:
            return False
        if self.relation != other.relation:
            return False
        if self.facet != other.facet:
            return False
        if self.category != other.category:
            return False
        if self.descriptor != other.descriptor:
            return False
        return True

    def activateRuleDescriptions(self):
        if self.relation:
            self.relation.buffer = 100.0
        if self.facet:
            self.facet.buffer = 100.0
        if self.category:
            self.category.buffer = 100.0
        if self.descriptor:
            self.descriptor.buffer = 100.0

    def incompatibleRuleCorrespondence(self, correspondence):
        workspace = self.ctx.workspace
        if not correspondence:
            return False
        # find changed object
        changeds = [o for o in workspace.initial.objects if o.changed]
        if not changeds:
            return False
        changed = changeds[0]
        if correspondence.objectFromInitial != changed:
            return False
        # it is incompatible if the rule descriptor is not in the mapping list
        return any(m.initialDescriptor == self.descriptor
                   for m in correspondence.conceptMappings)

    def __changeString(self, string):
        slipnet = self.ctx.slipnet
        # applies the changes to self string ie. successor
        if self.facet == slipnet.length:
            if self.relation == slipnet.predecessor:
                return string[:-1]
            elif self.relation == slipnet.successor:
                # This seems to be happening at the wrong level of abstraction.
                # "Lengthening" is not an operation that makes sense on strings;
                # it makes sense only on *groups*, and here we've lost the
                # "groupiness" of this string. What gives?
                return string + string[0]
            return string
        # apply character changes
        if self.relation == slipnet.predecessor:
            if 'a' in string:
                return None
            return ''.join(chr(ord(c) - 1) for c in string)
        elif self.relation == slipnet.successor:
            if 'z' in string:
                return None
            return ''.join(chr(ord(c) + 1) for c in string)
        else:
            return self.relation.name.lower()

    def buildTranslatedRule(self):
        workspace = self.ctx.workspace
        if not (self.descriptor and self.relation):
            return workspace.targetString
        slippages = workspace.slippages()
        self.category = self.category.applySlippages(slippages)
        self.facet = self.facet.applySlippages(slippages)
        self.descriptor = self.descriptor.applySlippages(slippages)
        self.relation = self.relation.applySlippages(slippages)
        # generate the final string
        changeds = [o for o in workspace.target.objects if
                    o.described(self.descriptor) and
                    o.described(self.category)]
        if len(changeds) == 0:
            return workspace.targetString
        elif len(changeds) > 1:
            logging.info("More than one letter changed. Sorry, I can't solve problems like this right now.")
            return None
        else:
            changed = changeds[0]
            logging.debug('changed object = %s', changed)
            left = changed.leftIndex - 1
            right = changed.rightIndex
            s = workspace.targetString
            changed_middle = self.__changeString(s[left:right])
            if changed_middle is None:
                return None
            return s[:left] + changed_middle + s[right:]
