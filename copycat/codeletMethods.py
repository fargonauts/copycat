import inspect
import logging
import random

from slipnet import slipnet
import temperature
import formulas
from workspaceFormulas import chooseDirectedNeighbor
from workspaceFormulas import chooseNeighbor
from workspaceObject import WorkspaceObject
from letter import Letter
from replacement import Replacement
from workspaceFormulas import workspace
from group import Group
from bond import Bond
from bond import possibleGroupBonds
from correspondence import Correspondence
from workspaceFormulas import chooseUnmodifiedObject
from workspaceFormulas import chooseBondFacet

def codelet(name):
    """Decorator for otherwise-unused functions that are in fact used as codelet behaviors"""
    def wrap(f):
        assert tuple(inspect.getargspec(f)) == (['coderack', 'codelet'], None, None, None)
        f.is_codelet_method = True
        f.codelet_name = name
        return f
    return wrap

# some methods common to the codelets
def __showWhichStringObjectIsFrom(structure):
    if not structure:
        return
    whence = 'other'
    if isinstance(structure, WorkspaceObject):
        whence = 'target'
        if structure.string == workspace.initial:
            whence = 'initial'
    #print 'object chosen = %s from %s string' % (structure, whence)


def __getScoutSource(slipnode, relevanceMethod, typeName):
    initialRelevance = relevanceMethod(workspace.initial, slipnode)
    targetRelevance = relevanceMethod(workspace.target, slipnode)
    initialUnhappiness = workspace.initial.intraStringUnhappiness
    targetUnhappiness = workspace.target.intraStringUnhappiness
    logging.info('initial : relevance = %d, unhappiness=%d',
                 initialRelevance, int(initialUnhappiness))
    logging.info('target : relevance = %d, unhappiness=%d',
                 targetRelevance, int(targetUnhappiness))
    string = workspace.initial
    relevances = initialRelevance + targetRelevance
    unhappinesses = initialUnhappiness + targetUnhappiness
    randomized = random.random() * (relevances + unhappinesses)
    initials = initialRelevance + initialUnhappiness
    if randomized > initials:
        string = workspace.target
        logging.info('target string selected: %s for %s',
                     workspace.target, typeName)
    else:
        logging.info('initial string selected: %s for %s',
                     workspace.initial, typeName)
    source = chooseUnmodifiedObject('intraStringSalience', string.objects)
    return source


def __getBondFacet(source, destination):
    bondFacet = chooseBondFacet(source, destination)
    assert bondFacet
    return bondFacet


def __getDescriptors(bondFacet, source, destination):
    sourceDescriptor = source.getDescriptor(bondFacet)
    destinationDescriptor = destination.getDescriptor(bondFacet)
    assert sourceDescriptor and destinationDescriptor
    return sourceDescriptor, destinationDescriptor


def __allOppositeMappings(mappings):
    return all(m.label == slipnet.opposite for m in mappings)


def __structureVsStructure(structure1, weight1, structure2, weight2):
    structure1.updateStrength()
    structure2.updateStrength()
    weightedStrength1 = formulas.temperatureAdjustedValue(
        structure1.totalStrength * weight1)
    weightedStrength2 = formulas.temperatureAdjustedValue(
        structure2.totalStrength * weight2)
    rhs = (weightedStrength1 + weightedStrength2) * random.random()
    logging.info('%d > %d', weightedStrength1, rhs)
    return weightedStrength1 > rhs


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


def __slippability(conceptMappings):
    for mapping in conceptMappings:
        slippiness = mapping.slippability() / 100.0
        probabilityOfSlippage = formulas.temperatureAdjustedProbability(
            slippiness)
        if formulas.coinFlip(probabilityOfSlippage):
            return True
    return False


@codelet('breaker')
def breaker(coderack, codelet):
    probabilityOfFizzle = (100.0 - formulas.Temperature) / 100.0
    if formulas.coinFlip(probabilityOfFizzle):
        return
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
        breakProbability = formulas.temperatureAdjustedProbability(
            structure.totalStrength / 100.0)
        if formulas.coinFlip(breakProbability):
            return
    for structure in breakObjects:
        structure.break_the_structure()


