import inspect
import logging

from . import formulas
from .workspaceFormulas import chooseDirectedNeighbor
from .workspaceFormulas import chooseNeighbor
from .workspaceFormulas import chooseUnmodifiedObject
from .workspaceObject import WorkspaceObject
from .letter import Letter
from .replacement import Replacement
from .group import Group
from .bond import Bond
from .correspondence import Correspondence


def codelet(name):
    """Decorator for otherwise-unused functions that are in fact used as codelet behaviors"""
    def wrap(f):
        assert tuple(inspect.getargspec(f)) == (['ctx', 'codelet'], None, None, None)
        f.is_codelet_method = True
        f.codelet_name = name
        return f
    return wrap


# some methods common to the codelets
def __showWhichStringObjectIsFrom(structure):
    if not structure:
        return
    workspace = structure.ctx.workspace
    whence = 'other'
    if isinstance(structure, WorkspaceObject):
        whence = 'target'
        if structure.string == workspace.initial:
            whence = 'initial'
    logging.info('object chosen = %s from %s string' % (structure, whence))


def __getScoutSource(ctx, slipnode, relevanceMethod, typeName):
    random = ctx.random
    workspace = ctx.workspace
    initialRelevance = relevanceMethod(workspace.initial, slipnode)
    targetRelevance = relevanceMethod(workspace.target, slipnode)
    initialUnhappiness = workspace.initial.intraStringUnhappiness
    targetUnhappiness = workspace.target.intraStringUnhappiness
    logging.info('initial : relevance = %d, unhappiness=%d',
                 initialRelevance, int(initialUnhappiness))
    logging.info('target : relevance = %d, unhappiness=%d',
                 targetRelevance, int(targetUnhappiness))
    string = workspace.initial
    initials = initialRelevance + initialUnhappiness
    targets = targetRelevance + targetUnhappiness
    if random.weighted_greater_than(targets, initials):
        string = workspace.target
        logging.info('target string selected: %s for %s',
                     workspace.target, typeName)
    else:
        logging.info('initial string selected: %s for %s',
                     workspace.initial, typeName)
    source = chooseUnmodifiedObject(ctx, 'intraStringSalience', string.objects)
    return source


def __getDescriptors(bondFacet, source, destination):
    sourceDescriptor = source.getDescriptor(bondFacet)
    destinationDescriptor = destination.getDescriptor(bondFacet)
    assert sourceDescriptor and destinationDescriptor
    return sourceDescriptor, destinationDescriptor


def __structureVsStructure(structure1, weight1, structure2, weight2):
    """Return true if the first structure comes out stronger than the second."""
    ctx = structure1.ctx
    random = ctx.random
    structure1.updateStrength()
    structure2.updateStrength()
    # TODO: use entropy
    weightedStrength1 = structure1.totalStrength * weight1
    # TODO: use entropy
    weightedStrength2 = structure2.totalStrength * weight2
    return random.weighted_greater_than(weightedStrength1, weightedStrength2)

def __fight(structure, structureWeight, incompatibles, incompatibleWeight):
    if not (incompatibles and len(incompatibles)):
        return True
    for incompatible in incompatibles:
        if not __structureVsStructure(structure, structureWeight,
                                      incompatible, incompatibleWeight):
            logging.info('lost fight with %s', incompatible)
            return False
        logging.info('won fight with %s', incompatible)
    return True


def __fightIncompatibles(incompatibles, structure, name,
                         structureWeight, incompatibleWeight):
    if len(incompatibles):
        if __fight(structure, structureWeight,
                   incompatibles, incompatibleWeight):
            logging.info('broke the %s', name)
            return True
        logging.info('failed to break %s: Fizzle', name)
        return False
    logging.info('no incompatible %s', name)
    return True

def __slippability(ctx, conceptMappings):
    random = ctx.random
    for mapping in conceptMappings:
        slippiness = mapping.slippability() / 100.0
        # TODO: use entropy
        probabilityOfSlippage = slippiness
        if random.coinFlip(probabilityOfSlippage):
            return True
    return False


@codelet('breaker')
def breaker(ctx, codelet):
    random = ctx.random
    workspace = ctx.workspace
    # choose a structure at random
    structures = [s for s in workspace.structures if
                  isinstance(s, (Group, Bond, Correspondence))]
    assert len(structures)
    structure = random.choice(structures)
    __showWhichStringObjectIsFrom(structure)
    breakObjects = [structure]
    if isinstance(structure, Bond):
        if structure.source.group:
            if structure.source.group == structure.destination.group:
                breakObjects += [structure.source.group]
    # Break all the objects or none of them; this matches the Java
    for structure in breakObjects:
        # TODO: use entropy
        breakProbability = structure.totalStrength / 100.0
        if random.coinFlip(breakProbability):
            return
    for structure in breakObjects:
        structure.break_the_structure()

