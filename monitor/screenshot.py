import threading
import time
import pyautogui
import os
from datetime import datetime

def take_screenshot():
    folder = "screenshots"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    print(f"[+] Screenshot saved: {filename}")

def screenshot_loop():
    while True:
        take_screenshot()
        time.sleep(300)  # every 5 minutes

def start_screenshot_thread():
    t = threading.Thread(target=screenshot_loop, daemon=True)
    t.start()
