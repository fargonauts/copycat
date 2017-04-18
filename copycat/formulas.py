import math
import random

from conceptMapping import ConceptMapping


def selectListPosition(probabilities):
    total = sum(probabilities)
    #logging.info('total: %s' % total)
    r = random.random()
    stopPosition = total * r
    #logging.info('stopPosition: %s' % stopPosition)
    total = 0
    i = 0
    for probability in probabilities:
        total += probability
        if total > stopPosition:
            return i
        i += 1
    return 0


def weightedAverage(values):
    total = 0.0
    totalWeights = 0.0
    for value, weight in values:
        total += value * weight
        totalWeights += weight
    if not totalWeights:
        return 0.0
    return total / totalWeights


def coinFlip(chance=0.5):
    return random.random() < chance


def blur(value):
    root = math.sqrt(value)
    if coinFlip():
        return value + root
    return value - root


def chooseRelevantDescriptionByActivation(workspaceObject):
    descriptions = workspaceObject.relevantDescriptions()
    if not descriptions:
        return None
    activations = [description.descriptor.activation
                   for description in descriptions]
    i = selectListPosition(activations)
    return descriptions[i]


def __relevantCategory(objekt, slipnode):
    return objekt.rightBond and objekt.rightBond.category == slipnode


def __relevantDirection(objekt, slipnode):
    return objekt.rightBond and objekt.rightBond.directionCategory == slipnode


def __localRelevance(string, slipnode, relevance):
    numberOfObjectsNotSpanning = numberOfMatches = 0.0
    #logging.info("find relevance for a string: %s" % string);
    for objekt in string.objects:
        if not objekt.spansString():
            #logging.info('non spanner: %s' % objekt)
            numberOfObjectsNotSpanning += 1.0
            if relevance(objekt, slipnode):
                numberOfMatches += 1.0
    if numberOfObjectsNotSpanning == 1:
        return 100.0 * numberOfMatches
    return 100.0 * numberOfMatches / (numberOfObjectsNotSpanning - 1.0)


def localBondCategoryRelevance(string, category):
    if len(string.objects) == 1:
        return 0.0
    return __localRelevance(string, category, __relevantCategory)


def localDirectionCategoryRelevance(string, direction):
    return __localRelevance(string, direction, __relevantDirection)


def getMappings(objectFromInitial, objectFromTarget,
                initialDescriptions, targetDescriptions):
    mappings = []
    for initial in initialDescriptions:
        for target in targetDescriptions:
            if initial.descriptionType == target.descriptionType:
                if  (initial.descriptor == target.descriptor or
                     initial.descriptor.slipLinked(target.descriptor)):
                    mapping = ConceptMapping(
                        initial.descriptionType,
                        target.descriptionType,
                        initial.descriptor,
                        target.descriptor,
                        objectFromInitial,
                        objectFromTarget
                    )
                    mappings += [mapping]
    return mappings