@codelet('bottom-up-description-scout')
def bottom_up_description_scout(coderack, codelet):
    chosenObject = chooseUnmodifiedObject('totalSalience', workspace.objects)
    assert chosenObject
    __showWhichStringObjectIsFrom(chosenObject)
    description = formulas.chooseRelevantDescriptionByActivation(chosenObject)
    assert description
    sliplinks = formulas.similarPropertyLinks(description.descriptor)
    assert sliplinks and len(sliplinks)
    values = [sliplink.degreeOfAssociation() * sliplink.destination.activation
              for sliplink in sliplinks]
    i = formulas.selectListPosition(values)
    chosen = sliplinks[i]
    chosenProperty = chosen.destination
    coderack.proposeDescription(chosenObject, chosenProperty.category(),
                                chosenProperty, codelet)


@codelet('top-down-description-scout')
def top_down_description_scout(coderack, codelet):
    descriptionType = codelet.arguments[0]
    chosenObject = chooseUnmodifiedObject('totalSalience', workspace.objects)
    assert chosenObject
    __showWhichStringObjectIsFrom(chosenObject)
    descriptions = chosenObject.getPossibleDescriptions(descriptionType)
    assert descriptions and len(descriptions)
    values = [n.activation for n in descriptions]
    i = formulas.selectListPosition(values)
    chosenProperty = descriptions[i]
    coderack.proposeDescription(chosenObject, chosenProperty.category(),
                                chosenProperty, codelet)


@codelet('description-strength-tester')
def description_strength_tester(coderack, codelet):
    description = codelet.arguments[0]
    description.descriptor.buffer = 100.0
    description.updateStrength()
    strength = description.totalStrength
    probability = formulas.temperatureAdjustedProbability(strength / 100.0)
    assert formulas.coinFlip(probability)
    coderack.newCodelet('description-builder', codelet, strength)


@codelet('description-builder')
def description_builder(coderack, codelet):
    description = codelet.arguments[0]
    assert description.object in workspace.objects
    if description.object.described(description.descriptor):
        description.descriptionType.buffer = 100.0
        description.descriptor.buffer = 100.0
    else:
        description.build()


@codelet('bottom-up-bond-scout')
def bottom_up_bond_scout(coderack, codelet):
    source = chooseUnmodifiedObject('intraStringSalience', workspace.objects)
    __showWhichStringObjectIsFrom(source)
    destination = chooseNeighbor(source)
    assert destination
    logging.info('destination: %s', destination)
    bondFacet = __getBondFacet(source, destination)
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
                         sourceDescriptor, destinationDescriptor, codelet)


@codelet('rule-scout')
def rule_scout(coderack, codelet):
    assert workspace.numberOfUnreplacedObjects() == 0
    changedObjects = [o for o in workspace.initial.objects if o.changed]
    #assert len(changedObjects) < 2
    # if there are no changed objects, propose a rule with no changes
    if not changedObjects:
        return coderack.proposeRule(None, None, None, None, codelet)

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
        objectList = newList  # surely this should be +=
                              # "union of this and distinguishing descriptors"
    assert objectList and len(objectList)
    # use conceptual depth to choose a description
    valueList = []
    for node in objectList:
        depth = node.conceptualDepth
        value = formulas.temperatureAdjustedValue(depth)
        valueList += [value]
    i = formulas.selectListPosition(valueList)
    descriptor = objectList[i]
    # choose the relation (change the letmost object to "successor" or "d"
    objectList = []
    if changed.replacement.relation:
        objectList += [changed.replacement.relation]
    objectList += [changed.replacement.objectFromModified.getDescriptor(
        slipnet.letterCategory)]
    # use conceptual depth to choose a relation
    valueList = []
    for node in objectList:
        depth = node.conceptualDepth
        value = formulas.temperatureAdjustedValue(depth)
        valueList += [value]
    i = formulas.selectListPosition(valueList)
    relation = objectList[i]
    coderack.proposeRule(slipnet.letterCategory, descriptor,
                         slipnet.letter, relation, codelet)


@codelet('rule-strength-tester')
def rule_strength_tester(coderack, codelet):
    rule = codelet.arguments[0]
    rule.updateStrength()
    probability = formulas.temperatureAdjustedProbability(
        rule.totalStrength / 100.0)
    if formulas.coinFlip(probability):
        coderack.newCodelet('rule-builder', codelet, rule.totalStrength, rule)


