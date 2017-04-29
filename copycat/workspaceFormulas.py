
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


def chooseUnmodifiedObject(ctx, attribute, inObjects):
    workspace = ctx.workspace
    objects = [o for o in inObjects if o.string != workspace.modified]
    return __chooseObjectFromList(ctx, objects, attribute)


def chooseNeighbor(ctx, source):
    workspace = ctx.workspace
    objects = [o for o in workspace.objects if o.beside(source)]
    return __chooseObjectFromList(ctx, objects, "intraStringSalience")


def chooseDirectedNeighbor(ctx, source, direction):
    slipnet = ctx.slipnet
    workspace = ctx.workspace
    if direction == slipnet.left:
        objects = [o for o in workspace.objects
                   if o.string == source.string
                   and source.leftIndex == o.rightIndex + 1]
    else:
        objects = [o for o in workspace.objects
                   if o.string == source.string
                   and o.leftIndex == source.rightIndex + 1]
    return __chooseObjectFromList(ctx, objects, 'intraStringSalience')


def chooseBondFacet(ctx, source, destination):
    random = ctx.random
    slipnet = ctx.slipnet
    sourceFacets = [d.descriptionType for d in source.descriptions
                    if d.descriptionType in slipnet.bondFacets]
    bondFacets = [d.descriptionType for d in destination.descriptions
                  if d.descriptionType in sourceFacets]
    supports = [__supportForDescriptionType(ctx, f, source.string)
                for f in bondFacets]
    return random.weighted_choice(bondFacets, supports)


def __supportForDescriptionType(ctx, descriptionType, string):
    string_support = __descriptionTypeSupport(ctx, descriptionType, string)
    return (descriptionType.activation + string_support) / 2


def __descriptionTypeSupport(ctx, descriptionType, string):
    """The proportion of objects in the string with this descriptionType"""
    workspace = ctx.workspace
    described_count = 0
    total = 0
    for objekt in workspace.objects:
        if objekt.string == string:
            total += 1
            for description in objekt.descriptions:
                if description.descriptionType == descriptionType:
                    described_count += 1
    return described_count / float(total)
