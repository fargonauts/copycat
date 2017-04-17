import logging

from workspace import Workspace
from slipnet import Slipnet
from temperature import Temperature
from coderack import Coderack

from context import context


context.slipnet = Slipnet()
context.temperature = Temperature()
context.coderack = Coderack(context.slipnet)
context.workspace = Workspace()

def run(initial, modified, target, iterations):
    context.run(initial, modified, target, iterations)