@codelet('replacement-finder')
def replacement_finder(coderack, codelet):
    # choose random letter in initial string
    letters = [o for o in workspace.initial.objects if isinstance(o, Letter)]
    letterOfInitialString = random.choice(letters)
    logging.info('selected letter in initial string = %s',
                 letterOfInitialString)
    if letterOfInitialString.replacement:
        logging.info("Replacement already found for %s, so fizzling",
                     letterOfInitialString)
        return
    position = letterOfInitialString.leftIndex
    moreLetters = [o for o in workspace.modified.objects
                   if isinstance(o, Letter) and o.leftIndex == position]
    letterOfModifiedString = moreLetters and moreLetters[0] or None
    assert letterOfModifiedString
    position -= 1
    initialAscii = ord(workspace.initialString[position])
    modifiedAscii = ord(workspace.modifiedString[position])
    diff = initialAscii - modifiedAscii
    if abs(diff) < 2:
        relations = {
            0: slipnet.sameness,
            -1: slipnet.successor,
            1: slipnet.predecessor}
        relation = relations[diff]
        logging.info('Relation found: %s', relation.name)
    else:
        relation = None
        logging.info('no relation found')
    letterOfInitialString.replacement = Replacement(
        letterOfInitialString, letterOfModifiedString, relation)
    if relation != slipnet.sameness:
        letterOfInitialString.changed = True
        workspace.changedObject = letterOfInitialString
    logging.info('building replacement')


@codelet('top-down-bond-scout--category')
def top_down_bond_scout__category(coderack, codelet):
    logging.info('top_down_bond_scout__category')
    category = codelet.arguments[0]
    source = __getScoutSource(category, formulas.localBondCategoryRelevance,
                              'bond')
    destination = chooseNeighbor(source)
    logging.info('source: %s, destination: %s', source, destination)
    assert destination
    bondFacet = __getBondFacet(source, destination)
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
                             destinationDescriptor, codelet)
    else:
        coderack.proposeBond(destination, source, category,
                             bondFacet, destinationDescriptor,
                             sourceDescriptor, codelet)


@codelet('top-down-bond-scout--direction')
def top_down_bond_scout__direction(coderack, codelet):
    direction = codelet.arguments[0]
    source = __getScoutSource(
        direction, formulas.localDirectionCategoryRelevance, 'bond')
    destination = chooseDirectedNeighbor(source, direction)
    assert destination
    logging.info('to object: %s', destination)
    bondFacet = __getBondFacet(source, destination)
    sourceDescriptor, destinationDescriptor = __getDescriptors(
        bondFacet, source, destination)
    category = sourceDescriptor.getBondCategory(destinationDescriptor)
    assert category
    if category == slipnet.identity:
        category = slipnet.sameness
    coderack.proposeBond(source, destination, category, bondFacet,
                         sourceDescriptor, destinationDescriptor, codelet)


@codelet('bond-strength-tester')
def bond_strength_tester(coderack, codelet):
    bond = codelet.arguments[0]
    __showWhichStringObjectIsFrom(bond)
    bond.updateStrength()
    strength = bond.totalStrength
    probability = formulas.temperatureAdjustedProbability(strength / 100.0)
    logging.info('bond strength = %d for %s', strength, bond)
    assert formulas.coinFlip(probability)
    bond.facet.buffer = 100.0
    bond.sourceDescriptor.buffer = 100.0
    bond.destinationDescriptor.buffer = 100.0
    logging.info("succeeded: posting bond-builder")
    coderack.newCodelet('bond-builder', codelet, strength)


@codelet('bond-builder')
def bond_builder(coderack, codelet):
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
            #assert __fightIncompatibles(incompatibleCorrespondences,
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
def top_down_group_scout__category(coderack, codelet):
    groupCategory = codelet.arguments[0]
    category = groupCategory.getRelatedNode(slipnet.bondCategory)
    assert category
    source = __getScoutSource(category, formulas.localBondCategoryRelevance,
                              'group')
    assert source and not source.spansString()
    if source.leftmost:
        direction = slipnet.right
    elif source.rightmost:
        direction = slipnet.left
    else:
        activations = [slipnet.left.activation, slipnet.right.activation]
        if not formulas.selectListPosition(activations):
            direction = slipnet.left
        else:
            direction = slipnet.right
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
                if formulas.coinFlip(probability):
                    coderack.proposeSingleLetterGroup(source, codelet)
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
                          direction, bondFacet, codelet)


@codelet('top-down-group-scout--direction')
def top_down_group_scout__direction(coderack, codelet):
    direction = codelet.arguments[0]
    source = __getScoutSource(direction,
                              formulas.localDirectionCategoryRelevance,
                              'direction')
    logging.info('source chosen = %s', source)
    assert not source.spansString()
    if source.leftmost:
        mydirection = slipnet.right
    elif source.rightmost:
        mydirection = slipnet.left
    else:
        activations = [slipnet.left.activation]
        activations += [slipnet.right.activation]
        if not formulas.selectListPosition(activations):
            mydirection = slipnet.left
        else:
            mydirection = slipnet.right
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
                          direction, bondFacet, codelet)


