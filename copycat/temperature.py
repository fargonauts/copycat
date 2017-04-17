import logging


class Temperature(object):
    def __init__(self):
        self.value = 100.0
        self.clamped = True
        self.clampTime = 30

    def update(self, value):
        self.value = value

    def tryUnclamp(self, currentTime):
        if self.clamped and currentTime >= self.clampTime:
            logging.info('unclamp temperature at %d', currentTime)
            self.clamped = False


temperature = Temperature()
