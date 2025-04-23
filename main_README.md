# README_main.md

## Overview
`main.py` is the primary entry point for the Copycat program, which implements an analogical reasoning system. The program takes three strings as input and attempts to find an analogous transformation between them.

## Usage
Run the program from the terminal with the following command:
```bash
python main.py abc abd ppqqrr --iterations 10
```

### Arguments
- `initial`: The first string in the analogy (e.g., "abc")
- `modified`: The second string showing the transformation (e.g., "abd")
- `target`: The third string to be transformed (e.g., "ppqqrr")
- `--iterations` (optional): Number of times to run the case (default: 1)
- `--seed` (optional): Provide a deterministic seed for the random number generator
- `--plot` (optional): Generate a bar graph of answer distribution
- `--noshow` (optional): Don't display the bar graph at the end of the run

## Output
The program produces output in the following format:
```
iiijjjlll: 670 (avg time 1108.5, avg temp 23.6)
iiijjjd: 2 (avg time 1156.0, avg temp 35.0)
...
```
Where:
- The first number indicates how many times Copycat chose that string as its answer (higher means "more obvious")
- The last number indicates the average final temperature of the workspace (lower means "more elegant")

## Features
- Implements the Copycat analogical reasoning system
- Provides detailed logging to `./output/copycat.log`
- Can generate visualizations of answer distributions
- Saves results to `output/answers.csv`

## Dependencies
- Requires the `copycat` module
- Uses `argparse` for command-line argument parsing
- Uses `logging` for output logging 