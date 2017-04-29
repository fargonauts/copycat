from conceptMapping import ConceptMapping


def weightedAverage(values):
    total = 0.0
    totalWeights = 0.0
    for value, weight in values:
        total += value * weight
        totalWeights += weight
    if not totalWeights:
        return 0.0
    return total / totalWeights


def __relevantCategory(objekt, slipnode):
    return objekt.rightBond and objekt.rightBond.category == slipnode


def __relevantDirection(objekt, slipnode):
    return objekt.rightBond and objekt.rightBond.directionCategory == slipnode


def __localRelevance(string, slipnode, relevance):
    numberOfObjectsNotSpanning = 0.0
    numberOfMatches = 0.0
    for objekt in string.objects:
        if not objekt.spansString():
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
