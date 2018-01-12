import math

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
