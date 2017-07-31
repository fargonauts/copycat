import math
import logging

from . import codeletMethods
from .bond import Bond
from .codelet import Codelet
from .correspondence import Correspondence
from .description import Description
from .group import Group
from .rule import Rule


NUMBER_OF_BINS = 7


def getUrgencyBin(urgency):
    i = int(urgency) * NUMBER_OF_BINS / 100
    if i >= NUMBER_OF_BINS:
        return NUMBER_OF_BINS
    return i + 1


class Coderack(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.reset()
        self.methods = {}

        for name in dir(codeletMethods):
            method = getattr(codeletMethods, name)
            if getattr(method, 'is_codelet_method', False):
                self.methods[method.codelet_name] = method

        assert set(self.methods.keys()) == set([
            'breaker',
            'bottom-up-description-scout',
            'top-down-description-scout',
            'description-strength-tester',
            'description-builder',
            'bottom-up-bond-scout',
            'top-down-bond-scout--category',
            'top-down-bond-scout--direction',
            'bond-strength-tester',
            'bond-builder',
            'top-down-group-scout--category',
            'top-down-group-scout--direction',
            'group-scout--whole-string',
            'group-strength-tester',
            'group-builder',
            'replacement-finder',
            'rule-scout',
            'rule-strength-tester',
            'rule-builder',
            'rule-translator',
            'bottom-up-correspondence-scout',
            'important-object-correspondence-scout',
            'correspondence-strength-tester',
            'correspondence-builder',
        ])

    def reset(self):
        self.codelets = []
        self.codeletsRun = 0

    def updateCodelets(self):
        if self.codeletsRun > 0:
            self.postTopDownCodelets()
            self.postBottomUpCodelets()

    def probabilityOfPosting(self, codeletName):
        temperature = self.ctx.temperature
        workspace = self.ctx.workspace
        if codeletName == 'breaker':
            return 1.0
        if 'replacement' in codeletName:
            if workspace.numberOfUnreplacedObjects() > 0:
                return 1.0
            return 0.0
        if 'rule' in codeletName:
            if not workspace.rule:
                return 1.0
            return workspace.rule.totalWeakness() / 100.0
        if 'correspondence' in codeletName:
            return workspace.interStringUnhappiness / 100.0
        if 'description' in codeletName:
            return (temperature.value() / 100.0) ** 2
        return workspace.intraStringUnhappiness / 100.0

    def howManyToPost(self, codeletName):
        random = self.ctx.random
        workspace = self.ctx.workspace
        if codeletName == 'breaker' or 'description' in codeletName:
            return 1
        if 'translator' in codeletName:
            if not workspace.rule:
                return 0
            return 1
        if 'rule' in codeletName:
            return 2
        if 'group' in codeletName and not workspace.numberOfBonds():
            return 0
        if 'replacement' in codeletName and workspace.rule:
            return 0
        number = 0
        if 'bond' in codeletName:
            number = workspace.numberOfUnrelatedObjects()
        if 'group' in codeletName:
            number = workspace.numberOfUngroupedObjects()
        if 'replacement' in codeletName:
            number = workspace.numberOfUnreplacedObjects()
        if 'correspondence' in codeletName:
            number = workspace.numberOfUncorrespondingObjects()
        if number < random.sqrtBlur(2.0):
            return 1
        if number < random.sqrtBlur(4.0):
            return 2
        return 3

    def post(self, codelet):
        self.codelets += [codelet]
        if len(self.codelets) > 100:
            oldCodelet = self.chooseOldCodelet()
            self.removeCodelet(oldCodelet)

    def postTopDownCodelets(self):
        random = self.ctx.random
        slipnet = self.ctx.slipnet
        for node in slipnet.slipnodes:
            if node.activation != 100.0:
                continue
            for codeletName in node.codelets:
                probability = self.probabilityOfPosting(codeletName)
                howMany = self.howManyToPost(codeletName)
                for _ in range(howMany):
                    if not random.coinFlip(probability):
                        continue
                    urgency = getUrgencyBin(
                        node.activation * node.conceptualDepth / 100.0)
                    codelet = Codelet(codeletName, urgency, [node], self.codeletsRun)
                    logging.info('Post top down: %s, with urgency: %d',
                                 codelet.name, urgency)
                    self.post(codelet)

    def postBottomUpCodelets(self):
        logging.info("posting bottom up codelets")
        self.__postBottomUpCodelets('bottom-up-description-scout')
        self.__postBottomUpCodelets('bottom-up-bond-scout')
        self.__postBottomUpCodelets('group-scout--whole-string')
        self.__postBottomUpCodelets('bottom-up-correspondence-scout')
        self.__postBottomUpCodelets('important-object-correspondence-scout')
        self.__postBottomUpCodelets('replacement-finder')
        self.__postBottomUpCodelets('rule-scout')
        self.__postBottomUpCodelets('rule-translator')
        self.__postBottomUpCodelets('breaker')

    def __postBottomUpCodelets(self, codeletName):
        random = self.ctx.random
        temperature = self.ctx.temperature
        probability = self.probabilityOfPosting(codeletName)
        howMany = self.howManyToPost(codeletName)
        urgency = 3
        if codeletName == 'breaker':
            urgency = 1
        if temperature.value() < 25.0 and 'translator' in codeletName:
            urgency = 5
        for _ in range(howMany):
            if random.coinFlip(probability):
                codelet = Codelet(codeletName, urgency, [], self.codeletsRun)
                self.post(codelet)

    def removeCodelet(self, codelet):
        self.codelets.remove(codelet)

    def newCodelet(self, name, strength, arguments):
        urgency = getUrgencyBin(strength)
        newCodelet = Codelet(name, urgency, arguments, self.codeletsRun)
        self.post(newCodelet)

    # pylint: disable=too-many-arguments
    def proposeRule(self, facet, description, category, relation):
        """Creates a proposed rule, and posts a rule-strength-tester codelet.

        The new codelet has urgency a function of
            the degree of conceptual-depth of the descriptions in the rule
        """
        rule = Rule(self.ctx, facet, description, category, relation)
        rule.updateStrength()
        if description and relation:
            averageDepth = (description.conceptualDepth + relation.conceptualDepth) / 2.0
            urgency = 100.0 * math.sqrt(averageDepth / 100.0)
        else:
            urgency = 0
        self.newCodelet('rule-strength-tester', urgency, [rule])

    def proposeCorrespondence(self, initialObject, targetObject,
                              conceptMappings, flipTargetObject):
        correspondence = Correspondence(self.ctx, initialObject, targetObject,
                                        conceptMappings, flipTargetObject)
        for mapping in conceptMappings:
            mapping.initialDescriptionType.buffer = 100.0
            mapping.initialDescriptor.buffer = 100.0
            mapping.targetDescriptionType.buffer = 100.0
            mapping.targetDescriptor.buffer = 100.0
        mappings = correspondence.distinguishingConceptMappings()
        urgency = sum(mapping.strength() for mapping in mappings)
        numberOfMappings = len(mappings)
        if urgency:
            urgency /= numberOfMappings
        binn = getUrgencyBin(urgency)
        logging.info('urgency: %s, number: %d, bin: %d',
                     urgency, numberOfMappings, binn)
        self.newCodelet('correspondence-strength-tester',
                        urgency, [correspondence])

    def proposeDescription(self, objekt, type_, descriptor):
        description = Description(objekt, type_, descriptor)
        descriptor.buffer = 100.0
        urgency = type_.activation
        self.newCodelet('description-strength-tester',
                        urgency, [description])

    def proposeSingleLetterGroup(self, source):
        slipnet = self.ctx.slipnet
        self.proposeGroup([source], [], slipnet.samenessGroup, None,
                          slipnet.letterCategory)

    def proposeGroup(self, objects, bondList, groupCategory, directionCategory,
                     bondFacet):
        slipnet = self.ctx.slipnet
        bondCategory = groupCategory.getRelatedNode(slipnet.bondCategory)
        bondCategory.buffer = 100.0
        if directionCategory:
            directionCategory.buffer = 100.0
        group = Group(objects[0].string, groupCategory, directionCategory,
                      bondFacet, objects, bondList)
        urgency = bondCategory.bondDegreeOfAssociation()
        self.newCodelet('group-strength-tester', urgency, [group])

    def proposeBond(self, source, destination, bondCategory, bondFacet,
                    sourceDescriptor, destinationDescriptor):
        bondFacet.buffer = 100.0
        sourceDescriptor.buffer = 100.0
        destinationDescriptor.buffer = 100.0
        bond = Bond(self.ctx, source, destination, bondCategory, bondFacet,
                    sourceDescriptor, destinationDescriptor)
        urgency = bondCategory.bondDegreeOfAssociation()
        self.newCodelet('bond-strength-tester', urgency, [bond])

    def chooseOldCodelet(self):
        # selects an old codelet to remove from the coderack
        # more likely to select lower urgency codelets
        urgencies = []
        for codelet in self.codelets:
            urgency = ((self.codeletsRun - codelet.birthdate) *
                       (7.5 - codelet.urgency))
            urgencies += [urgency]
        random = self.ctx.random
        return random.weighted_choice(self.codelets, urgencies)

    def postInitialCodelets(self):
        workspace = self.ctx.workspace
        n = len(workspace.objects)
        if n == 0:
            # The most pathological case.
            codeletsToPost = [
                ('rule-scout', 1),
            ]
        else:
            codeletsToPost = [
                ('bottom-up-bond-scout', 2 * n),
                ('replacement-finder', 2 * n),
                ('bottom-up-correspondence-scout', 2 * n),
            ]
        for name, count in codeletsToPost:
            for _ in range(count):
                codelet = Codelet(name, 1, [], self.codeletsRun)
                self.post(codelet)

    def chooseAndRunCodelet(self):
        if not len(self.codelets):
            # Indeed, this happens fairly often.
            self.postInitialCodelets()
        codelet = self.chooseCodeletToRun()
        self.run(codelet)

    def chooseCodeletToRun(self):
        random = self.ctx.random
        temperature = self.ctx.temperature
        assert self.codelets
        scale = (100.0 - temperature.value() + 10.0) / 15.0
        chosen = random.weighted_choice(self.codelets, [codelet.urgency ** scale for codelet in self.codelets])
        self.removeCodelet(chosen)
        return chosen

    def run(self, codelet):
        methodName = codelet.name
        self.codeletsRun += 1
        method = self.methods[methodName]
        try:
            method(self.ctx, codelet)
        except AssertionError:
            pass
