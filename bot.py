import pyautogui
import keyboard
import time
import pytesseract
from PIL import Image
import threading
import io

# Screenshots areas
region = (0, 440, 1920, 160)
region_typing = (0, 490, 1920, 140)

# Loop Values
running = False 
is_typing = False
bot_thread = None

# Delay between loops (adjust if needed)
screenshot_delay = 0.02
typing_delay = 0.008

# Colors to filter the image
text_color = (100, 102, 104)
background_color = (50, 52, 55)

def is_close_color(c1, c2, tolerance=20):
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2)) # Return true if the color is close to text color

def correct_image(screenshot):
    try:
        img = screenshot.convert("RGB")

        # Replace non-text colors with background color 
        pixel_data = [
            pixel if is_close_color(pixel, text_color) else background_color
            for pixel in img.getdata()
        ]

        new_img = Image.new("RGB", img.size)
        new_img.putdata(pixel_data)
        return new_img
    except Exception as e:
        print(f"⚠️ Error while correcting image: {e}")
        return screenshot

def get_text_from_screen():
    # Take a screenshot of the text to write
    region_to_capture = region_typing if is_typing else region
    screenshot = pyautogui.screenshot(region=region_to_capture)

    # Process image
    processed_img = correct_image(screenshot)

    # OCR without saving to disk
    buffer = io.BytesIO()
    processed_img.save(buffer, format="PNG")
    buffer.seek(0)
    image = Image.open(buffer)

    text = pytesseract.image_to_string(image, lang='eng').replace('\n', ' ')
    return text

def type_text(text_array):
    global running
    global is_typing
    is_typing = True

    # Type each character from the text array 
    for key in text_array:
        if not running:
            break
        keyboard.write(key)
        time.sleep(typing_delay)

def run():
    global running

    text = get_text_from_screen()
    
    if text.strip():
        text_array = list(text)
        type_text(text_array)
    else:
        print("🛑 No text detected. Stopping the bot.")
        running = False

def bot_loop():
    while running:
        run()
        time.sleep(screenshot_delay)

def start_bot():
    global running, bot_thread
    if not running:
        running = True
        print("🚀 Bot Started!")
        bot_thread = threading.Thread(target=bot_loop)
        bot_thread.start()

def stop_bot():
    global running
    running = False
    print("🛑 Bot Stopped.")

# Hotkeys
keyboard.add_hotkey('f1', start_bot)
keyboard.add_hotkey('f2', stop_bot)
print('ℹ️ Hit F1 to start and F2 to stop the bot (Make sure your browser is in full screen!)')

keyboard.wait()