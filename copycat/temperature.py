import logging

class Temperature(object):
	def __init__(self):
		self.value = 100.0
		self.clamped = True
		self.clampTime = 30

	def update(self, value):
		logging.debug('update to %s' % value)
		self.value = value

	def tryUnclamp(self):
		from coderack import coderack

		if self.clamped and coderack.codeletsRun >= self.clampTime:
			logging.info('unclamp temperature at %d' % coderack.codeletsRun)
			self.clamped = False

	def log(self):
		logging.debug('temperature.value: %f' % self.value)

temperature = Temperature()
