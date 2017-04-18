import math
import logging
import random

import codeletMethods
import formulas
from bond import Bond
from codelet import Codelet
from correspondence import Correspondence
from description import Description
from group import Group
from rule import Rule


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
        self.runCodelets = {}
        self.postings = {}
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
        if 'description' in codeletName:
            result = (temperature.value() / 100.0) ** 2
        else:
            result = workspace.intraStringUnhappiness / 100.0
        if 'correspondence' in codeletName:
            result = workspace.interStringUnhappiness / 100.0
        if 'replacement' in codeletName:
            if workspace.numberOfUnreplacedObjects() > 0:
                return 1.0
            return 0.0
        if 'rule' in codeletName:
            if not workspace.rule:
                return 1.0
            return workspace.rule.totalWeakness() / 100.0
        if 'translator' in codeletName:
            assert False
        return result

    def howManyToPost(self, codeletName):
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
        if number < formulas.blur(2.0):
            return 1
        if number < formulas.blur(4.0):
            return 2
        return 3

    def post(self, codelet):
        self.postings[codelet.name] = self.postings.get(codelet.name, 0) + 1
        self.codelets += [codelet]
        if len(self.codelets) > 100:
            oldCodelet = self.chooseOldCodelet()
            self.removeCodelet(oldCodelet)

    def postTopDownCodelets(self):
        slipnet = self.ctx.slipnet
        for node in slipnet.slipnodes:
            #logging.info('Trying slipnode: %s' % node.get_name())
            if node.activation != 100.0:
                continue
            #logging.info('using slipnode: %s' % node.get_name())
            for codeletName in node.codelets:
                probability = self.probabilityOfPosting(codeletName)
                howMany = self.howManyToPost(codeletName)
                for _ in xrange(howMany):
                    if not formulas.coinFlip(probability):
                        continue
                    urgency = getUrgencyBin(
                        node.activation * node.conceptualDepth / 100.0)
                    codelet = Codelet(codeletName, urgency, self.codeletsRun)
                    codelet.arguments += [node]
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
        temperature = self.ctx.temperature
        probability = self.probabilityOfPosting(codeletName)
        howMany = self.howManyToPost(codeletName)
        urgency = 3
        if codeletName == 'breaker':
            urgency = 1
        if temperature.value() < 25.0 and 'translator' in codeletName:
            urgency = 5
        for _ in xrange(howMany):
            if formulas.coinFlip(probability):
                codelet = Codelet(codeletName, urgency, self.codeletsRun)
                self.post(codelet)

    def removeCodelet(self, codelet):
        self.codelets.remove(codelet)

    def newCodelet(self, name, oldCodelet, strength, arguments=None):
        #logging.debug('Posting new codelet called %s' % name)
        urgency = getUrgencyBin(strength)
        newCodelet = Codelet(name, urgency, self.codeletsRun)
        if arguments:
            newCodelet.arguments = [arguments]
        else:
            newCodelet.arguments = oldCodelet.arguments
        self.post(newCodelet)

    # pylint: disable=too-many-arguments
    def proposeRule(self, facet, description, category, relation, oldCodelet):
        """Creates a proposed rule, and posts a rule-strength-tester codelet.

        The new codelet has urgency a function of
            the degree of conceptual-depth of the descriptions in the rule
        """
        rule = Rule(facet, description, category, relation)
        rule.updateStrength()
        if description and relation:
            depths = description.conceptualDepth + relation.conceptualDepth
            depths /= 200.0
            urgency = math.sqrt(depths) * 100.0
        else:
            urgency = 0
        self.newCodelet('rule-strength-tester', oldCodelet, urgency, rule)

    def proposeCorrespondence(self, initialObject, targetObject,
                              conceptMappings, flipTargetObject, oldCodelet):
        correspondence = Correspondence(initialObject, targetObject,
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
                        oldCodelet, urgency, correspondence)

    def proposeDescription(self, objekt, type_, descriptor, oldCodelet):
        description = Description(objekt, type_, descriptor)
        descriptor.buffer = 100.0
        urgency = type_.activation
        self.newCodelet('description-strength-tester',
                        oldCodelet, urgency, description)

    def proposeSingleLetterGroup(self, source, codelet):
        slipnet = self.ctx.slipnet
        self.proposeGroup([source], [], slipnet.samenessGroup, None,
                          slipnet.letterCategory, codelet)

    def proposeGroup(self, objects, bondList, groupCategory, directionCategory,
                     bondFacet, oldCodelet):
        slipnet = self.ctx.slipnet
        bondCategory = groupCategory.getRelatedNode(slipnet.bondCategory)
        bondCategory.buffer = 100.0
        if directionCategory:
            directionCategory.buffer = 100.0
        group = Group(objects[0].string, groupCategory, directionCategory,
                      bondFacet, objects, bondList)
        urgency = bondCategory.bondDegreeOfAssociation()
        self.newCodelet('group-strength-tester', oldCodelet, urgency, group)

    def proposeBond(self, source, destination, bondCategory, bondFacet,
                    sourceDescriptor, destinationDescriptor, oldCodelet):
        bondFacet.buffer = 100.0
        sourceDescriptor.buffer = 100.0
        destinationDescriptor.buffer = 100.0
        bond = Bond(source, destination, bondCategory, bondFacet,
                    sourceDescriptor, destinationDescriptor)
        urgency = bondCategory.bondDegreeOfAssociation()
        self.newCodelet('bond-strength-tester', oldCodelet, urgency, bond)

    def chooseOldCodelet(self):
        # selects an old codelet to remove from the coderack
        # more likely to select lower urgency codelets
        if not len(self.codelets):
            return None
        urgencies = []
        for codelet in self.codelets:
            urgency = ((self.codeletsRun - codelet.birthdate) *
                       (7.5 - codelet.urgency))
            urgencies += [urgency]
        threshold = random.random() * sum(urgencies)
        sumOfUrgencies = 0.0
        for i in xrange(len(self.codelets)):
            sumOfUrgencies += urgencies[i]
            if sumOfUrgencies > threshold:
                return self.codelets[i]
        return self.codelets[0]

    def postInitialCodelets(self):
        workspace = self.ctx.workspace
        logging.info("posting initial codelets")
        codeletsToPost = [
            'bottom-up-bond-scout',
            'replacement-finder',
            'bottom-up-correspondence-scout',
        ]
        for name in codeletsToPost:
            for _ in xrange(2 * len(workspace.objects)):
                codelet = Codelet(name, 1, self.codeletsRun)
                self.post(codelet)

    def chooseAndRunCodelet(self):
        if not len(self.codelets):
            # Indeed, this happens fairly often.
            self.postInitialCodelets()
        codelet = self.chooseCodeletToRun()
        self.run(codelet)

    def chooseCodeletToRun(self):
        temperature = self.ctx.temperature
        assert self.codelets
        scale = (100.0 - temperature.value() + 10.0) / 15.0
        urgsum = sum(codelet.urgency ** scale for codelet in self.codelets)
        threshold = random.random() * urgsum
        chosen = self.codelets[0]
        urgencySum = 0.0

        for codelet in self.codelets:
            urgencySum += codelet.urgency ** scale
            if urgencySum > threshold:
                chosen = codelet
                break
        self.removeCodelet(chosen)
        logging.info('chosen codelet\n\t%s, urgency = %s',
                     chosen.name, chosen.urgency)
        return chosen

    def run(self, codelet):
        methodName = codelet.name
        self.codeletsRun += 1
        self.runCodelets[methodName] = self.runCodelets.get(methodName, 0) + 1
        method = self.methods[methodName]
        try:
            method(self.ctx, codelet)
        except AssertionError:
            pass