#noinspection PyStringFormat
@codelet('group-scout--whole-string')
def group_scout__whole_string(coderack, codelet):
    if formulas.coinFlip():
        string = workspace.target
        logging.info('target string selected: %s', workspace.target)
    else:
        string = workspace.initial
        logging.info('initial string selected: %s', workspace.initial)
    # find leftmost object & the highest group to which it belongs
    leftmost = None
    for objekt in string.objects:
        if objekt.leftmost:
            leftmost = objekt
    while leftmost.group and leftmost.group.bondCategory == slipnet.sameness:
        leftmost = leftmost.group
    if leftmost.spansString():
        # the object already spans the string - propose this object
        group = leftmost
        coderack.proposeGroup(group.objectList, group.bondList,
                              group.groupCategory, group.directionCategory,
                              group.facet, codelet)
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
    category = chosenBond.category
    directionCategory = chosenBond.directionCategory
    bondFacet = chosenBond.facet
    bonds = possibleGroupBonds(category, directionCategory, bondFacet, bonds)
    assert bonds
    groupCategory = category.getRelatedNode(slipnet.groupCategory)
    coderack.proposeGroup(objects, bonds, groupCategory, directionCategory,
                          bondFacet, codelet)


@codelet('group-strength-tester')
def group_strength_tester(coderack, codelet):
    # update strength value of the group
    group = codelet.arguments[0]
    __showWhichStringObjectIsFrom(group)
    group.updateStrength()
    strength = group.totalStrength
    probability = formulas.temperatureAdjustedProbability(strength / 100.0)
    if formulas.coinFlip(probability):
        # it is strong enough - post builder  & activate nodes
        group.groupCategory.getRelatedNode(slipnet.bondCategory).buffer = 100.0
        if group.directionCategory:
            group.directionCategory.buffer = 100.0
        coderack.newCodelet('group-builder', codelet, strength)


