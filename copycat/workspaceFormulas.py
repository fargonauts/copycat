import logging


def __chooseObjectFromList(ctx, objects, attribute):
    random = ctx.random
    temperature = ctx.temperature
    weights = [
        temperature.getAdjustedValue(
            getattr(o, attribute)
        )
        for o in objects
    ]
    return random.weighted_choice(objects, weights)


def chooseUnmodifiedObject(attribute, inObjects):
    from context import context as ctx
    workspace = ctx.workspace
    objects = [o for o in inObjects if o.string != workspace.modified]
    if not len(objects):
        print 'no objects available in initial or target strings'
    return __chooseObjectFromList(ctx, objects, attribute)


def chooseNeighbor(source):
    from context import context as ctx
    workspace = ctx.workspace
    objects = []
    for objekt in workspace.objects:
        if objekt.string != source.string:
            continue
        if objekt.leftIndex == source.rightIndex + 1:
            objects += [objekt]
        elif source.leftIndex == objekt.rightIndex + 1:
            objects += [objekt]
    return __chooseObjectFromList(ctx, objects, "intraStringSalience")


def chooseDirectedNeighbor(source, direction):
    from context import context as ctx
    slipnet = ctx.slipnet
    if direction == slipnet.left:
        logging.info('Left')
        return __chooseLeftNeighbor(source)
    logging.info('Right')
    return __chooseRightNeighbor(source)


def __chooseLeftNeighbor(source):
    from context import context as ctx
    workspace = ctx.workspace
    objects = []
    for o in workspace.objects:
        if o.string == source.string:
            if source.leftIndex == o.rightIndex + 1:
                logging.info('%s is on left of %s', o, source)
                objects += [o]
            else:
                logging.info('%s is not on left of %s', o, source)
    logging.info('Number of left objects: %s', len(objects))
    return __chooseObjectFromList(ctx, objects, 'intraStringSalience')


def __chooseRightNeighbor(source):
    from context import context as ctx
    workspace = ctx.workspace
    objects = [o for o in workspace.objects
               if o.string == source.string
               and o.leftIndex == source.rightIndex + 1]
    return __chooseObjectFromList(ctx, objects, 'intraStringSalience')


def chooseBondFacet(source, destination):
    from context import context as ctx
    random = ctx.random
    slipnet = ctx.slipnet
    sourceFacets = [d.descriptionType for d in source.descriptions
                    if d.descriptionType in slipnet.bondFacets]
    bondFacets = [d.descriptionType for d in destination.descriptions
                  if d.descriptionType in sourceFacets]
    supports = [__supportForDescriptionType(f, source.string)
                for f in bondFacets]
    return random.weighted_choice(bondFacets, supports)


def __supportForDescriptionType(descriptionType, string):
    string_support = __descriptionTypeSupport(descriptionType, string)
    return (descriptionType.activation + string_support) / 2


def __descriptionTypeSupport(descriptionType, string):
    """The proportion of objects in the string with this descriptionType"""
    from context import context as ctx
    workspace = ctx.workspace
    described_count = total = 0
    for objekt in workspace.objects:
        if objekt.string == string:
            total += 1
            for description in objekt.descriptions:
                if description.descriptionType == descriptionType:
                    described_count += 1
    return described_count / float(total)
