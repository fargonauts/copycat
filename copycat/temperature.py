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

def _weighted_inverse(temp, prob):
    iprob = 1 - prob
    weight = 100
    inverse_weighted = (temp / weight) * iprob + ((weight - temp) / weight) * prob 
    return inverse_weighted

def _fifty_converge(temp, prob): # Uses .5 instead of 1-prob
    weight = 100
    curved = (temp / weight) * .5 + ((weight - temp) / weight) * prob 
    return curved 

def _soft_curve(temp, prob): # Curves to the average of the (1-p) and .5
    iprob = 1 - prob
    weight = 100
    curved = min(1, (temp / weight) * ((1.5 - prob) / 2) + ((weight - temp) / weight) * prob)
    return curved

def _weighted_soft_curve(temp, prob): # Curves to the weighted average of the (1-p) and .5
    weight = 100 # Don't change me in this context
    gamma  = .5  # convergance value
    alpha  = 1   # gamma weight
    beta   = 3   # iprob weight
    curved = min(1, (temp / weight) * ((alpha * gamma + beta * (1 - prob)) / (alpha + beta)) + ((weight - temp) / weight) * prob)
    return curved

class Temperature(object):
    def __init__(self):
        self.reset()
        self.adjustmentType = 'inverse'
        self._adjustmentFormulas = {
                'original'       : _original,
                'entropy'        : _entropy,
                'inverse'        : _weighted_inverse,
                'fifty_converge' : _fifty_converge,
                'soft'           : _soft_curve,
                'weighted_soft'  : _weighted_soft_curve}

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
