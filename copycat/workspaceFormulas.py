

def __chooseObjectFromList(ctx, objects, attribute):
    random = ctx.random
    weights = [getattr(o, attribute) for o in objects]
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
