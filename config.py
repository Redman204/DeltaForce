"""
Configuration file for AFK Automation Script
Modify these settings to customize the behavior of the automation.
"""

# Mouse movement settings
MOUSE_MOVEMENT_STEPS = 100
MOUSE_MOVEMENT_DELAY = 0.001
MOUSE_ROTATION_DELAY = 0.01

# Action timing settings (min, max) in seconds
ACTION_TIMINGS = {
    'w': (0.5, 1.5),        # Forward movement
    'd': (0.5, 1.5),        # Right movement
    'q': (0.1, 0.3),        # Quick action
    's': (0.5, 1.5),        # Backward movement
    'a': (0.5, 1.5),        # Left movement
    'space': (0.1, 0.3),    # Jump/action
    'e': (0.1, 0.3),        # Interact
    'ctrl': (0.1, 0.3),     # Crouch/control
    'v': (0.1, 0.3),        # Melee/action
    'right': (0.5, 1.0),    # Right mouse button
    'left': (0.3, 0.8),     # Left mouse button
    'r': (0.1, 0.3),        # Reload
}

# Delay between actions (min, max) in seconds
ACTION_DELAY_RANGE = (0.5, 1.3)

# Chat message settings
CHAT_MESSAGE_INTERVAL = (30, 60)  # Seconds between messages (min, max)
ENABLE_CHAT_MESSAGES = False      # Set to True to enable chat messages

# Custom chat messages (you can modify this list)
CHAT_MESSAGES = [
    "hi", "came here", "unlucky bro", "i have 100.000 cash", "you have uav", "okay", "yes", "yes yes!",
    "what's up?", "anyone here?", "let's go!", "nice game", "good luck", "well played", "gg", "brb",
    "afk for a bit", "back now", "let's win this", "teamwork!", "focus up", "let's push", "defend!",
    "attack now", "need help", "on my way", "wait for me", "let's regroup", "nice shot!", "great job",
    "thanks!", "no problem", "sorry!", "my bad", "let's try again", "next round", "we got this",
    "keep it up", "don't give up", "almost there", "victory!", "defeat...", "next time", "good game",
    "well played everyone", "let's do better", "practice makes perfect", "see you next time", "bye!"
]

# Safety settings
FAILSAFE_ENABLED = True  # Enable PyAutoGUI failsafe (move mouse to corner to stop)