#!/usr/bin/env python3
"""
AFK Automation Script

This script provides automated actions to prevent AFK (Away From Keyboard) detection
in games. It includes mouse movements, keyboard inputs, and chat messaging.

Controls:
- Right Shift: Pause/Resume the script
- Ctrl+C: Stop the script completely

WARNING: Use responsibly and in accordance with game terms of service.
"""

import random
import time
import threading
import sys
from typing import List, Tuple

try:
    import pydirectinput
    import pyautogui
    from pynput.keyboard import Controller, Key, Listener
    from pynput.mouse import Button
    from config import (
        MOUSE_MOVEMENT_STEPS, MOUSE_MOVEMENT_DELAY, MOUSE_ROTATION_DELAY,
        ACTION_TIMINGS, ACTION_DELAY_RANGE, CHAT_MESSAGE_INTERVAL,
        ENABLE_CHAT_MESSAGES, CHAT_MESSAGES, FAILSAFE_ENABLED
    )
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install required packages: pip install pydirectinput pyautogui pynput")
    print("Also ensure config.py is in the same directory.")
    sys.exit(1)


class AFKAutomation:
    """Main class for AFK automation functionality."""
    
    def __init__(self):
        self.keyboard = Controller()
        self.stop_afk = False
        self.paused = True
        self.listener = None
        
        # Load configuration
        self.messages = CHAT_MESSAGES
        self.actions = list(ACTION_TIMINGS.items())
        
        # Configure PyAutoGUI
        if FAILSAFE_ENABLED:
            pyautogui.FAILSAFE = True
        else:
            pyautogui.FAILSAFE = False

    def on_press(self, key):
        """Handle key press events."""
        if key == Key.shift_r:
            self.paused = not self.paused
            status = "paused" if self.paused else "resumed"
            print(f"Script {status}.")

    def smooth_move_mouse(self, target_x: int, target_y: int, steps: int = None, delay: float = None):
        """Smoothly move mouse to target position."""
        if self.stop_afk or self.paused:
            return
        
        steps = steps or MOUSE_MOVEMENT_STEPS
        delay = delay or MOUSE_MOVEMENT_DELAY
            
        current_x, current_y = pyautogui.position()
        step_x = (target_x - current_x) / steps
        step_y = (target_y - current_y) / steps

        for _ in range(steps):
            if self.stop_afk or self.paused:
                break
            current_x += step_x
            current_y += step_y
            pydirectinput.moveTo(int(current_x), int(current_y))
            time.sleep(delay)

    def rotate_mouse(self):
        """Continuously rotate mouse in random patterns."""
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        radius = min(screen_width, screen_height) // 4

        while not self.stop_afk:
            if self.paused:
                time.sleep(1)
                continue

            direction = random.choice(['positive', 'negative'])
            if direction == 'positive':
                target_x = center_x + radius * (1 + 0.5 * random.random())
            else:
                target_x = center_x - radius * (1 + 0.5 * random.random())
            target_y = center_y

            self.smooth_move_mouse(target_x, target_y)
            time.sleep(MOUSE_ROTATION_DELAY)

    def perform_key_action(self, key: str, duration: float):
        """Perform a single key action."""
        print(f"Pressing: {key} for {duration:.2f} seconds")
        
        if key == 'right':
            pydirectinput.mouseDown(button='right')
            time.sleep(duration)
            pydirectinput.mouseUp(button='right')
        elif key == 'left':
            pydirectinput.mouseDown(button='left')
            time.sleep(duration)
            pydirectinput.mouseUp(button='left')
        else:
            pydirectinput.keyDown(key)
            time.sleep(duration)
            pydirectinput.keyUp(key)
        
        print(f"Released: {key}")

    def perform_sequence(self):
        """Perform the main action sequence."""
        while not self.stop_afk:
            if self.paused:
                time.sleep(1)
                continue

            for key, duration_range in self.actions:
                if self.stop_afk or self.paused:
                    break

                duration = random.uniform(*duration_range)
                self.perform_key_action(key, duration)
                time.sleep(random.uniform(*ACTION_DELAY_RANGE))

    def type_message_in_chat(self):
        """Type random messages in chat."""
        last_message = None

        while not self.stop_afk:
            if self.paused:
                time.sleep(1)
                continue

            # Select a message different from the last one
            available_messages = [msg for msg in self.messages if msg != last_message]
            if not available_messages:
                available_messages = self.messages
            
            message = random.choice(available_messages)
            last_message = message

            # Temporarily pause other actions
            was_paused = self.paused
            self.paused = True
            time.sleep(1)

            # Open chat and send message
            self.keyboard.press(Key.enter)
            self.keyboard.release(Key.enter)
            time.sleep(0.5)
            
            self.keyboard.type(message)
            time.sleep(0.5)
            
            self.keyboard.press(Key.enter)
            self.keyboard.release(Key.enter)

            time.sleep(1)
            self.paused = was_paused

            # Wait before next message
            time.sleep(random.uniform(*CHAT_MESSAGE_INTERVAL))

    def start_keyboard_listener(self):
        """Start the keyboard listener for pause/resume control."""
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

    def start_afk_actions(self):
        """Start all AFK automation threads."""
        self.stop_afk = False
        
        # Start background threads
        threading.Thread(target=self.perform_sequence, daemon=True).start()
        threading.Thread(target=self.rotate_mouse, daemon=True).start()
        
        # Start chat messages if enabled
        if ENABLE_CHAT_MESSAGES:
            threading.Thread(target=self.type_message_in_chat, daemon=True).start()
            print("Chat messages enabled.")
        
        print("AFK actions started. Press Right Shift to pause or resume.")
        print("Press Ctrl+C to stop the script.")

    def stop(self):
        """Stop all automation activities."""
        self.stop_afk = True
        if self.listener:
            self.listener.stop()
        print("Script stopped.")

    def run(self):
        """Main run loop."""
        try:
            self.start_keyboard_listener()
            self.start_afk_actions()
            
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.stop()


def main():
    """Main entry point."""
    print("Starting AFK Automation Script...")
    print("WARNING: Use responsibly and in accordance with game terms of service.")
    print()
    
    afk_bot = AFKAutomation()
    afk_bot.run()


if __name__ == "__main__":
    main()