@codelet('group-builder')
def group_builder(coderack, codelet):
    # update strength value of the group
    group = codelet.arguments[0]
    #print '%s' % group
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
            #print 770
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
    for i in xrange(1, len(group.objectList)):
        #print 803
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
            newBond = Bond(source, destination, category, facet,
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
def rule_builder(coderack, codelet):
    rule = codelet.arguments[0]
    if rule.ruleEqual(workspace.rule):
        rule.activateRuleDescriptions()
        return
    rule.updateStrength()
    assert rule.totalStrength
    # fight against other rules
    if workspace.rule:
        assert __structureVsStructure(rule, 1.0, workspace.rule, 1.0)
    workspace.buildRule(rule)


def __getCutOff(density):
    if density > 0.8:
        distribution = [5.0, 150.0, 5.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    elif density > 0.6:
        distribution = [2.0, 5.0, 150.0, 5.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    elif density > 0.4:
        distribution = [1.0, 2.0, 5.0, 150.0, 5.0, 2.0, 1.0, 1.0, 1.0, 1.0]
    elif density > 0.2:
        distribution = [1.0, 1.0, 2.0, 5.0, 150.0, 5.0, 2.0, 1.0, 1.0, 1.0]
    else:
        distribution = [1.0, 1.0, 1.0, 2.0, 5.0, 150.0, 5.0, 2.0, 1.0, 1.0]
    stop = sum(distribution) * random.random()
    total = 0.0
    for i in xrange(len(distribution)):
        total += distribution[i]
        if total >= stop:
            return i + 1
    return len(distribution)


@codelet('rule-translator')
def rule_translator(coderack, codelet):
    assert workspace.rule
    if len(workspace.initial) == 1 and len(workspace.target) == 1:
        bondDensity = 1.0
    else:
        numberOfBonds = (len(workspace.initial.bonds) +
                         len(workspace.target.bonds))
        nearlyTotalLength = len(workspace.initial) + len(workspace.target) - 2
        bondDensity = numberOfBonds / nearlyTotalLength
        if bondDensity > 1.0:
            bondDensity = 1.0
    cutoff = __getCutOff(bondDensity) * 10.0
    assert cutoff >= formulas.actualTemperature
    if workspace.rule.buildTranslatedRule():
        workspace.foundAnswer = True
    else:
        temperature.clampTime = coderack.codeletsRun + 100
        temperature.clamped = True
        formulas.Temperature = 100.0


@codelet('bottom-up-correspondence-scout')
def bottom_up_correspondence_scout(coderack, codelet):
    objectFromInitial = chooseUnmodifiedObject('interStringSalience',
                                               workspace.initial.objects)
    objectFromTarget = chooseUnmodifiedObject('interStringSalience',
                                              workspace.target.objects)
    assert objectFromInitial.spansString() == objectFromTarget.spansString()
    # get the posible concept mappings
    conceptMappings = formulas.getMappings(
        objectFromInitial, objectFromTarget,
        objectFromInitial.relevantDescriptions(),
        objectFromTarget.relevantDescriptions())
    assert conceptMappings and __slippability(conceptMappings)
    #find out if any are distinguishing
    distinguishingMappings = [m for m in conceptMappings if m.distinguishing()]
    assert distinguishingMappings
    # if both objects span the strings, check to see if the
    # string description needs to be flipped
    opposites = [m for m in distinguishingMappings
                 if m.initialDescriptionType == slipnet.stringPositionCategory
                 and m.initialDescriptionType != slipnet.bondFacet]
    initialDescriptionTypes = [m.initialDescriptionType for m in opposites]
    flipTargetObject = False
    if  (objectFromInitial.spansString() and
         objectFromTarget.spansString() and
         slipnet.directionCategory in initialDescriptionTypes
         and __allOppositeMappings(formulas.oppositeMappings)
         and slipnet.opposite.activation != 100.0):
        objectFromTarget = objectFromTarget.flippedVersion()
        conceptMappings = formulas.getMappings(
            objectFromInitial, objectFromTarget,
            objectFromInitial.relevantDescriptions(),
            objectFromTarget.relevantDescriptions())
        flipTargetObject = True
    coderack.proposeCorrespondence(objectFromInitial, objectFromTarget,
                                   conceptMappings, flipTargetObject, codelet)


@codelet('important-object-correspondence-scout')
def important_object_correspondence_scout(coderack, codelet):
    objectFromInitial = chooseUnmodifiedObject('relativeImportance',
                                               workspace.initial.objects)
    descriptors = objectFromInitial.relevantDistinguishingDescriptors()
    slipnode = formulas.chooseSlipnodeByConceptualDepth(descriptors)
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
    objectFromTarget = chooseUnmodifiedObject('interStringSalience',
                                              targetCandidates)
    assert objectFromInitial.spansString() == objectFromTarget.spansString()
    # get the posible concept mappings
    conceptMappings = formulas.getMappings(
        objectFromInitial, objectFromTarget,
        objectFromInitial.relevantDescriptions(),
        objectFromTarget.relevantDescriptions())
    assert conceptMappings and __slippability(conceptMappings)
    #find out if any are distinguishing
    distinguishingMappings = [m for m in conceptMappings if m.distinguishing()]
    assert distinguishingMappings
    # if both objects span the strings, check to see if the
    # string description needs to be flipped
    opposites = [m for m in distinguishingMappings
                 if m.initialDescriptionType == slipnet.stringPositionCategory
                 and m.initialDescriptionType != slipnet.bondFacet]
    initialDescriptionTypes = [m.initialDescriptionType for m in opposites]
    flipTargetObject = False
    if  (objectFromInitial.spansString()
         and objectFromTarget.spansString()
         and slipnet.directionCategory in initialDescriptionTypes
         and __allOppositeMappings(formulas.oppositeMappings)
         and slipnet.opposite.activation != 100.0):
        objectFromTarget = objectFromTarget.flippedVersion()
        conceptMappings = formulas.getMappings(
            objectFromInitial, objectFromTarget,
            objectFromInitial.relevantDescriptions(),
            objectFromTarget.relevantDescriptions())
        flipTargetObject = True
    coderack.proposeCorrespondence(objectFromInitial, objectFromTarget,
                                   conceptMappings, flipTargetObject, codelet)


@codelet('correspondence-strength-tester')
def correspondence_strength_tester(coderack, codelet):
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
    probability = formulas.temperatureAdjustedProbability(strength / 100.0)
    if formulas.coinFlip(probability):
        # activate some concepts
        for mapping in correspondence.conceptMappings:
            mapping.initialDescriptionType.buffer = 100.0
            mapping.initialDescriptor.buffer = 100.0
            mapping.targetDescriptionType.buffer = 100.0
            mapping.targetDescriptor.buffer = 100.0
        coderack.newCodelet('correspondence-builder', codelet,
                            strength, correspondence)


@codelet('correspondence-builder')
def correspondence_builder(coderack, codelet):
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
    if  (initial.leftmost or initial.rightmost and
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
