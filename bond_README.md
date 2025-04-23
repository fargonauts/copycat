# README_bond.md

## Overview
`bond.py` implements the Bond system, a key component of the Copycat system that manages the relationships between objects in strings. It handles the creation, evaluation, and management of bonds that represent meaningful connections between objects based on their properties and relationships.

## Core Components
- `Bond` class: Main class that represents a bond between objects
- Bond evaluation system
- Bond compatibility management

## Key Features
- Manages bonds between objects in strings
- Evaluates bond strength based on multiple factors
- Handles bond direction and category
- Supports bond flipping and versioning
- Manages bond compatibility and support

## Bond Components
- `source`: Source object of the bond
- `destination`: Destination object of the bond
- `category`: Category of the bond
- `facet`: Aspect of the bond
- `directionCategory`: Direction of the bond
- `sourceDescriptor`: Descriptor of the source object
- `destinationDescriptor`: Descriptor of the destination object

## Main Methods
- `updateInternalStrength()`: Calculate internal bond strength
- `updateExternalStrength()`: Calculate external bond strength
- `buildBond()`: Create and establish bond
- `breakBond()`: Remove bond
- `localSupport()`: Calculate local support
- `numberOfLocalSupportingBonds()`: Count supporting bonds
- `sameCategories()`: Compare bond categories
- `localDensity()`: Calculate local bond density

## Bond Types
- Letter category bonds
- Direction-based bonds
- Category-based bonds
- Flipped bonds
- Modified bonds

## Dependencies
- Requires `workspaceStructure` module
- Used by the main `copycat` module

## Notes
- Bonds are evaluated based on member compatibility and facet factors
- The system supports both same-type and different-type bonds
- Bonds can have direction categories (left, right)
- The system handles bond compatibility and support
- Bonds can be flipped to create alternative versions
- Local density and support factors influence bond strength 