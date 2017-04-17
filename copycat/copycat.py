import logging

from workspace import workspace
from slipnet import slipnet
from temperature import temperature
from coderack import Coderack

from context import context


context.slipnet = slipnet
context.temperature = temperature
context.coderack = Coderack(context)
context.workspace = workspace

def run(initial, modified, target, iterations):
    return context.run(initial, modified, target, iterations)