def chooseRelevantDescriptionByActivation(ctx, workspaceObject):
    random = ctx.random
    descriptions = workspaceObject.relevantDescriptions()
    weights = [description.descriptor.activation for description in descriptions]
    return random.weighted_choice(descriptions, weights)

def similarPropertyLinks(ctx, slip_node):
    random = ctx.random
    result = []
    for slip_link in slip_node.propertyLinks:
        association = slip_link.degreeOfAssociation() / 100.0
        # TODO:use entropy
        probability = association
        if random.coinFlip(probability):
            result += [slip_link]
    return result


@codelet('bottom-up-description-scout')
def bottom_up_description_scout(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    workspace = ctx.workspace
    chosenObject = chooseUnmodifiedObject(ctx, 'totalSalience', workspace.objects)
    assert chosenObject
    __showWhichStringObjectIsFrom(chosenObject)
    # choose relevant description by activation
    descriptions = chosenObject.relevantDescriptions()
    weights = [d.descriptor.activation for d in descriptions]
    description = random.weighted_choice(descriptions, weights)
    assert description
    sliplinks = similarPropertyLinks(ctx, description.descriptor)
    assert sliplinks
    weights = [sliplink.degreeOfAssociation() * sliplink.destination.activation
               for sliplink in sliplinks]
    chosen = random.weighted_choice(sliplinks, weights)
    chosenProperty = chosen.destination
    coderack.proposeDescription(chosenObject, chosenProperty.category(),
                                chosenProperty)


@codelet('top-down-description-scout')
def top_down_description_scout(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    workspace = ctx.workspace
    descriptionType = codelet.arguments[0]
    chosenObject = chooseUnmodifiedObject(ctx, 'totalSalience', workspace.objects)
    assert chosenObject
    __showWhichStringObjectIsFrom(chosenObject)
    descriptions = chosenObject.getPossibleDescriptions(descriptionType)
    assert descriptions and len(descriptions)
    weights = [n.activation for n in descriptions]
    chosenProperty = random.weighted_choice(descriptions, weights)
    coderack.proposeDescription(chosenObject, chosenProperty.category(),
                                chosenProperty)


@codelet('description-strength-tester')
def description_strength_tester(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    description = codelet.arguments[0]
    description.descriptor.buffer = 100.0
    description.updateStrength()
    strength = description.totalStrength
    # TODO: use entropy
    probability = strength / 100.0
    assert random.coinFlip(probability)
    coderack.newCodelet('description-builder', strength, [description])


@codelet('description-builder')
def description_builder(ctx, codelet):
    workspace = ctx.workspace
    description = codelet.arguments[0]
    assert description.object in workspace.objects
    if description.object.described(description.descriptor):
        description.descriptionType.buffer = 100.0
        description.descriptor.buffer = 100.0
    else:
        description.build()


def __supportForDescriptionType(ctx, descriptionType, string):
    workspace = ctx.workspace
    described_count = 0
    total = 0
    for o in workspace.objects:
        if o.string == string:
            total += 1
            described_count += sum(1 for d in o.descriptions if d.descriptionType == descriptionType)
    string_support = described_count / float(total)
    return (descriptionType.activation + string_support) / 2


def __chooseBondFacet(ctx, source, destination):
    random = ctx.random
    slipnet = ctx.slipnet

    # specify the descriptor types that bonds can form between
    b = [
        slipnet.letterCategory,
        slipnet.length,
    ]

    sourceFacets = [d.descriptionType for d in source.descriptions if d.descriptionType in b]
    bondFacets = [d.descriptionType for d in destination.descriptions if d.descriptionType in sourceFacets]
    supports = [__supportForDescriptionType(ctx, f, source.string) for f in bondFacets]
    return random.weighted_choice(bondFacets, supports)


@codelet('bottom-up-bond-scout')
def bottom_up_bond_scout(ctx, codelet):
    coderack = ctx.coderack
    slipnet = ctx.slipnet
    workspace = ctx.workspace
    source = chooseUnmodifiedObject(ctx, 'intraStringSalience', workspace.objects)
    assert source is not None
    __showWhichStringObjectIsFrom(source)
    destination = chooseNeighbor(ctx, source)
    assert destination
    logging.info('destination: %s', destination)
    bondFacet = __chooseBondFacet(ctx, source, destination)
    assert bondFacet
    logging.info('chosen bond facet: %s', bondFacet.get_name())
    logging.info('Source: %s, destination: %s', source, destination)
    bond_descriptors = __getDescriptors(bondFacet, source, destination)
    sourceDescriptor, destinationDescriptor = bond_descriptors
    logging.info("source descriptor: %s", sourceDescriptor.name.upper())
    logging.info("destination descriptor: %s",
                 destinationDescriptor.name.upper())
    category = sourceDescriptor.getBondCategory(destinationDescriptor)
    assert category
    if category == slipnet.identity:
        category = slipnet.sameness
    logging.info('proposing %s bond ', category.name)
    coderack.proposeBond(source, destination, category, bondFacet,
                         sourceDescriptor, destinationDescriptor)


@codelet('rule-scout')
def rule_scout(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    slipnet = ctx.slipnet
    workspace = ctx.workspace
    assert workspace.numberOfUnreplacedObjects() == 0
    changedObjects = [o for o in workspace.initial.objects if o.changed]
    # assert len(changedObjects) < 2
    # if there are no changed objects, propose a rule with no changes
    if not changedObjects:
        return coderack.proposeRule(None, None, None, None)

    changed = changedObjects[-1]
    # generate a list of distinguishing descriptions for the first object
    # ie. string-position (left-,right-most,middle or whole) or letter category
    # if it is the only one of its type in the string
    objectList = []
    position = changed.getDescriptor(slipnet.stringPositionCategory)
    if position:
        objectList += [position]
    letter = changed.getDescriptor(slipnet.letterCategory)
    otherObjectsOfSameLetter = [o for o in workspace.initial.objects
                                if not o != changed
                                and o.getDescriptionType(letter)]
    if not len(otherObjectsOfSameLetter):
        objectList += [letter]
    # if this object corresponds to another object in the workspace
    # objectList = the union of this and the distingushing descriptors
    if changed.correspondence:
        targetObject = changed.correspondence.objectFromTarget
        newList = []
        slippages = workspace.slippages()
        for node in objectList:
            node = node.applySlippages(slippages)
            if targetObject.described(node):
                if targetObject.distinguishingDescriptor(node):
                    newList += [node]
        objectList = newList    # surely this should be +=
        # "union of this and distinguishing descriptors"
    assert objectList
    # use conceptual depth to choose a description
    weights = [
        node.conceptualDepth
        for node in objectList
    ]
    descriptor = random.weighted_choice(objectList, weights)
    # choose the relation (change the leftmost object to "successor" or "d"
    objectList = []
    if changed.replacement.relation:
        objectList += [changed.replacement.relation]
    objectList += [changed.replacement.objectFromModified.getDescriptor(
        slipnet.letterCategory)]
    # use conceptual depth to choose a relation
    weights = [
        node.conceptualDepth
        for node in objectList
    ]
    relation = random.weighted_choice(objectList, weights)
    coderack.proposeRule(slipnet.letterCategory, descriptor,
                         slipnet.letter, relation)


@codelet('rule-strength-tester')
def rule_strength_tester(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    rule = codelet.arguments[0]
    rule.updateStrength()
    # TODO: use entropy
    probability = rule.totalStrength / 100.0
    if random.coinFlip(probability):
        coderack.newCodelet('rule-builder', rule.totalStrength, [rule])


@codelet('replacement-finder')
def replacement_finder(ctx, codelet):
    random = ctx.random
    slipnet = ctx.slipnet
    workspace = ctx.workspace
    # choose random letter in initial string
    letters = [o for o in workspace.initial.objects if isinstance(o, Letter)]
    assert letters
    letterOfInitialString = random.choice(letters)
    assert not letterOfInitialString.replacement
    position = letterOfInitialString.leftIndex
    moreLetters = [o for o in workspace.modified.objects
                   if isinstance(o, Letter) and o.leftIndex == position]
    assert moreLetters
    letterOfModifiedString = moreLetters[0]
    initialAscii = ord(workspace.initialString[position - 1])
    modifiedAscii = ord(workspace.modifiedString[position - 1])
    diff = initialAscii - modifiedAscii
    if abs(diff) < 2:
        relations = {
            0: slipnet.sameness,
            -1: slipnet.successor,
            1: slipnet.predecessor
        }
        relation = relations[diff]
    else:
        relation = None
    letterOfInitialString.replacement = Replacement(ctx, letterOfInitialString,
                                                    letterOfModifiedString, relation)
    if relation != slipnet.sameness:
        letterOfInitialString.changed = True
        workspace.changedObject = letterOfInitialString


@codelet('top-down-bond-scout--category')
def top_down_bond_scout__category(ctx, codelet):
    coderack = ctx.coderack
    slipnet = ctx.slipnet
    logging.info('top_down_bond_scout__category')
    category = codelet.arguments[0]
    source = __getScoutSource(ctx, category, formulas.localBondCategoryRelevance,
                              'bond')
    destination = chooseNeighbor(ctx, source)
    logging.info('source: %s, destination: %s', source, destination)
    assert destination
    bondFacet = __chooseBondFacet(ctx, source, destination)
    assert bondFacet
    sourceDescriptor, destinationDescriptor = __getDescriptors(
        bondFacet, source, destination)
    forwardBond = sourceDescriptor.getBondCategory(destinationDescriptor)
    if forwardBond == slipnet.identity:
        forwardBond = slipnet.sameness
        backwardBond = slipnet.sameness
    else:
        backwardBond = destinationDescriptor.getBondCategory(sourceDescriptor)
    assert category == forwardBond or category == backwardBond
    if category == forwardBond:
        coderack.proposeBond(source, destination, category,
                             bondFacet, sourceDescriptor,
                             destinationDescriptor)
    else:
        coderack.proposeBond(destination, source, category,
                             bondFacet, destinationDescriptor,
                             sourceDescriptor)


@codelet('top-down-bond-scout--direction')
def top_down_bond_scout__direction(ctx, codelet):
    coderack = ctx.coderack
    slipnet = ctx.slipnet
    direction = codelet.arguments[0]
    source = __getScoutSource(ctx, direction, formulas.localDirectionCategoryRelevance,
                              'bond')
    destination = chooseDirectedNeighbor(ctx, source, direction)
    assert destination
    logging.info('to object: %s', destination)
    bondFacet = __chooseBondFacet(ctx, source, destination)
    assert bondFacet
    sourceDescriptor, destinationDescriptor = __getDescriptors(
        bondFacet, source, destination)
    category = sourceDescriptor.getBondCategory(destinationDescriptor)
    assert category
    if category == slipnet.identity:
        category = slipnet.sameness
    coderack.proposeBond(source, destination, category, bondFacet,
                         sourceDescriptor, destinationDescriptor)


@codelet('bond-strength-tester')
def bond_strength_tester(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    bond = codelet.arguments[0]
    __showWhichStringObjectIsFrom(bond)
    bond.updateStrength()
    strength = bond.totalStrength
    # TODO: use entropy
    probability = strength / 100.0
    logging.info('bond strength = %d for %s', strength, bond)
    assert random.coinFlip(probability)
    bond.facet.buffer = 100.0
    bond.sourceDescriptor.buffer = 100.0
    bond.destinationDescriptor.buffer = 100.0
    logging.info("succeeded: posting bond-builder")
    coderack.newCodelet('bond-builder', strength, [bond])


@codelet('bond-builder')
def bond_builder(ctx, codelet):
    workspace = ctx.workspace
    bond = codelet.arguments[0]
    __showWhichStringObjectIsFrom(bond)
    bond.updateStrength()
    assert (bond.source in workspace.objects or
            bond.destination in workspace.objects)
    for stringBond in bond.string.bonds:
        if bond.sameNeighbors(stringBond) and bond.sameCategories(stringBond):
            if bond.directionCategory:
                bond.directionCategory.buffer = 100.0
            bond.category.buffer = 100.0
            logging.info('already exists: activate descriptors & Fizzle')
            return
    incompatibleBonds = bond.getIncompatibleBonds()
    logging.info('number of incompatibleBonds: %d', len(incompatibleBonds))
    if len(incompatibleBonds):
        logging.info('%s', incompatibleBonds[0])
    assert __fightIncompatibles(incompatibleBonds, bond, 'bonds', 1.0, 1.0)
    incompatibleGroups = bond.source.getCommonGroups(bond.destination)
    assert __fightIncompatibles(incompatibleGroups, bond, 'groups', 1.0, 1.0)
    # fight all incompatible correspondences
    incompatibleCorrespondences = []
    if bond.leftObject.leftmost or bond.rightObject.rightmost:
        if bond.directionCategory:
            incompatibleCorrespondences = bond.getIncompatibleCorrespondences()
            if incompatibleCorrespondences:
                logging.info("trying to break incompatible correspondences")
                assert __fight(bond, 2.0, incompatibleCorrespondences, 3.0)
            # assert __fightIncompatibles(incompatibleCorrespondences,
            #                            bond, 'correspondences', 2.0, 3.0)
    for incompatible in incompatibleBonds:
        incompatible.break_the_structure()
    for incompatible in incompatibleGroups:
        incompatible.break_the_structure()
    for incompatible in incompatibleCorrespondences:
        incompatible.break_the_structure()
    logging.info('building bond %s', bond)
    bond.buildBond()


# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
@codelet('top-down-group-scout--category')
def top_down_group_scout__category(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    slipnet = ctx.slipnet
    groupCategory = codelet.arguments[0]
    category = groupCategory.getRelatedNode(slipnet.bondCategory)
    assert category
    source = __getScoutSource(ctx, category, formulas.localBondCategoryRelevance,
                              'group')
    assert source and not source.spansString()
    if source.leftmost:
        direction = slipnet.right
    elif source.rightmost:
        direction = slipnet.left
    else:
        direction = random.weighted_choice(
            [slipnet.left, slipnet.right],
            [slipnet.left.activation, slipnet.right.activation]
        )
    if direction == slipnet.left:
        firstBond = source.leftBond
    else:
        firstBond = source.rightBond
    if not firstBond or firstBond.category != category:
        # check the other side of object
        if direction == slipnet.right:
            firstBond = source.leftBond
        else:
            firstBond = source.rightBond
        if not firstBond or firstBond.category != category:
            if category == slipnet.sameness and isinstance(source, Letter):
                group = Group(source.string, slipnet.samenessGroup,
                              None, slipnet.letterCategory, [source], [])
                probability = group.singleLetterGroupProbability()
                if random.coinFlip(probability):
                    coderack.proposeSingleLetterGroup(source)
        return
    direction = firstBond.directionCategory
    search = True
    bondFacet = None
    # find leftmost object in group with these bonds
    while search:
        search = False
        if not source.leftBond:
            continue
        if source.leftBond.category != category:
            continue
        if source.leftBond.directionCategory != direction:
            if source.leftBond.directionCategory:
                continue
        if not bondFacet or bondFacet == source.leftBond.facet:
            bondFacet = source.leftBond.facet
            direction = source.leftBond.directionCategory
            source = source.leftBond.leftObject
            search = True
    # find rightmost object in group with these bonds
    search = True
    destination = source
    while search:
        search = False
        if not destination.rightBond:
            continue
        if destination.rightBond.category != category:
            continue
        if destination.rightBond.directionCategory != direction:
            if destination.rightBond.directionCategory:
                continue
        if not bondFacet or bondFacet == destination.rightBond.facet:
            bondFacet = destination.rightBond.facet
            direction = source.rightBond.directionCategory
            destination = destination.rightBond.rightObject
            search = True
    assert destination != source
    objects = [source]
    bonds = []
    while source != destination:
        bonds += [source.rightBond]
        objects += [source.rightBond.rightObject]
        source = source.rightBond.rightObject
    coderack.proposeGroup(objects, bonds, groupCategory,
                          direction, bondFacet)


@codelet('top-down-group-scout--direction')
def top_down_group_scout__direction(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    slipnet = ctx.slipnet
    direction = codelet.arguments[0]
    source = __getScoutSource(ctx, direction,
                              formulas.localDirectionCategoryRelevance,
                              'direction')
    logging.info('source chosen = %s', source)
    assert not source.spansString()
    if source.leftmost:
        mydirection = slipnet.right
    elif source.rightmost:
        mydirection = slipnet.left
    else:
        mydirection = random.weighted_choice(
            [slipnet.left, slipnet.right],
            [slipnet.left.activation, slipnet.right.activation]
        )
    if mydirection == slipnet.left:
        firstBond = source.leftBond
    else:
        firstBond = source.rightBond
    if not firstBond:
        logging.info('no firstBond')
    else:
        logging.info('firstBond: %s', firstBond)
    if firstBond and not firstBond.directionCategory:
        direction = None
    if not firstBond or firstBond.directionCategory != direction:
        if mydirection == slipnet.right:
            firstBond = source.leftBond
        else:
            firstBond = source.rightBond
        if not firstBond:
            logging.info('no firstBond2')
        else:
            logging.info('firstBond2: %s', firstBond)
        if firstBond and not firstBond.directionCategory:
            direction = None
        assert firstBond and firstBond.directionCategory == direction
    logging.info('possible group: %s', firstBond)
    category = firstBond.category
    assert category
    groupCategory = category.getRelatedNode(slipnet.groupCategory)
    logging.info('trying from %s to %s', source, category.name)
    bondFacet = None
    # find leftmost object in group with these bonds
    search = True
    while search:
        search = False
        if not source.leftBond:
            continue
        if source.leftBond.category != category:
            continue
        if source.leftBond.directionCategory != direction:
            if source.leftBond.directionCategory:
                continue
        if not bondFacet or bondFacet == source.leftBond.facet:
            bondFacet = source.leftBond.facet
            direction = source.leftBond.directionCategory
            source = source.leftBond.leftObject
            search = True
    destination = source
    search = True
    while search:
        search = False
        if not destination.rightBond:
            continue
        if destination.rightBond.category != category:
            continue
        if destination.rightBond.directionCategory != direction:
            if destination.rightBond.directionCategory:
                continue
        if not bondFacet or bondFacet == destination.rightBond.facet:
            bondFacet = destination.rightBond.facet
            direction = source.rightBond.directionCategory
            destination = destination.rightBond.rightObject
            search = True
    assert destination != source
    logging.info('proposing group from %s to %s', source, destination)
    objects = [source]
    bonds = []
    while source != destination:
        bonds += [source.rightBond]
        objects += [source.rightBond.rightObject]
        source = source.rightBond.rightObject
    coderack.proposeGroup(objects, bonds, groupCategory,
                          direction, bondFacet)


# noinspection PyStringFormat
@codelet('group-scout--whole-string')
def group_scout__whole_string(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    slipnet = ctx.slipnet
    workspace = ctx.workspace
    string = random.choice([workspace.initial, workspace.target])
    # find leftmost object & the highest group to which it belongs
    leftmost = next((o for o in string.objects if o.leftmost), None)
    assert leftmost is not None
    while leftmost.group and leftmost.group.bondCategory == slipnet.sameness:
        leftmost = leftmost.group
    if leftmost.spansString():
        # the object already spans the string - propose this object
        if isinstance(leftmost, Group):
            group = leftmost
            coderack.proposeGroup(group.objectList, group.bondList,
                                  group.groupCategory, group.directionCategory,
                                  group.facet)
        else:
            coderack.proposeSingleLetterGroup(leftmost)
        return
    bonds = []
    objects = [leftmost]
    while leftmost.rightBond:
        bonds += [leftmost.rightBond]
        leftmost = leftmost.rightBond.rightObject
        objects += [leftmost]
    assert leftmost.rightmost
    # choose a random bond from list
    chosenBond = random.choice(bonds)
    bonds = chosenBond.possibleGroupBonds(bonds)
    assert bonds
    category = chosenBond.category
    groupCategory = category.getRelatedNode(slipnet.groupCategory)
    directionCategory = chosenBond.directionCategory
    bondFacet = chosenBond.facet
    coderack.proposeGroup(objects, bonds, groupCategory, directionCategory, bondFacet)


@codelet('group-strength-tester')
def group_strength_tester(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    slipnet = ctx.slipnet
    # update strength value of the group
    group = codelet.arguments[0]
    __showWhichStringObjectIsFrom(group)
    group.updateStrength()
    strength = group.totalStrength
    # TODO: use entropy
    probability = strength / 100.0
    if random.coinFlip(probability):
        # it is strong enough - post builder  & activate nodes
        group.groupCategory.getRelatedNode(slipnet.bondCategory).buffer = 100.0
        if group.directionCategory:
            group.directionCategory.buffer = 100.0
        coderack.newCodelet('group-builder', strength, [group])


@codelet('group-builder')
def group_builder(ctx, codelet):
    slipnet = ctx.slipnet
    workspace = ctx.workspace
    # update strength value of the group
    group = codelet.arguments[0]
    __showWhichStringObjectIsFrom(group)
    equivalent = group.string.equivalentGroup(group)
    if equivalent:
        logging.info('already exists...activate descriptors & fizzle')
        group.activateDescriptions()
        equivalent.addDescriptions(group.descriptions)
        return
    # check to see if all objects are still there
    for o in group.objectList:
        assert o in workspace.objects
    # check to see if bonds are there of the same direction
    incompatibleBonds = []  # incompatible bond list
    if len(group.objectList) > 1:
        previous = group.objectList[0]
        for objekt in group.objectList[1:]:
            leftBond = objekt.leftBond
            if leftBond:
                if leftBond.leftObject == previous:
                    continue
                if leftBond.directionCategory == group.directionCategory:
                    continue
                incompatibleBonds += [leftBond]
            previous = objekt
        next_object = group.objectList[-1]
        for objekt in reversed(group.objectList[:-1]):
            rightBond = objekt.rightBond
            if rightBond:
                if rightBond.rightObject == next_object:
                    continue
                if rightBond.directionCategory == group.directionCategory:
                    continue
                incompatibleBonds += [rightBond]
            next_object = objekt
    # if incompatible bonds exist - fight
    group.updateStrength()
    assert __fightIncompatibles(incompatibleBonds, group, 'bonds', 1.0, 1.0)
    # fight incompatible groups
    # fight all groups containing these objects
    incompatibleGroups = group.getIncompatibleGroups()
    assert __fightIncompatibles(incompatibleGroups, group, 'Groups', 1.0, 1.0)
    for incompatible in incompatibleBonds:
        incompatible.break_the_structure()
    # create new bonds
    group.bondList = []
    for i in range(1, len(group.objectList)):
        object1 = group.objectList[i - 1]
        object2 = group.objectList[i]
        if not object1.rightBond:
            if group.directionCategory == slipnet.right:
                source = object1
                destination = object2
            else:
                source = object2
                destination = object1
            category = group.groupCategory.getRelatedNode(slipnet.bondCategory)
            facet = group.facet
            newBond = Bond(ctx, source, destination, category, facet,
                           source.getDescriptor(facet),
                           destination.getDescriptor(facet))
            newBond.buildBond()
        group.bondList += [object1.rightBond]
    for incompatible in incompatibleGroups:
        incompatible.break_the_structure()
    group.buildGroup()
    group.activateDescriptions()
    logging.info('building group')


@codelet('rule-builder')
def rule_builder(ctx, codelet):
    workspace = ctx.workspace
    rule = codelet.arguments[0]
    if rule.ruleEqual(workspace.rule):
        rule.activateRuleDescriptions()
        return
    rule.updateStrength()
    assert rule.totalStrength
    # fight against other rules
    if workspace.rule is not None:
        assert __structureVsStructure(rule, 1.0, workspace.rule, 1.0)
    workspace.buildRule(rule)


def __getCutoffWeights(bondDensity):
    if bondDensity > 0.8:
        return [5.0, 150.0, 5.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    elif bondDensity > 0.6:
        return [2.0, 5.0, 150.0, 5.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    elif bondDensity > 0.4:
        return [1.0, 2.0, 5.0, 150.0, 5.0, 2.0, 1.0, 1.0, 1.0, 1.0]
    elif bondDensity > 0.2:
        return [1.0, 1.0, 2.0, 5.0, 150.0, 5.0, 2.0, 1.0, 1.0, 1.0]
    else:
        return [1.0, 1.0, 1.0, 2.0, 5.0, 150.0, 5.0, 2.0, 1.0, 1.0]


@codelet('rule-translator')
def rule_translator(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    workspace = ctx.workspace
    assert workspace.rule
    if len(workspace.initial) + len(workspace.target) <= 2:
        bondDensity = 1.0
    else:
        numberOfBonds = len(workspace.initial.bonds) + len(workspace.target.bonds)
        nearlyTotalLength = len(workspace.initial) + len(workspace.target) - 2
        bondDensity = numberOfBonds / nearlyTotalLength
        bondDensity = min(bondDensity, 1.0)
    weights = __getCutoffWeights(bondDensity)
    cutoff = 10.0 * random.weighted_choice(list(range(1, 11)), weights)
    if cutoff >= workspace.getUpdatedTemperature():
        result = workspace.rule.buildTranslatedRule()
        if result is not None:
            workspace.finalAnswer = result


@codelet('bottom-up-correspondence-scout')
def bottom_up_correspondence_scout(ctx, codelet):
    coderack = ctx.coderack
    slipnet = ctx.slipnet
    workspace = ctx.workspace
    objectFromInitial = chooseUnmodifiedObject(ctx, 'interStringSalience',
                                               workspace.initial.objects)
    assert objectFromInitial is not None
    objectFromTarget = chooseUnmodifiedObject(ctx, 'interStringSalience',
                                              workspace.target.objects)
    assert objectFromTarget is not None
    assert objectFromInitial.spansString() == objectFromTarget.spansString()
    # get the posible concept mappings
    conceptMappings = formulas.getMappings(
        objectFromInitial, objectFromTarget,
        objectFromInitial.relevantDescriptions(),
        objectFromTarget.relevantDescriptions())
    assert conceptMappings and __slippability(ctx, conceptMappings)
    # find out if any are distinguishing
    distinguishingMappings = [m for m in conceptMappings if m.distinguishing()]
    assert distinguishingMappings
    # if both objects span the strings, check to see if the
    # string description needs to be flipped
    opposites = [m for m in distinguishingMappings
                 if m.initialDescriptionType == slipnet.stringPositionCategory
                 and m.initialDescriptionType != slipnet.bondFacet]
    initialDescriptionTypes = [m.initialDescriptionType for m in opposites]
    flipTargetObject = False
    if (objectFromInitial.spansString() and
        objectFromTarget.spansString() and
        slipnet.directionCategory in initialDescriptionTypes
        and all(m.label == slipnet.opposite for m in opposites)  # unreached?
            and slipnet.opposite.activation != 100.0):
        objectFromTarget = objectFromTarget.flippedVersion()
        conceptMappings = formulas.getMappings(
            objectFromInitial, objectFromTarget,
            objectFromInitial.relevantDescriptions(),
            objectFromTarget.relevantDescriptions())
        flipTargetObject = True
    coderack.proposeCorrespondence(objectFromInitial, objectFromTarget,
                                   conceptMappings, flipTargetObject)


@codelet('important-object-correspondence-scout')
def important_object_correspondence_scout(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    slipnet = ctx.slipnet
    # TODO: use entropy
    workspace = ctx.workspace
    objectFromInitial = chooseUnmodifiedObject(ctx, 'relativeImportance',
                                               workspace.initial.objects)
    assert objectFromInitial is not None
    descriptors = objectFromInitial.relevantDistinguishingDescriptors()
    # choose descriptor by conceptual depth
    weights = [n.conceptualDepth for n in descriptors]
    slipnode = random.weighted_choice(descriptors, weights)
    assert slipnode
    initialDescriptor = slipnode
    for mapping in workspace.slippages():
        if mapping.initialDescriptor == slipnode:
            initialDescriptor = mapping.targetDescriptor
    targetCandidates = []
    for objekt in workspace.target.objects:
        for description in objekt.relevantDescriptions():
            if description.descriptor == initialDescriptor:
                targetCandidates += [objekt]
    assert targetCandidates
    objectFromTarget = chooseUnmodifiedObject(ctx, 'interStringSalience',
                                              targetCandidates)
    assert objectFromInitial.spansString() == objectFromTarget.spansString()
    # get the posible concept mappings
    conceptMappings = formulas.getMappings(
        objectFromInitial, objectFromTarget,
        objectFromInitial.relevantDescriptions(),
        objectFromTarget.relevantDescriptions())
    assert conceptMappings and __slippability(ctx, conceptMappings)
    # find out if any are distinguishing
    distinguishingMappings = [m for m in conceptMappings if m.distinguishing()]
    assert distinguishingMappings
    # if both objects span the strings, check to see if the
    # string description needs to be flipped
    opposites = [m for m in distinguishingMappings
                 if m.initialDescriptionType == slipnet.stringPositionCategory
                 and m.initialDescriptionType != slipnet.bondFacet]
    initialDescriptionTypes = [m.initialDescriptionType for m in opposites]
    flipTargetObject = False
    if (objectFromInitial.spansString()
        and objectFromTarget.spansString()
        and slipnet.directionCategory in initialDescriptionTypes
        and all(m.label == slipnet.opposite for m in opposites)  # unreached?
            and slipnet.opposite.activation != 100.0):
        objectFromTarget = objectFromTarget.flippedVersion()
        conceptMappings = formulas.getMappings(
            objectFromInitial, objectFromTarget,
            objectFromInitial.relevantDescriptions(),
            objectFromTarget.relevantDescriptions())
        flipTargetObject = True
    coderack.proposeCorrespondence(objectFromInitial, objectFromTarget,
                                   conceptMappings, flipTargetObject)


@codelet('correspondence-strength-tester')
def correspondence_strength_tester(ctx, codelet):
    coderack = ctx.coderack
    random = ctx.random
    workspace = ctx.workspace
    correspondence = codelet.arguments[0]
    objectFromInitial = correspondence.objectFromInitial
    objectFromTarget = correspondence.objectFromTarget
    assert (objectFromInitial in workspace.objects and
            (objectFromTarget in workspace.objects or
             correspondence.flipTargetObject and
             not workspace.target.equivalentGroup(
                 objectFromTarget.flipped_version())))
    correspondence.updateStrength()
    strength = correspondence.totalStrength
    # TODO: use entropy
    probability = strength / 100.0
    if random.coinFlip(probability):
        # activate some concepts
        for mapping in correspondence.conceptMappings:
            mapping.initialDescriptionType.buffer = 100.0
            mapping.initialDescriptor.buffer = 100.0
            mapping.targetDescriptionType.buffer = 100.0
            mapping.targetDescriptor.buffer = 100.0
        coderack.newCodelet('correspondence-builder',
                            strength, [correspondence])


@codelet('correspondence-builder')
def correspondence_builder(ctx, codelet):
    workspace = ctx.workspace
    correspondence = codelet.arguments[0]
    objectFromInitial = correspondence.objectFromInitial
    objectFromTarget = correspondence.objectFromTarget
    wantFlip = correspondence.flipTargetObject
    if wantFlip:
        flipper = objectFromTarget.flippedVersion()
        targetNotFlipped = not workspace.target.equivalentGroup(flipper)
    else:
        targetNotFlipped = False
    initialInObjects = objectFromInitial in workspace.objects
    targetInObjects = objectFromTarget in workspace.objects
    assert (initialInObjects or (
        not targetInObjects and (not (wantFlip and targetNotFlipped))))
    if correspondence.reflexive():
        # if the correspondence exists, activate concept mappings
        # and add new ones to the existing corr.
        existing = correspondence.objectFromInitial.correspondence
        for mapping in correspondence.conceptMappings:
            if mapping.label:
                mapping.label.buffer = 100.0
            if not mapping.isContainedBy(existing.conceptMappings):
                existing.conceptMappings += [mapping]
        return
    incompatibles = correspondence.getIncompatibleCorrespondences()
    # fight against all correspondences
    if incompatibles:
        correspondenceSpans = (correspondence.objectFromInitial.letterSpan() +
                               correspondence.objectFromTarget.letterSpan())
        for incompatible in incompatibles:
            incompatibleSpans = (incompatible.objectFromInitial.letterSpan() +
                                 incompatible.objectFromTarget.letterSpan())
            assert __structureVsStructure(correspondence, correspondenceSpans,
                                          incompatible, incompatibleSpans)
    incompatibleBond = None
    incompatibleGroup = None
    # if there is an incompatible bond then fight against it
    initial = correspondence.objectFromInitial
    target = correspondence.objectFromTarget
    if (initial.leftmost or initial.rightmost and
            target.leftmost or target.rightmost):
        # search for the incompatible bond
        incompatibleBond = correspondence.getIncompatibleBond()
        if incompatibleBond:
            # bond found - fight against it
            assert __structureVsStructure(correspondence, 3.0,
                                          incompatibleBond, 2.0)
            # won against incompatible bond
            incompatibleGroup = target.group
            if incompatibleGroup:
                assert __structureVsStructure(correspondence, 1.0,
                                              incompatibleGroup, 1.0)
    # if there is an incompatible rule, fight against it
    incompatibleRule = None
    if workspace.rule:
        if workspace.rule.incompatibleRuleCorrespondence(correspondence):
            incompatibleRule = workspace.rule
            assert __structureVsStructure(correspondence, 1.0,
                                          incompatibleRule, 1.0)
    for incompatible in incompatibles:
        incompatible.break_the_structure()
    # break incompatible group and bond if they exist
    if incompatibleBond:
        incompatibleBond.break_the_structure()
    if incompatibleGroup:
        incompatibleGroup.break_the_structure()
    if incompatibleRule:
        workspace.breakRule()
    correspondence.buildCorrespondence()
