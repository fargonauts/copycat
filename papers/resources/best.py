def _working_best(temp, prob):
    s = .5   # convergence
    r = 1.05 # power
    u = prob ** r if prob < .5 else prob ** (1/r)
    return _weighted(temp, prob, s, u)

def _soft_best(temp, prob):
    s = .5   # convergence
    r = 1.05 # power
    u = prob ** r if prob < .5 else prob ** (1/r)
    return _weighted(temp, prob, s, u)

def _parameterized_best(temp, prob):
    alpha = 5
    beta  = 1
    s     = .5
    s     = (alpha * prob + beta * s) / (alpha + beta)
    r     = 1.05
    u = prob ** r if prob < .5 else prob ** (1/r)
    return _weighted(temp, prob, s, u)

