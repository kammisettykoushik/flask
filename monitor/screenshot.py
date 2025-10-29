import os

# ✅ Create a fake DISPLAY environment before importing pyautogui
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":99"

from xvfbwrapper import Xvfb
import threading
import time
import pyautogui
from datetime import datetime

def take_screenshot():
    # 1. Start the Virtual Display (This resolves the 'DISPLAY' error)
    vdisplay = Xvfb()
    vdisplay.start()
    
    try:
        folder = "screenshots"
        os.makedirs(folder, exist_ok=True)
        filename = f"{folder}/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        # 2. PyAutoGUI runs successfully inside the virtual display
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        
        print(f"[+] Screenshot saved: {filename}")
        
    except Exception as e:
        print(f"[-] Error taking screenshot: {e}")
        
    finally:
        # 3. Stop the virtual display immediately
        vdisplay.stop()

def screenshot_loop():
    # It's generally better to let the web app handle long-running tasks
    # as scheduled tasks or external processes on PythonAnywhere, 
    # but this threading structure will technically execute the task.
    while True:
        take_screenshot()
        time.sleep(300)


def start_screenshot_thread():
    # Ensure this thread starts *after* your Flask/Django application is fully set up.
    t = threading.Thread(target=screenshot_loop, daemon=True)
    t.start()

# NOTE: You MUST have installed the library: pip install xvfbwrapper


# import threading
# import time
# import pyautogui
# import os
# from datetime import datetime

# def take_screenshot():
#     folder = "screenshots"
#     os.makedirs(folder, exist_ok=True)
#     filename = f"{folder}/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
#     screenshot = pyautogui.screenshot()
#     screenshot.save(filename)
#     print(f"[+] Screenshot saved: {filename}")

# def screenshot_loop():
#     while True:
#         take_screenshot()
#         time.sleep(300)  # every 5 minutes

# def start_screenshot_thread():
#     t = threading.Thread(target=screenshot_loop, daemon=True)
#     t.start()
