# Curses Reporter System

## Overview
The curses reporter system is a visualization component of the Copycat architecture that provides a terminal-based user interface for monitoring and debugging the system's operation. This system uses the curses library to create an interactive display of the system's state.

## Key Features
- Real-time state display
- Interactive monitoring
- Debug information
- System metrics visualization
- User input handling

## Display Components
1. **Main Display**
   - Workspace visualization
   - Slipnet state
   - Coderack status
   - Correspondence view

2. **Debug Panels**
   - Codelet execution
   - Activation levels
   - Mapping strengths
   - Error messages

3. **Control Interface**
   - User commands
   - System controls
   - Display options
   - Navigation

## Usage
The curses reporter is used to monitor the system:

```python
# Initialize the reporter
reporter = CursesReporter()

# Update the display
reporter.update_display()

# Handle user input
reporter.process_input()
```

## Dependencies
- Python 3.x
- curses library
- No other external dependencies required

## Related Components
- Workspace: Provides state to display
- Slipnet: Provides activation information
- Coderack: Provides execution status
- Correspondence: Provides mapping information 