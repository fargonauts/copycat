import math

# Alternate formulas for getAdjustedProbability

def _original(temp, prob):
    if prob == 0 or prob == 0.5 or temp == 0:
        return prob
    if prob < 0.5:
        return 1.0 - _original(temp, 1.0 - prob)
    coldness = 100.0 - temp
    a = math.sqrt(coldness)
    c = (10 - a) / 100
    f = (c + 1) * prob
    return max(f, 0.5)

def _entropy(temp, prob):
    if prob == 0 or prob == 0.5 or temp == 0:
        return prob
    if prob < 0.5:
        return 1.0 - _original(temp, 1.0 - prob)
    coldness = 100.0 - temp
    a = math.sqrt(coldness)
    c = (10 - a) / 100
    f = (c + 1) * prob
    return -f * math.log2(f)

def _inverse_prob(temp, prob):
    iprob = 1 - prob
    return (temp / 100) * iprob + ((100 - temp) / 100) * prob

class Temperature(object):
    def __init__(self):
        self.reset()
        self.adjustmentType = 'inverse'
        self._adjustmentFormulas = {
                'original'    : _original,
                'entropy'     : _entropy,
                'inverse'     : _inverse_prob}

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
        temp = self.value()
        prob = value
        return self._adjustmentFormulas[self.adjustmentType](temp, prob)

    def useAdj(self, adj):
        print('Changing to adjustment formula {}'.format(adj))
        self.adjustmentType = adj

    def adj_formulas(self):
        return self._adjustmentFormulas.keys()
