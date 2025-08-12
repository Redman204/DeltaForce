# AFK Automation Script

An advanced automation script designed to prevent AFK (Away From Keyboard) detection in games through simulated mouse movements, keyboard inputs, and optional chat messages.

## ⚠️ IMPORTANT WARNINGS

- **Use responsibly** and in accordance with game terms of service
- Some games **prohibit automation tools** and may result in account penalties
- This script may **trigger anti-cheat systems**
- **Use at your own risk**

## Features

- **Mouse Automation**: Smooth mouse movements in random patterns
- **Keyboard Simulation**: Configurable key sequences with random timing
- **Chat Messages**: Optional automated chat messages (disabled by default)
- **Pause/Resume**: Real-time control with Right Shift key
- **Safety Features**: PyAutoGUI failsafe and graceful shutdown
- **Configurable**: Easy customization through configuration files

## Installation

1. **Clone or download** the script files to a directory
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

Run the launcher script for guided setup:
```bash
python run_afk.py
```

### Direct Execution

Alternatively, run the main script directly:
```bash
python afk_automation.py
```

### Controls

- **Right Shift**: Pause/Resume the automation
- **Ctrl+C**: Stop the script completely
- **Mouse to top-left corner**: Emergency stop (if failsafe enabled)

## Configuration

Edit `config.py` to customize the behavior:

### Mouse Settings
```python
MOUSE_MOVEMENT_STEPS = 100      # Smoothness of mouse movement
MOUSE_MOVEMENT_DELAY = 0.001    # Delay between mouse steps
MOUSE_ROTATION_DELAY = 0.01     # Delay between mouse rotations
```

### Action Timings
```python
ACTION_TIMINGS = {
    'w': (0.5, 1.5),        # Forward movement (min, max seconds)
    'd': (0.5, 1.5),        # Right movement
    # ... customize other keys
}
```

### Chat Messages
```python
ENABLE_CHAT_MESSAGES = False    # Set to True to enable
CHAT_MESSAGE_INTERVAL = (30, 60)  # Interval between messages
CHAT_MESSAGES = [
    "hi", "good game", "gg"     # Customize your messages
]
```

### Safety Settings
```python
FAILSAFE_ENABLED = True         # PyAutoGUI failsafe feature
```

## File Structure

```
afk_automation/
├── afk_automation.py    # Main automation script
├── config.py           # Configuration settings
├── run_afk.py         # User-friendly launcher
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## How It Works

1. **Mouse Movement**: Creates smooth, random mouse movements to simulate user activity
2. **Keyboard Actions**: Performs randomized key sequences with configurable timing
3. **Chat System**: Optionally sends random chat messages at intervals
4. **Threading**: Uses separate threads for different automation tasks
5. **Control System**: Monitors for pause/resume commands via keyboard listener

## Customization

### Adding New Actions

Edit the `ACTION_TIMINGS` dictionary in `config.py`:
```python
ACTION_TIMINGS = {
    'your_key': (min_seconds, max_seconds),
    # ... other actions
}
```

### Custom Chat Messages

Modify the `CHAT_MESSAGES` list in `config.py`:
```python
CHAT_MESSAGES = [
    "your custom message",
    "another message",
    # ... more messages
]
```

## Troubleshooting

### Dependencies Issues
- Ensure all packages are installed: `pip install -r requirements.txt`
- On Linux, you may need additional permissions for input simulation

### Permission Issues
- On macOS: Grant accessibility permissions in System Preferences
- On Linux: Ensure your user has input device permissions

### Anti-virus Warnings
- Some anti-virus software may flag automation tools
- Add exceptions if you trust the software

## Technical Details

### Dependencies
- `pydirectinput`: Direct input simulation
- `pyautogui`: Screen interaction and mouse control
- `pynput`: Keyboard and mouse event handling
- `Pillow`: Image processing (required by pyautogui)

### Threading Architecture
- Main thread: User interface and control
- Worker thread 1: Keyboard action sequences
- Worker thread 2: Mouse movement patterns
- Worker thread 3: Chat message system (if enabled)

## Legal and Ethical Considerations

- **Game Terms of Service**: Always check if automation is allowed
- **Fair Play**: Consider the impact on other players
- **Account Safety**: Understand the risks to your gaming accounts
- **Responsible Use**: Don't use this to gain unfair advantages

## Support

This script is provided as-is for educational purposes. Users are responsible for:
- Understanding their game's terms of service
- Accepting risks associated with automation tools
- Using the software ethically and responsibly

## License

This project is provided for educational purposes. Use at your own risk and responsibility.
