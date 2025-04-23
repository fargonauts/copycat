# README_correspondence.md

## Overview
`correspondence.py` implements the Correspondence system, a key component of the Copycat system that manages the mapping relationships between objects in the initial and target strings. It handles the creation, evaluation, and management of correspondences that link objects based on their properties and relationships.

## Core Components
- `Correspondence` class: Main class that represents a mapping between objects
- Concept mapping system
- Correspondence strength evaluation

## Key Features
- Manages mappings between objects in initial and target strings
- Evaluates correspondence strength based on multiple factors
- Handles concept slippages and mappings
- Supports both direct and accessory concept mappings
- Manages correspondence compatibility and support

## Correspondence Components
- `objectFromInitial`: Object from the initial string
- `objectFromTarget`: Object from the target string
- `conceptMappings`: List of concept mappings
- `accessoryConceptMappings`: Additional concept mappings
- `flipTargetObject`: Flag for target object flipping

## Main Methods
- `updateInternalStrength()`: Calculate internal correspondence strength
- `updateExternalStrength()`: Calculate external correspondence strength
- `buildCorrespondence()`: Create and establish correspondence
- `breakCorrespondence()`: Remove correspondence
- `incompatible()`: Check correspondence compatibility
- `supporting()`: Check if correspondence supports another
- `internallyCoherent()`: Check internal coherence

## Concept Mapping Types
- Distinguishing mappings
- Relevant distinguishing mappings
- Bond mappings
- Direction mappings
- Symmetric mappings

## Dependencies
- Requires `conceptMapping`, `group`, `letter`, and `workspaceStructure` modules
- Uses `formulas` for mapping calculations
- Used by the main `copycat` module

## Notes
- Correspondences are evaluated based on concept mapping strength and coherence
- The system supports both direct and indirect concept mappings
- Correspondences can be incompatible with each other
- The system handles both letter and group correspondences
- Concept slippages are tracked and managed 