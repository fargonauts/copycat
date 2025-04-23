# README_cross_compare.md

## Overview
`cross_compare.py` is a utility script that performs cross-comparison analysis between different problem sets in the Copycat system. It reads pickled problem sets and generates a comparison table showing how different variants of the Copycat system perform across various problems.

## Usage
Run the program from the terminal with the following command:
```bash
python cross_compare.py problem_set1.pkl problem_set2.pkl ...
```

### Arguments
- One or more pickled problem set files (`.pkl` files) to compare

## Output
The script generates a CSV file at `output/cross_compare.csv` containing:
- A comparison table of different Copycat variants
- Problem formulas and their results
- Cross-comparison metrics between different problem sets

## Features
- Reads multiple pickled problem sets
- Generates a cross-comparison table
- Organizes results by Copycat variants and formulas
- Exports results to CSV format

## Dependencies
- Requires the `copycat` module
- Uses `pickle` for reading problem sets
- Uses `collections.defaultdict` for data organization
- Uses `pprint` for pretty printing (though not actively used in the current code)

## File Structure
The output CSV file contains:
1. Headers: source, compare, source formula, compare formula
2. Problem descriptions in the format `A:B::C:_`
3. Results for each combination of variants and formulas 