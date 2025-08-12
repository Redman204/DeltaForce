# AFK Script

A Python script that performs automated actions to keep applications/games active while you're away.

## Features

- **Mouse Movement**: Smooth circular mouse movements to prevent screen saver
- **Keyboard Input**: Random key presses and sequences (WASD, space, ctrl, etc.)
- **Chat Messages**: Automated typing of random messages in chat
- **Pause/Resume**: Press Right Shift to pause or resume the script
- **Safe Exit**: Use Ctrl+C to stop the script

## Installation

1. Install Python 3.7+ if you haven't already
2. Install the required dependencies:
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

3. The script will start automatically and begin performing actions

## What it does

- Moves the mouse in circular patterns
- Presses random keys (WASD, space, ctrl, etc.) for random durations
- Types random chat messages every 30-60 seconds
- All actions are randomized to appear more human-like

## Safety Features

- Script starts in paused state
- Easy pause/resume with Right Shift
- Clean exit with Ctrl+C
- All actions can be stopped immediately

## Warning

⚠️ **Use responsibly**: This script is designed for legitimate AFK prevention in games/applications. Make sure you have permission to use automation tools in your target application.

## Dependencies

- `pydirectinput`: Direct input simulation
- `pyautogui`: Mouse and keyboard control
- `pynput`: Keyboard listener for controls
