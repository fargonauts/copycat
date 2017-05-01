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


def __localRelevance(string, isRelevant):
    numberOfObjectsNotSpanning = 0.0
    numberOfMatches = 0.0
    for o in string.objects:
        if not o.spansString():
            numberOfObjectsNotSpanning += 1.0
            if isRelevant(o):
                numberOfMatches += 1.0
    if numberOfObjectsNotSpanning == 1:
        return 100.0 * numberOfMatches
    return 100.0 * numberOfMatches / (numberOfObjectsNotSpanning - 1.0)


def localBondCategoryRelevance(string, category):
    def isRelevant(o):
        return o.rightBond and o.rightBond.category == category
    if len(string.objects) == 1:
        return 0.0
    return __localRelevance(string, isRelevant)


def localDirectionCategoryRelevance(string, direction):
    def isRelevant(o):
        return o.rightBond and o.rightBond.directionCategory == direction
    return __localRelevance(string, isRelevant)


def getMappings(objectFromInitial, objectFromTarget,
                initialDescriptions, targetDescriptions):
    mappings = []
    for initial in initialDescriptions:
        for target in targetDescriptions:
            if initial.descriptionType == target.descriptionType:
                if (initial.descriptor == target.descriptor or
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
