# Randomness System

## Overview
The randomness system is a utility component of the Copycat architecture that provides controlled random number generation and probabilistic operations. This system ensures consistent and reproducible random behavior across the analogical reasoning process.

## Key Features
- Random number generation
- Probability distributions
- State management
- Seed control
- Reproducibility

## Operation Types
1. **Basic Operations**
   - Random number generation
   - Probability sampling
   - Distribution selection
   - State initialization

2. **Advanced Operations**
   - Weighted selection
   - Distribution mixing
   - State transitions
   - Pattern generation

3. **Special Operations**
   - Seed management
   - State persistence
   - Debug control
   - Test reproducibility

## Usage
Random operations are performed through the randomness system:

```python
# Generate a random number
value = randomness.random()

# Sample from a distribution
sample = randomness.sample(distribution)

# Set random seed
randomness.set_seed(seed)
```

## Dependencies
- Python 3.x
- No external dependencies required

## Related Components
- Codelets: Use randomness for selection
- Temperature: Uses randomness for control
- Statistics: Uses randomness for sampling
- Workspace: Uses randomness for operations 