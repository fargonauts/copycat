import logging

from slipnode import Slipnode
from sliplink import Sliplink


class SlipNet(object):
    def __init__(self):
        logging.debug("SlipNet.__init__()")
        self.initiallyClampedSlipnodes = []
        self.slipnodes = []
        self.sliplinks = []
        self.bondFacets = []
        self.timeStepLength = 15
        self.numberOfUpdates = 0
        self.__addInitialNodes()
        self.__addInitialLinks()
        self.predecessor = None

    def __repr__(self):
        return '<slipnet>'

    def setConceptualDepths(self, depth):
        logging.debug('slipnet set all depths to %f' % depth)
        [node.setConceptualDepth(depth) for node in self.slipnodes]

    def reset(self):
        logging.debug('slipnet.reset()')
        self.numberOfUpdates = 0
        for node in self.slipnodes:
            node.reset()
            if node in self.initiallyClampedSlipnodes:
                node.clampHigh()

    def update(self):
        logging.debug('slipnet.update()')
        self.numberOfUpdates += 1
        if self.numberOfUpdates == 50:
            [node.unclamp() for node in self.initiallyClampedSlipnodes]
        [node.update() for node in self.slipnodes]
        # Note - spreadActivation() affects more than one node, so the following
        #   cannot go in a general "for node" loop with the other node actions
        for node in self.slipnodes:
            node.spread_activation()
        for node in self.slipnodes:
            node.addBuffer()
            node.jump()
            node.buffer = 0.0

    def __addInitialNodes(self):
        self.slipnodes = []
        self.letters = []
        for c in 'abcdefghijklmnopqrstuvwxyz':
            slipnode = self.__addNode(c, 10.0)
            self.letters += [slipnode]
        self.numbers = []
        for c in '12345':
            slipnode = self.__addNode(c, 30.0)
            self.numbers += [slipnode]

        # string positions
        self.leftmost = self.__addNode('leftmost', 40.0)
        self.rightmost = self.__addNode('rightmost', 40.0)
        self.middle = self.__addNode('middle', 40.0)
        self.single = self.__addNode('single', 40.0)
        self.whole = self.__addNode('whole', 40.0)

        # alphabetic positions
        self.first = self.__addNode('first', 60.0)
        self.last = self.__addNode('last', 60.0)

        # directions
        self.left = self.__addNode('left', 40.0)
        self.left.codelets += ['top-down-bond-scout--direction']
        self.left.codelets += ['top-down-group-scout--direction']
        self.right = self.__addNode('right', 40.0)
        self.right.codelets += ['top-down-bond-scout--direction']
        self.right.codelets += ['top-down-group-scout--direction']

        # bond types
        self.predecessor = self.__addNode('predecessor', 50.0, 60.0)
        self.predecessor.codelets += ['top-down-bond-scout--category']
        self.successor = self.__addNode('successor', 50.0, 60.0)
        self.successor.codelets += ['top-down-bond-scout--category']
        self.sameness = self.__addNode('sameness', 80.0)
        self.sameness.codelets += ['top-down-bond-scout--category']

        # group types
        self.predecessorGroup = self.__addNode('predecessorGroup', 50.0)
        self.predecessorGroup.codelets += ['top-down-group-scout--category']
        self.successorGroup = self.__addNode('successorGroup', 50.0)
        self.successorGroup.codelets += ['top-down-group-scout--category']
        self.samenessGroup = self.__addNode('samenessGroup', 80.0)
        self.samenessGroup.codelets += ['top-down-group-scout--category']

        # other relations
        self.identity = self.__addNode('identity', 90.0)
        self.opposite = self.__addNode('opposite', 90.0, 80.0)

        # objects
        self.letter = self.__addNode('letter', 20.0)
        self.group = self.__addNode('group', 80.0)

        # categories
        self.letterCategory = self.__addNode('letterCategory', 30.0)
        self.stringPositionCategory = self.__addNode('stringPositionCategory', 70.0)
        self.stringPositionCategory.codelets += ['top-down-description-scout']
        self.alphabeticPositionCategory = self.__addNode('alphabeticPositionCategory', 80.0)
        self.alphabeticPositionCategory.codelets += ['top-down-description-scout']
        self.directionCategory = self.__addNode('directionCategory', 70.0)
        self.bondCategory = self.__addNode('bondCategory', 80.0)
        self.groupCategory = self.__addNode('groupCategory', 80.0)
        self.length = self.__addNode('length', 60.0)
        self.objectCategory = self.__addNode('objectCategory', 90.0)
        self.bondFacet = self.__addNode('bondFacet', 90.0)

        # specify the descriptor types that bonds can form between
        self.bondFacets += [self.letterCategory]
        self.bondFacets += [self.length]

        #
        self.initiallyClampedSlipnodes += [self.letterCategory]
        self.letterCategory.clamped = True
        self.initiallyClampedSlipnodes += [self.stringPositionCategory]
        self.stringPositionCategory.clamped = True

    def __addInitialLinks(self):
        self.sliplinks = []
        self.__link_items_to_their_neighbours(self.letters)
        self.__link_items_to_their_neighbours(self.numbers)
        # letter categories
        for letter in self.letters:
            self.__addInstanceLink(self.letterCategory, letter, 97.0)
        self.__addCategoryLink(self.samenessGroup, self.letterCategory, 50.0)
        # lengths
        for number in self.numbers:
            self.__addInstanceLink(self.length, number, 100.0)
        self.__addNonSlipLink(self.predecessorGroup, self.length, length=95.0)
        self.__addNonSlipLink(self.successorGroup, self.length, length=95.0)
        self.__addNonSlipLink(self.samenessGroup, self.length, length=95.0)
        # opposites
        self.__addOppositeLink(self.first, self.last)
        self.__addOppositeLink(self.leftmost, self.rightmost)
        self.__addOppositeLink(self.left, self.right)
        self.__addOppositeLink(self.successor, self.predecessor)
        self.__addOppositeLink(self.successorGroup, self.predecessorGroup)
        # properties
        self.__addPropertyLink(self.letters[0], self.first, 75.0)
        self.__addPropertyLink(self.letters[-1], self.last, 75.0)
        # object categories
        self.__addInstanceLink(self.objectCategory, self.letter, 100.0)
        self.__addInstanceLink(self.objectCategory, self.group, 100.0)
        # string positions
        self.__addInstanceLink(self.stringPositionCategory, self.leftmost, 100.0)
        self.__addInstanceLink(self.stringPositionCategory, self.rightmost, 100.0)
        self.__addInstanceLink(self.stringPositionCategory, self.middle, 100.0)
        self.__addInstanceLink(self.stringPositionCategory, self.single, 100.0)
        self.__addInstanceLink(self.stringPositionCategory, self.whole, 100.0)
        # alphabetic positions
        self.__addInstanceLink(self.alphabeticPositionCategory, self.first, 100.0)
        self.__addInstanceLink(self.alphabeticPositionCategory, self.last, 100.0)
        # direction categories
        self.__addInstanceLink(self.directionCategory, self.left, 100.0)
        self.__addInstanceLink(self.directionCategory, self.right, 100.0)
        # bond categories
        self.__addInstanceLink(self.bondCategory, self.predecessor, 100.0)
        self.__addInstanceLink(self.bondCategory, self.successor, 100.0)
        self.__addInstanceLink(self.bondCategory, self.sameness, 100.0)
        # group categories
        self.__addInstanceLink(self.groupCategory, self.predecessorGroup, 100.0)
        self.__addInstanceLink(self.groupCategory, self.successorGroup, 100.0)
        self.__addInstanceLink(self.groupCategory, self.samenessGroup, 100.0)
        # link bonds to their groups
        self.__addNonSlipLink(self.sameness, self.samenessGroup, label=self.groupCategory, length=30.0)
        self.__addNonSlipLink(self.successor, self.successorGroup, label=self.groupCategory, length=60.0)
        self.__addNonSlipLink(self.predecessor, self.predecessorGroup, label=self.groupCategory, length=60.0)
        # link bond groups to their bonds
        self.__addNonSlipLink(self.samenessGroup, self.sameness, label=self.bondCategory, length=90.0)
        self.__addNonSlipLink(self.successorGroup, self.successor, label=self.bondCategory, length=90.0)
        self.__addNonSlipLink(self.predecessorGroup, self.predecessor, label=self.bondCategory, length=90.0)
        # bond facets
        self.__addInstanceLink(self.bondFacet, self.letterCategory, 100.0)
        self.__addInstanceLink(self.bondFacet, self.length, 100.0)
        # letter category to length
        self.__addSlipLink(self.letterCategory, self.length, length=95.0)
        self.__addSlipLink(self.length, self.letterCategory, length=95.0)
        # letter to group
        self.__addSlipLink(self.letter, self.group, length=90.0)
        self.__addSlipLink(self.group, self.letter, length=90.0)
        # direction-position, direction-neighbour, position-neighbour
        self.__addBidirectionalLink(self.left, self.leftmost, 90.0)
        self.__addBidirectionalLink(self.right, self.rightmost, 90.0)
        self.__addBidirectionalLink(self.right, self.leftmost, 100.0)
        self.__addBidirectionalLink(self.left, self.rightmost, 100.0)
        self.__addBidirectionalLink(self.leftmost, self.first, 100.0)
        self.__addBidirectionalLink(self.rightmost, self.first, 100.0)
        self.__addBidirectionalLink(self.leftmost, self.last, 100.0)
        self.__addBidirectionalLink(self.rightmost, self.last, 100.0)
        # other
        self.__addSlipLink(self.single, self.whole, length=90.0)
        self.__addSlipLink(self.whole, self.single, length=90.0)

    def __addLink(self, source, destination, label=None, length=0.0):
        link = Sliplink(source, destination, label=label, length=length)
        self.sliplinks += [link]
        return link

    def __addSlipLink(self, source, destination, label=None, length=0.0):
        link = self.__addLink(source, destination, label, length)
        source.lateralSlipLinks += [link]

    def __addNonSlipLink(self, source, destination, label=None, length=0.0):
        link = self.__addLink(source, destination, label, length)
        source.lateralNonSlipLinks += [link]

    def __addBidirectionalLink(self, source, destination, length):
        self.__addNonSlipLink(source, destination, length=length)
        self.__addNonSlipLink(destination, source, length=length)

    def __addCategoryLink(self, source, destination, length):
        #noinspection PyArgumentEqualDefault
        link = self.__addLink(source, destination, None, length)
        source.categoryLinks += [link]

    def __addInstanceLink(self, source, destination, length):
        categoryLength = source.conceptualDepth - destination.conceptualDepth
        self.__addCategoryLink(destination, source, categoryLength)
        #noinspection PyArgumentEqualDefault
        link = self.__addLink(source, destination, None, length)
        source.instanceLinks += [link]

    def __addPropertyLink(self, source, destination, length):
        #noinspection PyArgumentEqualDefault
        link = self.__addLink(source, destination, None, length)
        source.propertyLinks += [link]

    def __addOppositeLink(self, source, destination):
        self.__addSlipLink(source, destination, label=self.opposite)
        self.__addSlipLink(destination, source, label=self.opposite)

    def __addNode(self, name, depth, length=0):
        slipnode = Slipnode(name, depth, length)
        self.slipnodes += [slipnode]
        return slipnode

    def __link_items_to_their_neighbours(self, items):
        previous = items[0]
        for item in items[1:]:
            self.__addNonSlipLink(previous, item, label=self.successor)
            self.__addNonSlipLink(item, previous, label=self.predecessor)
            previous = item

slipnet = SlipNet()
