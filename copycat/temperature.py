import math

class Temperature(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.actual_value = 100.0
        self.last_unclamped_value = 100.0
        self.clamped = True
        self.clampTime = 30

    def update(self, value):
        self.last_unclamped_value = value
        if self.clamped:
            self.actual_value = 100.0
        else:
            self.actual_value = value

    def clampUntil(self, when):
        self.clamped = True
        self.clampTime = when
        # but do not modify self.actual_value until someone calls update()

    def tryUnclamp(self, currentTime):
        if self.clamped and currentTime >= self.clampTime:
            self.clamped = False

    def value(self):
        return 100.0 if self.clamped else self.actual_value

    def getAdjustedValue(self, value):
        return value ** (((100.0 - self.value()) / 30.0) + 0.5)

    def getAdjustedProbability(self, value):
        if value == 0 or value == 0.5 or self.value() == 0:
            return value
        if value < 0.5:
            return 1.0 - self.getAdjustedProbability(1.0 - value)
        coldness = 100.0 - self.value()
        a = math.sqrt(coldness)
        c = (10 - a) / 100
        f = (c + 1) * value
        return max(f, 0.5)
