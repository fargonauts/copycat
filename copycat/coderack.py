import re, inspect, math, logging

import utils
import formulas
import workspaceFormulas
from slipnet import slipnet
from codelet import Codelet
from coderackPressure import CoderackPressures

NUMBER_OF_BINS = 7
MAX_NUMBER_OF_CODELETS = 100

codeletsUsed = {}

class CodeRack(object):
	def __init__(self):
		#logging.debug('coderack.__init__()')
		self.speedUpBonds = False
		self.removeBreakerCodelets = False
		self.removeTerracedScan = False
		self.pressures = CoderackPressures()
		self.pressures.initialisePressures()
		self.reset()
		self.initialCodeletNames = ( 'bottom-up-bond-scout', 'replacement-finder', 'bottom-up-correspondence-scout' )
		self.codeletMethodsDir = None
		self.runCodelets = {}
		self.postings = {}

	def reset(self):
		#logging.debug('coderack.reset()')
		from temperature import temperature

		self.codelets = []
		self.codeletsRun = 0
		temperature.clamped = True
		self.pressures.reset()

	def updateCodelets(self):
		if self.codeletsRun > 0:
			self.postTopDownCodelets()
			self.postBottomUpCodelets()

	def getUrgencyBin(self, urgency):
		bin = int(urgency) * NUMBER_OF_BINS
		bin /= 100
		if bin >= NUMBER_OF_BINS:
			bin = NUMBER_OF_BINS - 1
		return bin + 1

	def post(self, codelet):
		#logging.info('Posting codelet called: %s, with urgency %f' % (codelet.name,codelet.urgency))
		self.postings[codelet.name] = self.postings.get(codelet.name, 0) + 1
		self.pressures.addCodelet(codelet)
		self.codelets += [codelet]
		if len(self.codelets) > 100:
			oldCodelet = self.chooseOldCodelet()
			self.removeCodelet(oldCodelet)

	def postTopDownCodelets(self):
		for node in slipnet.slipnodes:
			#logging.info('Trying slipnode: %s' % node.get_name())
			if node.activation == 100.0:
				#logging.info('using slipnode: %s' % node.get_name())
				for codeletName in node.codelets:
					probability = workspaceFormulas.probabilityOfPosting(codeletName)
					howMany = workspaceFormulas.howManyToPost(codeletName)
					#print '%s:%d' % (codeletName,howMany)
					for unused in range(0, howMany):
						if utils.random() < probability:
							urgency = self.getUrgencyBin(node.activation * node.conceptualDepth / 100.0)
							codelet = Codelet(codeletName, urgency, self.codeletsRun)
							codelet.arguments += [node]
							logging.info('Post top down: %s, with urgency: %d' % (codelet.name, urgency))
							#logging.info("From slipnode %s, activation: %s, depth: %s" %(node.get_name(),node.activation,node.conceptual_depth) )
							self.post(codelet)

	def postBottomUpCodelets(self):
		logging.info("posting bottom up codelets")
		self.__postBottomUpCodelets('bottom-up-description-scout')
		self.__postBottomUpCodelets('bottom-up-bond-scout')
		self.__postBottomUpCodelets('group-scout--whole-string')
		self.__postBottomUpCodelets('bottom-up-correspondence-scout')
		self.__postBottomUpCodelets('important-object-correspondence-scout')
		self.__postBottomUpCodelets('replacement-finder')
		self.__postBottomUpCodelets('rule-scout')
		self.__postBottomUpCodelets('rule-translator')
		if not self.removeBreakerCodelets:
			self.__postBottomUpCodelets('breaker')

	def __postBottomUpCodelets(self, codeletName):
		probability = workspaceFormulas.probabilityOfPosting(codeletName)
		howMany = workspaceFormulas.howManyToPost(codeletName)
		#if codeletName == 'bottom-up-bond-scout':
		#	print 'post --> %f:%d' % (probability,howMany)
		if self.speedUpBonds:
			if 'bond' in codeletName or 'group' in codeletName:
				howMany *= 3
		urgency = 3
		if codeletName == 'breaker':
			urgency = 1
		if formulas.Temperature < 25.0 and 'translator' in codeletName:
			urgency = 5
		for unused in range(0, howMany):
			if utils.random() < probability:
				codelet = Codelet(codeletName, urgency, self.codeletsRun)
				self.post(codelet)

	def removeCodelet(self, codelet):
		self.codelets.remove(codelet)
		self.pressures.removeCodelet(codelet)

	def newCodelet(self, name, oldCodelet, strength, arguments=None):
		#logging.debug('Posting new codelet called %s' % name)
		urgency = self.getUrgencyBin(strength)
		newCodelet = Codelet(name, urgency, self.codeletsRun)
		if arguments:
			newCodelet.arguments = [arguments]
		else:
			newCodelet.arguments = oldCodelet.arguments
		newCodelet.pressure = oldCodelet.pressure
		self.tryRun(newCodelet)

	def proposeRule(self, facet, description, category, relation, oldCodelet):
		"""Creates a proposed rule, and posts a rule-strength-tester codelet.

		The new codelet has urgency a function of the degree of conceptual-depth of the descriptions in the rule
		"""
		from rule import Rule

		rule = Rule(facet, description, category, relation)
		rule.updateStrength()
		if description and relation:
			depths = description.conceptualDepth + relation.conceptualDepth
			depths /= 200.0
			urgency = math.sqrt(depths) * 100.0
		else:
			urgency = 0
		self.newCodelet('rule-strength-tester', oldCodelet, urgency, rule)

	def proposeCorrespondence(self, initialObject, targetObject, conceptMappings, flipTargetObject, oldCodelet):
		from correspondence import Correspondence

		correspondence = Correspondence(initialObject, targetObject, conceptMappings, flipTargetObject)
		for mapping in conceptMappings:
			mapping.initialDescriptionType.buffer = 100.0
			mapping.initialDescriptor.buffer = 100.0
			mapping.targetDescriptionType.buffer = 100.0
			mapping.targetDescriptor.buffer = 100.0
		mappings = correspondence.distinguishingConceptMappings()
		urgency = sum([mapping.strength() for mapping in mappings])
		numberOfMappings = len(mappings)
		if urgency:
			urgency /= numberOfMappings
		bin = self.getUrgencyBin(urgency)
		logging.info('urgency: %s, number: %d, bin: %d' % (urgency, numberOfMappings, bin))
		self.newCodelet('correspondence-strength-tester', oldCodelet, urgency, correspondence)

	def proposeDescription(self, objekt, descriptionType, descriptor, oldCodelet):
		from description import Description

		description = Description(objekt, descriptionType, descriptor)
		descriptor.buffer = 100.0
		urgency = descriptionType.activation
		self.newCodelet('description-strength-tester', oldCodelet, urgency, description)

	def proposeSingleLetterGroup(self, source, codelet):
		self.proposeGroup([source], [], slipnet.samenessGroup, None, slipnet.letterCategory, codelet)

	def proposeGroup(self, objects, bondList, groupCategory, directionCategory, bondFacet, oldCodelet ):
		from group import Group

		bondCategory = groupCategory.getRelatedNode(slipnet.bondCategory)
		bondCategory.buffer = 100.0
		if directionCategory:
			directionCategory.buffer = 100.0
		group = Group(objects[0].string, groupCategory, directionCategory, bondFacet, objects, bondList)
		urgency = bondCategory.bondDegreeOfAssociation()
		self.newCodelet('group-strength-tester', oldCodelet, urgency, group)

	def proposeBond(self, source, destination, bondCategory, bondFacet, sourceDescriptor, destinationDescriptor, oldCodelet ):
		from bond import Bond

		bondFacet.buffer = 100.0
		sourceDescriptor.buffer = 100.0
		destinationDescriptor.buffer = 100.0
		bond = Bond(source, destination, bondCategory, bondFacet, sourceDescriptor, destinationDescriptor)
		urgency = bondCategory.bondDegreeOfAssociation()
		self.newCodelet('bond-strength-tester', oldCodelet, urgency, bond)

	def chooseOldCodelet(self):
		# selects an old codelet to remove from the coderack
		# more likely to select lower urgency codelets
		if not len(self.codelets):
			return None
		urgencies = []
		for codelet in self.codelets:
			urgency = (coderack.codeletsRun - codelet.timeStamp) * (7.5 - codelet.urgency)
			urgencies += [urgency]
		threshold = utils.random() * sum(urgencies)
		sumOfUrgencies = 0.0
		for i in range(0, len(self.codelets)):
			sumOfUrgencies += urgencies[i]
			if sumOfUrgencies > threshold:
				return self.codelets[i]
		return self.codelets[0]

	def postInitialCodelets(self):
		#logging.debug('Posting initial codelets')
		#logging.debug('Number of inital codelets: %d' % len(self.initialCodeletNames))
		#logging.debug('Number of workspaceObjects: %d' % workspace.numberOfObjects())
		for name in self.initialCodeletNames:
			for unused in range(0, workspaceFormulas.numberOfObjects()):
				codelet = Codelet(name, 1, self.codeletsRun)
				self.post(codelet)
				codelet2 = Codelet(name, 1, self.codeletsRun)
				self.post(codelet2)

	def tryRun(self, newCodelet):
		if self.removeTerracedScan:
			self.run(newCodelet)
		else:
			self.post(newCodelet)

	def getCodeletmethods(self):
		import codeletMethods

		self.codeletMethodsDir = dir(codeletMethods)
		knownCodeletNames = (
		'breaker',
		'bottom-up-description-scout',
		'top-down-description-scout',
		'description-strength-tester',
		'description-builder',
		'bottom-up-bond-scout',
		'top-down-bond-scout--category',
		'top-down-bond-scout--direction',
		'bond-strength-tester',
		'bond-builder',
		'top-down-group-scout--category',
		'top-down-group-scout--direction',
		'group-scout--whole-string',
		'group-strength-tester',
		'group-builder',
		'replacement-finder',
		'rule-scout',
		'rule-strength-tester',
		'rule-builder',
		'rule-translator',
		'bottom-up-correspondence-scout',
		'important-object-correspondence-scout',
		'correspondence-strength-tester',
		'correspondence-builder',
		)
		self.methods = {}
		for codeletName in knownCodeletNames:
			methodName = re.sub('[ -]', '_', codeletName)
			if methodName not in self.codeletMethodsDir:
				raise NotImplementedError, 'Cannot find %s in codeletMethods' % methodName
			method = getattr(codeletMethods, methodName)
			self.methods[methodName] = method

	def chooseAndRunCodelet(self):
		if not len(coderack.codelets):
			coderack.postInitialCodelets()
		codelet = self.chooseCodeletToRun()
		if codelet:
			self.run(codelet)

	def chooseCodeletToRun(self):
		if not self.codelets:
			return None
		temp = formulas.Temperature
		scale = ( 100.0 - temp + 10.0 ) / 15.0
		#		threshold = sum( [ c.urgency ** scale for c in self.codelets ] ) * utils.random()
		urgsum = 0.0
		for codelet in self.codelets:
			urg = codelet.urgency ** scale
			urgsum += urg
		r = utils.random()
		threshold = r * urgsum
		chosen = None
		urgencySum = 0.0
		logging.info('temperature: %f' % formulas.Temperature)
		logging.info('actualTemperature: %f' % formulas.actualTemperature)
		logging.info('Slipnet:')
		for node in slipnet.slipnodes:
			logging.info("\tnode %s, activation: %d, buffer: %d, depth: %s" % (node.get_name(), node.activation, node.buffer, node.conceptualDepth))
		logging.info('Coderack:')
		for codelet in self.codelets:
			logging.info('\t%s, %d' % (codelet.name, codelet.urgency))
		from workspace import workspace

		workspace.initial.log("Initial: ")
		workspace.target.log("Target: ")
		for codelet in self.codelets:
			urgencySum += codelet.urgency ** scale
			if not chosen and urgencySum > threshold:
				chosen = codelet
				break
		if not chosen:
			chosen = self.codelets[0]
		self.removeCodelet(chosen)
		logging.info('chosen codelet\n\t%s, urgency = %s' % (chosen.name, chosen.urgency))
		return chosen

	def run(self, codelet):
		methodName = re.sub('[ -]', '_', codelet.name)
		self.codeletsRun += 1
		self.runCodelets[methodName] = self.runCodelets.get(methodName, 0) + 1

		#if self.codeletsRun > 2000:
		#import sys
		#print "running too many codelets"
		#for name,count in self.postings.iteritems():
		#print '%d:%s' % (count,name)
		#raise ValueError
		#else:
		#	print 'running %d' % self.codeletsRun
		if not self.codeletMethodsDir:
			self.getCodeletmethods()
		#if not self.codeletMethodsDir:
		method = self.methods[methodName]
		if not method:
			raise ValueError, 'Found %s in codeletMethods, but cannot get it' % methodName
		if not callable(method):
			raise RuntimeError, 'Cannot call %s()' % methodName
		args, varargs, varkw, defaults = inspect.getargspec(method)
		#global codeletsUsed
		#codeletsUsed[methodName] = codeletsUsed.get(methodName,0) + 1
		try:
			if 'codelet' in args:
				method(codelet)
			else:
				method()
		except AssertionError:
			pass

coderack = CodeRack()
