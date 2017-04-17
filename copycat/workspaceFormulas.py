import logging

from workspace import workspace
from slipnet import slipnet
import formulas


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
