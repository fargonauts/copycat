# README_rule.md

## Overview
`rule.py` implements the Rule system, a key component of the Copycat system that manages the transformation rules used in analogical reasoning. It handles the creation, evaluation, and application of rules that describe how to transform strings based on their properties and relationships.

## Core Components
- `Rule` class: Main class that represents a transformation rule
- Rule evaluation system
- Rule translation and application system

## Key Features
- Defines transformation rules with facets, descriptors, categories, and relations
- Evaluates rule strength based on multiple factors
- Supports rule translation through concept slippages
- Handles string transformations based on rules
- Manages rule compatibility with correspondences

## Rule Components
- `facet`: The aspect of the object to change (e.g., length)
- `descriptor`: The property being changed
- `category`: The type of object being changed
- `relation`: The transformation to apply

## Main Methods
- `updateInternalStrength()`: Calculate rule strength
- `updateExternalStrength()`: Update external strength
- `activateRuleDescriptions()`: Activate rule-related concepts
- `buildTranslatedRule()`: Apply rule to target string
- `incompatibleRuleCorrespondence()`: Check rule-correspondence compatibility
- `ruleEqual()`: Compare rules for equality

## Rule Types
- Length-based rules (predecessor, successor)
- Character-based rules (predecessor, successor)
- Category-based rules

## Dependencies
- Requires `workspaceStructure` and `formulas` modules
- Uses `logging` for debug output
- Used by the main `copycat` module

## Notes
- Rules are evaluated based on conceptual depth and descriptor sharing
- Rule strength is calculated using weighted averages
- Rules can be translated through concept slippages
- The system supports both single-character and length-based transformations
- Rules can be incompatible with certain correspondences 