from coderack import Coderack
from randomness import Randomness
from slipnet import Slipnet
from temperature import Temperature
from workspace import Workspace

from context import context


context.coderack = Coderack(context)
context.random = Randomness(42)
context.slipnet = Slipnet()
context.temperature = Temperature()
context.workspace = Workspace(context)


def run(initial, modified, target, iterations):
    return context.run(initial, modified, target, iterations)
