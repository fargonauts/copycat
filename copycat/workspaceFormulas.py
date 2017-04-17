import logging

from workspace import workspace
from temperature import temperature
from slipnet import slipnet
import formulas


def numberOfObjects():
    return len(workspace.objects)


def chooseUnmodifiedObject(attribute, inObjects):
    objects = [o for o in inObjects if o.string != workspace.modified]
    if not len(objects):
        print 'no objects available in initial or target strings'
    return formulas.chooseObjectFromList(objects, attribute)


def chooseNeighbor(source):
    objects = []
    for objekt in workspace.objects:
        if objekt.string != source.string:
            continue
        if objekt.leftIndex == source.rightIndex + 1:
            objects += [objekt]
        elif source.leftIndex == objekt.rightIndex + 1:
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
            if source.leftIndex == o.rightIndex + 1:
                logging.info('%s is on left of %s', o, source)
                objects += [o]
            else:
                logging.info('%s is not on left of %s', o, source)
    logging.info('Number of left objects: %s', len(objects))
    return formulas.chooseObjectFromList(objects, 'intraStringSalience')


def __chooseRightNeighbor(source):
    objects = [o for o in workspace.objects
               if o.string == source.string
               and o.leftIndex == source.rightIndex + 1]
    return formulas.chooseObjectFromList(objects, 'intraStringSalience')


def chooseBondFacet(source, destination):
    sourceFacets = [d.descriptionType for d in source.descriptions
                    if d.descriptionType in slipnet.bondFacets]
    bondFacets = [d.descriptionType for d in destination.descriptions
                  if d.descriptionType in sourceFacets]
    if not bondFacets:
        return None
    supports = [__supportForDescriptionType(f, source.string)
                for f in bondFacets]
    i = formulas.selectListPosition(supports)
    return bondFacets[i]


def __supportForDescriptionType(descriptionType, string):
    string_support = __descriptionTypeSupport(descriptionType, string)
    return (descriptionType.activation + string_support) / 2


def __descriptionTypeSupport(descriptionType, string):
    """The proportion of objects in the string with this descriptionType"""
    described_count = total = 0
    for objekt in workspace.objects:
        if objekt.string == string:
            total += 1
            for description in objekt.descriptions:
                if description.descriptionType == descriptionType:
                    described_count += 1
    return described_count / float(total)


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
