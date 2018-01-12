def _weighted(temp, prob, s, u):
    weighted = (temp / 100) * s + ((100 - temp) / 100) * u
    return weighted

def _weighted_inverse(temp, prob):
    iprob = 1 - prob
    return _weighted(temp, prob, iprob, prob)

# Uses .5 instead of 1-prob
def _fifty_converge(temp, prob):
    return _weighted(temp, prob, .5, prob)

# Curves to the average of the (1-p) and .5
def _soft_curve(temp, prob):
    return min(1, _weighted(temp, prob, (1.5-prob)/2, prob))

# Curves to the weighted average of the (1-p) and .5
def _weighted_soft_curve(temp, prob):
    weight = 100
    gamma  = .5  # convergance value
    alpha  = 1   # gamma weight
    beta   = 3   # iprob weight
    curved = min(1,
                 (temp / weight) *
                     ((alpha * gamma + beta * (1 - prob)) /
                         (alpha + beta)) +
                 ((weight - temp) / weight) * prob)
    return curved
