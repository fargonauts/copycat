import logging

from workspace import workspace
from temperature import temperature
from slipnet import slipnet
import formulas


class WorkspaceFormulas(object):
    def __init__(self):
        self.clampTemperature = False

    def updateTemperature(self):
        logging.debug('updateTemperature')
        workspace.assessTemperature()
        ruleWeakness = 100.0
        if workspace.rule:
            workspace.rule.updateStrength()
            ruleWeakness = 100.0 - workspace.rule.totalStrength
        values = ((workspace.totalUnhappiness, 0.8), (ruleWeakness, 0.2))
        slightly_above_actual_temperature = formulas.actualTemperature + 0.001
        logging.info('actualTemperature: %f' % slightly_above_actual_temperature)
        formulas.actualTemperature = formulas.weightedAverage(values)
        logging.info('unhappiness: %f, weakness: %f, actualTemperature: %f' % (
        workspace.totalUnhappiness + 0.001, ruleWeakness + 0.001, formulas.actualTemperature + 0.001))
        if temperature.clamped:
            formulas.actualTemperature = 100.0
        logging.info('actualTemperature: %f' % (formulas.actualTemperature + 0.001))
        temperature.update(formulas.actualTemperature)
        if not self.clampTemperature:
            formulas.Temperature = formulas.actualTemperature
        temperature.update(formulas.Temperature)

workspaceFormulas = WorkspaceFormulas()


def numberOfObjects():
    return len(workspace.objects)


def chooseUnmodifiedObject(attribute, inObjects):
    objects = [o for o in inObjects if o.string != workspace.modified]
    if not len(objects):
        print 'no objects available in initial or target strings'
    return formulas.chooseObjectFromList(objects, attribute)


def chooseNeighbour(source):
    objects = []
    for objekt in workspace.objects:
        if objekt.string != source.string:
            continue
        if objekt.leftStringPosition == source.rightStringPosition + 1:
            objects += [objekt]
        elif source.leftStringPosition == objekt.rightStringPosition + 1:
            objects += [objekt]
    return formulas.chooseObjectFromList(objects, "intraStringSalience")


def chooseDirectedNeighbor(source, direction):
    if direction == slipnet.left:
        logging.info('Left')
        return __chooseLeftNeighbor(source)
    logging.info('Right')
    return __chooseRightNeighbor(source)


def __chooseLeftNeighbor(source):
    objects = []
    for o in workspace.objects:
        if o.string == source.string:
            if source.leftStringPosition == o.rightStringPosition + 1:
                logging.info('%s is on left of %s' % (o, source))
                objects += [o]
            else:
                logging.info('%s is not on left of %s' % (o, source))
    logging.info('Number of left objects: %s' % len(objects))
    return formulas.chooseObjectFromList(objects, 'intraStringSalience')


def __chooseRightNeighbor(source):
    objects = [o for o in workspace.objects if
        o.string == source.string and
        o.leftStringPosition == source.rightStringPosition + 1
    ]
    return formulas.chooseObjectFromList(objects, 'intraStringSalience')


def chooseBondFacet(source, destination):
    sourceFacets = [d.descriptionType for d in source.descriptions if d.descriptionType in slipnet.bondFacets]
    bondFacets = [d.descriptionType for d in destination.descriptions if d.descriptionType in sourceFacets]
    if not bondFacets:
        return None
    supports = [__supportForDescriptionType(f, source.string) for f in bondFacets]
    i = formulas.selectListPosition(supports)
    return bondFacets[i]


def __supportForDescriptionType(descriptionType, string):
    return (descriptionType.activation + __descriptionTypeSupport(descriptionType, string)) / 2


def __descriptionTypeSupport(descriptionType, string):
    """The proportion of objects in the string that have a description with this descriptionType"""
    numberOfObjects = totalNumberOfObjects = 0.0
    for objekt in workspace.objects:
        if objekt.string == string:
            totalNumberOfObjects += 1.0
            for description in objekt.descriptions:
                if description.descriptionType == descriptionType:
                    numberOfObjects += 1.0
    return numberOfObjects / totalNumberOfObjects


def probabilityOfPosting(codeletName):
    if codeletName == 'breaker':
        return 1.0
    if 'description' in codeletName:
        result = (formulas.Temperature / 100.0) ** 2
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
        if not workspace.rule:
            assert 0
            return 0.0
        assert 0
        return 1.0
    return result


def howManyToPost(codeletName):
    if codeletName == 'breaker':
        return 1
    if 'description' in codeletName:
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
#       print 'post number of unrelated: %d, objects: %d' % (number,len(workspace.objects))
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
