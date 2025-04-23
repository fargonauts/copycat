# README_slipnet.md

## Overview
`slipnet.py` implements the Slipnet, a key component of the Copycat system that represents the conceptual network of relationships between different concepts. It manages a network of nodes (concepts) and links (relationships) that are used in analogical reasoning.

## Core Components
- `Slipnet` class: Main class that manages the conceptual network
- Network of `Slipnode` objects representing concepts
- Network of `Sliplink` objects representing relationships

## Key Features
- Manages a network of conceptual nodes and their relationships
- Handles activation spreading between nodes
- Supports both slip and non-slip links
- Implements various types of relationships:
  - Letter categories
  - String positions
  - Alphabetic positions
  - Directions
  - Bond types
  - Group types
  - Other relations

## Node Types
- Letters (a-z)
- Numbers (1-5)
- String positions (leftmost, rightmost, middle, single, whole)
- Alphabetic positions (first, last)
- Directions (left, right)
- Bond types (predecessor, successor, sameness)
- Group types (predecessorGroup, successorGroup, samenessGroup)
- Categories (letterCategory, stringPositionCategory, etc.)

## Link Types
- Slip links (lateral connections)
- Non-slip links (fixed connections)
- Category links (hierarchical connections)
- Instance links (specific examples)
- Property links (attributes)
- Opposite links (antonyms)

## Dependencies
- Requires `slipnode` and `sliplink` modules
- Used by the main `copycat` module

## Notes
- The network is initialized with predefined nodes and links
- Activation spreads through the network during reasoning
- Some nodes are initially clamped to high activation
- The network supports both hierarchical and lateral relationships
- The system uses conceptual depth to determine link strengths 