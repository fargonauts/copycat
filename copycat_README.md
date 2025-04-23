# README_copycat.md

## Overview
`copycat.py` is the core module of the Copycat system, implementing the main analogical reasoning algorithm. It coordinates the interaction between various components like the workspace, slipnet, coderack, and temperature system.

## Core Components
- `Copycat` class: Main class that orchestrates the analogical reasoning process
- `Reporter` class: Base class for defining different types of reporters (GUI, curses, etc.)

## Key Features
- Implements the main Copycat algorithm for analogical reasoning
- Manages the interaction between different system components
- Supports multiple interfaces (GUI, curses, command-line)
- Provides temperature-based control of the reasoning process
- Handles multiple iterations and answer collection

## Main Methods
- `run(initial, modified, target, iterations)`: Run the algorithm for a specified number of iterations
- `runGUI()`: Run the algorithm with graphical interface
- `run_forever(initial, modified, target)`: Run the algorithm continuously
- `runTrial()`: Run a single trial of the algorithm
- `step()`: Execute a single step of the algorithm
- `update_workspace(currentTime)`: Update all workspace components

## Dependencies
- Requires `coderack`, `randomness`, `slipnet`, `temperature`, and `workspace` modules
- Uses `pprint` for pretty printing results
- Optional GUI support through the `gui` module

## Usage
The module is typically used through one of the interface modules:
- `main.py` for command-line interface
- `gui.py` for graphical interface
- `curses_main.py` for terminal-based interface

## Notes
- The system uses a temperature-based control mechanism to guide the reasoning process
- Results include answer statistics, temperature, and time metrics
- The system supports both single-run and continuous operation modes
- The reporter system allows for flexible output handling 