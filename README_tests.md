# README_tests.md

## Overview
`tests.py` is a test suite for the Copycat program that verifies the system's behavior across various analogical reasoning problems. It includes functionality to generate test distributions and run statistical tests on the results.

## Usage
Run the tests from the terminal with the following command:
```bash
python tests.py [filename] [unittest_args]
```

### Arguments
- `filename` (optional): Path to the test distributions file (default: '.distributions')
- `--generate`: Generate new test distributions
- `unittest_args` (optional): Additional arguments to pass to unittest

## Test Cases
The test suite includes the following problem sets:
1. `abc` → `abd` : `efg` → ?
2. `abc` → `abd` : `ijk` → ?
3. `abc` → `abd` : `xyz` → ?
4. `abc` → `abd` : `ijkk` → ?
5. `abc` → `abd` : `mrrjjj` → ?

Each problem is run for 30 iterations by default.

## Features
- Generates and saves test distributions
- Runs statistical tests using chi-squared analysis
- Supports custom test distribution files
- Integrates with Python's unittest framework
- Provides detailed test output and error messages

## Dependencies
- Requires the `copycat` module
- Uses `unittest` for test framework
- Uses `pickle` for saving/loading test distributions
- Uses `argparse` for command-line argument parsing
- Uses `copycat.statistics` for statistical analysis

## Notes
- The test distributions are saved in a pickle file
- The test suite can be run with or without generating new distributions
- Statistical tests use the `iso_chi_squared` function from the copycat statistics module
- The test suite is designed to be extensible for adding new test cases 