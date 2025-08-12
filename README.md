# AFK Script

A Python script that simulates user input to keep applications/games active while you're away.

## Features

- **Mouse Movement**: Smooth circular mouse movements to prevent screen lock
- **Keyboard Input**: Random key presses and sequences
- **Chat Messages**: Automatic typing of predefined messages
- **Pause/Resume**: Use Right Shift to pause or resume the script
- **Safe Exit**: Press Ctrl+C to stop the script

## Installation

1. Install Python 3.7 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```bash
   python afk_script.py
   ```

2. **Controls**:
   - **Right Shift**: Pause/Resume the script
   - **Ctrl+C**: Stop the script completely

3. The script will start automatically and begin:
   - Moving the mouse in circular patterns
   - Pressing random keys
   - Typing chat messages every 30-60 seconds

## Safety Features

- Script starts in paused state
- Can be paused/resumed with Right Shift
- Graceful shutdown with Ctrl+C
- All actions respect the pause state

## Warning

⚠️ **Use responsibly**: This script is designed for legitimate AFK prevention in games/applications where you have permission to use such tools. Always follow the terms of service of the applications you're using.

## Requirements

- Python 3.7+
- Windows (for pydirectinput compatibility)
- Required packages listed in requirements.txt
