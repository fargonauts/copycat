# README_gui.md

## Overview
`gui.py` is a graphical user interface implementation for the Copycat program. It provides a visual interface for running the analogical reasoning system, using matplotlib for visualization with a dark background theme.

## Usage
Run the program from the terminal with the following command:
```bash
python gui.py
```

### Arguments
- `--seed` (optional): Provide a deterministic seed for the random number generator

## Features
- Graphical user interface for the Copycat system
- Dark background theme for better visibility
- Real-time visualization of the system's operation
- Detailed logging to `./output/copycat.log`

## Dependencies
- Requires the `copycat` module
- Uses `matplotlib` for visualization
- Uses `argparse` for command-line argument parsing
- Uses `logging` for output logging

## Notes
- The GUI provides a more user-friendly interface compared to the command-line version
- Results are displayed both in the GUI and printed to the console
- The interface includes temperature and time information for each answer
- The dark background theme is optimized for better visibility of the visualization 