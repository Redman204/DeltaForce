import random
import time
import threading
import pydirectinput
import pyautogui
from pynput.keyboard import Controller, Key, Listener
from pynput.mouse import Button
 
keyboard = Controller()
stop_afk = False
paused = True
 
def on_press(key):
    global paused
    if key == Key.shift_r:
        paused = not paused
        if paused:
            print("Script paused.")
        else:
            print("Script resumed.")
 
def smooth_move_mouse(target_x, target_y, steps=100, delay=0.001):
    current_x, current_y = pyautogui.position()
    step_x = (target_x - current_x) / steps
    step_y = (target_y - current_y) / steps
 
    for _ in range(steps):
        if stop_afk or paused:
            break
        current_x += step_x
        current_y += step_y
        pydirectinput.moveTo(int(current_x), int(current_y))
        time.sleep(delay)
 
def rotate_mouse():
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    radius = min(screen_width, screen_height) // 4
 
    while not stop_afk:
        if paused:
            time.sleep(1)
            continue
 
        direction = random.choice(['positive', 'negative'])
        if direction == 'positive':
            target_x = center_x + radius * (1 + 0.5 * random.random())
        else:
            target_x = center_x - radius * (1 + 0.5 * random.random())
        target_y = center_y
 
        smooth_move_mouse(target_x, target_y)
        time.sleep(0.01)
 
def perform_sequence():
    while not stop_afk:
        if paused:
            time.sleep(1)
            continue
 
        actions = [
            ('w', random.uniform(0.5, 1.5)),
            ('d', random.uniform(0.5, 1.5)),
            ('q', random.uniform(0.1, 0.3)),
            ('s', random.uniform(0.5, 1.5)),
            ('a', random.uniform(0.5, 1.5)),
            ('space', random.uniform(0.1, 0.3)),
            ('e', random.uniform(0.1, 0.3)),
            ('ctrl', random.uniform(0.1, 0.3)),
            ('v', random.uniform(0.1, 0.3)),
            ('right', random.uniform(0.5, 1)),
            ('ctrl', random.uniform(0.1, 0.3)),
            ('left', random.uniform(0.3, 0.8)),
            ('r', random.uniform(0.1, 0.3)),
        ]
 
        for key, duration in actions:
            if stop_afk or paused:
                break
 
            print(f"Pressing: {key} for {duration:.2f} seconds")
 
            if key == 'right':
                pydirectinput.mouseDown(button='right')
                time.sleep(duration)
                pydirectinput.mouseUp(button='right')
            if key == 'left':
                pydirectinput.mouseDown(button='left')
                time.sleep(duration)
                pydirectinput.mouseUp(button='left')
            else:
                pydirectinput.keyDown(key)
                time.sleep(duration)
                pydirectinput.keyUp(key)
 
            print(f"Released: {key}")
 
            time.sleep(random.uniform(0.5, 1.3))
 
def type_message_in_chat():
    global paused
    messages = [
        "hi", "came here", "unlocky bro", "i have 100.000 cash", "you have uav", "okey", "yes", "yes yes!",
        "what's up?", "anyone here?", "let's go!", "nice game", "good luck", "well played", "gg", "brb",
        "afk for a bit", "back now", "let's win this", "teamwork!", "focus up", "let's push", "defend!",
        "attack now", "need help", "on my way", "wait for me", "let's regroup", "nice shot!", "great job",
        "thanks!", "no problem", "sorry!", "my bad", "let's try again", "next round", "we got this",
        "keep it up", "don't give up", "almost there", "victory!", "defeat...", "next time", "good game",
        "well played everyone", "let's do better", "practice makes perfect", "see you next time", "bye!"
    ]
    last_message = None
 
    while not stop_afk:
        if paused:
            time.sleep(1)
            continue
 
        available_messages = [msg for msg in messages if msg != last_message]
        if not available_messages:
            available_messages = messages
        message = random.choice(available_messages)
        last_message = message
 
        paused = True
        time.sleep(1)
 
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(0.5)
        keyboard.type(message)
        time.sleep(0.5)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
 
        time.sleep(1)
        paused = False
 
        time.sleep(random.uniform(30, 60))
 
def start_afk_actions():
    global stop_afk
    stop_afk = False
    threading.Thread(target=perform_sequence, daemon=True).start()
    threading.Thread(target=rotate_mouse, daemon=True).start()
    print("AFK actions started. Press Right Shift to pause or resume.")
 
listener = Listener(on_press=on_press)
listener.start()
 
start_afk_actions()
 
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stop_afk = True
    print("Script stopped.")