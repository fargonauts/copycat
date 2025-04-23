# README_workspace.md

## Overview
`workspace.py` implements the Workspace, a central component of the Copycat system that manages the current state of the analogical reasoning process. It maintains the strings being compared, their objects, structures, and the overall state of the reasoning process.

## Core Components
- `Workspace` class: Main class that manages the reasoning workspace
- `WorkspaceString` objects for initial, modified, and target strings
- Collection of objects and structures (bonds, correspondences, etc.)

## Key Features
- Manages the three strings involved in the analogy (initial, modified, target)
- Tracks objects and their relationships
- Maintains structures like bonds, correspondences, and rules
- Calculates various unhappiness metrics
- Updates object values and structure strengths
- Manages the temperature-based control system

## Main Methods
- `resetWithStrings(initial, modified, target)`: Initialize workspace with new strings
- `updateEverything()`: Update all objects and structures
- `getUpdatedTemperature()`: Calculate current temperature
- `buildRule(rule)`: Add or replace the current rule
- `breakRule()`: Remove the current rule
- `buildDescriptions(objekt)`: Add descriptions to an object

## State Management
- Tracks total, intra-string, and inter-string unhappiness
- Maintains lists of objects and structures
- Manages the current rule and final answer
- Tracks changed objects and their correspondences

## Dependencies
- Requires `formulas`, `bond`, `correspondence`, `letter`, and `workspaceString` modules
- Used by the main `copycat` module

## Notes
- The workspace is the central state container for the reasoning process
- Unhappiness metrics guide the temperature-based control system
- The system supports both rule-based and correspondence-based reasoning
- Objects can have multiple descriptions and relationships
- The workspace maintains the final answer when reasoning is complete 