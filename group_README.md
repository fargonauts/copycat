# README_group.md

## Overview
`group.py` implements the Group system, a key component of the Copycat system that manages the grouping of objects in strings. It handles the creation, evaluation, and management of groups that represent meaningful collections of objects based on their properties and relationships.

## Core Components
- `Group` class: Main class that represents a group of objects
- Group evaluation system
- Group description management

## Key Features
- Manages groups of objects in strings
- Evaluates group strength based on multiple factors
- Handles group descriptions and bond descriptions
- Supports group flipping and versioning
- Manages group compatibility and support

## Group Components
- `groupCategory`: Category of the group
- `directionCategory`: Direction of the group
- `facet`: Aspect of the group
- `objectList`: List of objects in the group
- `bondList`: List of bonds in the group
- `descriptions`: List of group descriptions
- `bondDescriptions`: List of bond descriptions

## Main Methods
- `updateInternalStrength()`: Calculate internal group strength
- `updateExternalStrength()`: Calculate external group strength
- `buildGroup()`: Create and establish group
- `breakGroup()`: Remove group
- `localSupport()`: Calculate local support
- `numberOfLocalSupportingGroups()`: Count supporting groups
- `sameGroup()`: Compare groups for equality

## Group Types
- Single letter groups
- Multi-letter groups
- Direction-based groups
- Category-based groups
- Length-based groups

## Dependencies
- Requires `description`, `workspaceObject`, and `formulas` modules
- Used by the main `copycat` module

## Notes
- Groups are evaluated based on bond association and length
- The system supports both single and multi-object groups
- Groups can have multiple descriptions and bond descriptions
- The system handles group compatibility and support
- Groups can be flipped to create alternative versions
- Length descriptions are probabilistically added based on temperature 