# README_coderack.md

## Overview
`coderack.py` implements the Coderack, a key component of the Copycat system that manages the execution of codelets (small, focused procedures) that drive the analogical reasoning process. It handles the posting, selection, and execution of codelets based on their urgency and the current state of the system.

## Core Components
- `Coderack` class: Main class that manages codelet execution
- Codelet management system
- Urgency-based codelet selection

## Key Features
- Manages a collection of codelets (small procedures)
- Implements urgency-based codelet selection
- Supports both top-down and bottom-up codelet posting
- Handles codelet execution and removal
- Manages rule, correspondence, description, and group proposals

## Codelet Types
- Breaker codelets
- Description codelets (top-down and bottom-up)
- Bond codelets (top-down and bottom-up)
- Group codelets (top-down and whole-string)
- Rule codelets (scout, strength-tester, builder, translator)
- Correspondence codelets (bottom-up and important-object)
- Replacement finder codelets

## Main Methods
- `post(codelet)`: Add a codelet to the coderack
- `chooseAndRunCodelet()`: Select and execute a codelet
- `postTopDownCodelets()`: Post codelets from activated slipnet nodes
- `postBottomUpCodelets()`: Post codelets based on workspace state
- `proposeRule()`: Create and post a rule proposal
- `proposeCorrespondence()`: Create and post a correspondence proposal
- `proposeDescription()`: Create and post a description proposal
- `proposeGroup()`: Create and post a group proposal
- `proposeBond()`: Create and post a bond proposal

## Dependencies
- Requires `codeletMethods` module
- Uses `bond`, `codelet`, `correspondence`, `description`, `group`, and `rule` modules
- Uses `logging` for debug output
- Uses `math` for urgency calculations

## Notes
- Codelets are organized by urgency bins
- The system maintains a maximum of 100 codelets
- Codelet selection is influenced by temperature and workspace state
- The system supports both deterministic and probabilistic codelet posting
- Codelet urgency is calculated based on various factors including conceptual depth 