# Codelet System

## Overview
The codelet system is a fundamental component of the Copycat architecture that defines the basic structure and behavior of codelets. Codelets are small, specialized agents that perform specific operations in the workspace, forming the basis of the system's parallel processing capabilities.

## Key Features
- Codelet structure
- Behavior definition
- Priority management
- State tracking
- Execution control

## Codelet Types
1. **Basic Codelets**
   - Scout codelets
   - Builder codelets
   - Evaluator codelets
   - Breaker codelets

2. **Specialized Codelets**
   - Group codelets
   - Bond codelets
   - Correspondence codelets
   - Rule codelets

3. **Control Codelets**
   - Temperature codelets
   - Pressure codelets
   - Urgency codelets
   - Cleanup codelets

## Usage
Codelets are created and managed through the codelet system:

```python
# Create a codelet
codelet = Codelet(name, priority)

# Set behavior
''''
The behavior parameter would typically be a reference to one of the **many codelet methods defined in codeletMethods.py**.
For example, a codelet might be assigned a behavior like:
build_group - to create a new group of related elements
evaluate_bond - to assess the strength of a bond
scout_for_correspondence - to look for potential mappings between structures
The behavior is what gives each codelet its purpose and role in the system's parallel processing architecture. When the codelet is executed via codelet.run(), it performs this assigned behavior in the context of the current workspace state.
'''
codelet.set_behavior(behavior)

# Execute codelet
result = codelet.run()
```

## Dependencies
- Python 3.x
- No external dependencies required

## Related Components
- Coderack: Manages codelet execution
- CodeletMethods: Provides codelet behaviors
- Workspace: Environment for codelets
- Temperature: Influences codelet behavior 