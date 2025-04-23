# README_curses_main.md

## Overview
`curses_main.py` is a terminal-based interface for the Copycat program that provides a visual representation of the analogical reasoning process using the curses library. It offers a real-time view of the system's operation, including the workspace, slipnet, and coderack.

## Usage
Run the program from the terminal with the following command:
```bash
python curses_main.py abc abd ppqqrr
```

### Arguments
- `initial`: The first string in the analogy (e.g., "abc")
- `modified`: The second string showing the transformation (e.g., "abd")
- `target`: The third string to be transformed (e.g., "ppqqrr")
- `--focus-on-slipnet` (optional): Show the slipnet and coderack instead of the workspace
- `--fps` (optional): Target frames per second for the display
- `--seed` (optional): Provide a deterministic seed for the random number generator

## Features
- Interactive terminal-based interface
- Real-time visualization of the Copycat system's operation
- Option to focus on different components (workspace or slipnet/coderack)
- Configurable display speed
- Detailed logging to `./copycat.log`

## Dependencies
- Requires the `copycat` module
- Uses `curses` for terminal-based interface
- Uses `argparse` for command-line argument parsing
- Uses `logging` for output logging

## Notes
- The program can be interrupted with Ctrl+C
- The display is automatically cleaned up when the program exits
- The interface provides a more detailed view of the system's operation compared to the standard command-line interface 