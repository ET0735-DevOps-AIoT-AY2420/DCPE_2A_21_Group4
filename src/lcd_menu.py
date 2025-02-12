import time
import queue
from threading import Thread

import RPi.GPIO as GPIO

from hal.hal_lcd import lcd
from hal.hal_keypad import init as keypad_init, get_key

# Queue for keypad input
shared_keypad_queue = queue.Queue()

def key_pressed(key):
    """Callback function to store keypress in queue."""
    print(f" Key Pressed: {key}")  # Debugging
    shared_keypad_queue.put(str(key))  # Ensure key is stored as a string

def wait_for_keypress():
    """Wait for a key press and return its value."""
    try:
        key = shared_keypad_queue.get(timeout=5)  # Timeout to prevent blocking
        print(f" Key Retrieved from Queue: {key}")  # Debugging
        return key
    except queue.Empty:
        # Print this message less frequently
        if time.time() % 10 < 0.1:  # Print once every 10 seconds
            print(" No key press detected (timeout).")  # Debugging
        return None  # Return None if no key is pressed

def keypad_polling():
    """Continuously poll for keypad input in a background thread."""
    while True:
        key = get_key()
        if key:
            print(f" Key Detected in Polling: {key}")  # Debugging
            key_pressed(key)
        time.sleep(0.1)  # Prevent CPU overuse

def display_main_menu(lcd_display):
    """Display the main menu on the LCD."""
    print(" Displaying Main Menu")  # Debugging
    lcd_display.lcd_clear()
    time.sleep(0.1)  # Allow LCD to refresh
    lcd_display.lcd_display_string("1Loan  2Collect", 1)
    lcd_display.lcd_display_string("3Return 4Fines", 2)

def handle_selection(option, lcd_display):
    """Execute the function based on user selection."""
    print(f" Handling Selection: {option}")  # Debugging
    lcd_display.lcd_clear()
    time.sleep(0.1)  # Allow LCD to refresh
    if option == '1':
        lcd_display.lcd_display_string("Loan Selected", 1)
    elif option == '2':
        lcd_display.lcd_display_string("Collect Book", 1)
    elif option == '3':
        lcd_display.lcd_display_string("Return Book", 1)
    elif option == '4':
        lcd_display.lcd_display_string("Check Fines", 1)
    time.sleep(2)
    print(" Returning to Main Menu")  # Debugging
    display_main_menu(lcd_display)

def main():
    # Initialize hardware components
    print(" Initializing system...")  # Debugging
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    keypad_init(key_pressed)  # Initialize keypad

    lcd_display = lcd()
    display_main_menu(lcd_display)

    # Start keypad polling in a separate thread
    keypad_thread = Thread(target=keypad_polling, daemon=True)
    keypad_thread.start()

    print(" System ready... Waiting for user input.")
    while True:
        key = wait_for_keypress()
        if key == '0':  # Stop condition: Press '0' to exit
            print(" Exiting the program...")
            lcd_display.lcd_clear()
            lcd_display.lcd_display_string("Exiting...", 1)
            time.sleep(2)
            break  # Exit the loop
        elif key and key in ['1', '2', '3', '4']:
            print(f" Key Accepted: {key}")  # Debugging
            handle_selection(key, lcd_display)
        else:
            print(" Invalid or No Key Pressed")  # Debugging
        time.sleep(0.1)  # Prevent CPU overuse

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(" Program interrupted by user.")
    finally:
        GPIO.cleanup()  # Clean up GPIO resources