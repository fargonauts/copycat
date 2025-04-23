# README_temperature.md

## Overview
`temperature.py` implements the Temperature system, a crucial component of the Copycat system that controls the balance between exploration and exploitation during analogical reasoning. It provides various formulas for adjusting probabilities based on the current temperature, which affects how the system makes decisions.

## Core Components
- `Temperature` class: Main class that manages the temperature system
- Multiple adjustment formulas for probability modification
- Temperature history tracking

## Key Features
- Manages temperature-based control of the reasoning process
- Provides multiple formulas for probability adjustment
- Supports temperature clamping and unclamping
- Tracks temperature history and differences
- Allows dynamic switching between adjustment formulas

## Adjustment Formulas
- `original`: Basic temperature-based adjustment
- `entropy`: Entropy-based adjustment
- `inverse`: Inverse weighted adjustment
- `fifty_converge`: Convergence to 0.5
- `soft_curve`: Soft curve adjustment
- `weighted_soft_curve`: Weighted soft curve
- `alt_fifty`: Alternative fifty convergence
- `average_alt`: Averaged alternative
- `best`: Working best formula
- `sbest`: Soft best formula
- `pbest`: Parameterized best
- `meta`: Meta-level adjustment
- `pmeta`: Parameterized meta
- `none`: No adjustment

## Main Methods
- `update(value)`: Update temperature value
- `clampUntil(when)`: Clamp temperature until specified time
- `tryUnclamp(currentTime)`: Attempt to unclamp temperature
- `value()`: Get current temperature
- `getAdjustedProbability(value)`: Get temperature-adjusted probability
- `useAdj(adj)`: Switch to different adjustment formula

## Dependencies
- Uses `math` for mathematical operations
- Used by the main `copycat` module

## Notes
- Temperature starts at 100.0 and can be clamped
- Lower temperatures encourage more conservative decisions
- Higher temperatures allow more exploratory behavior
- The system tracks average differences between adjusted and original probabilities
- Different adjustment formulas can be used for different reasoning strategies 