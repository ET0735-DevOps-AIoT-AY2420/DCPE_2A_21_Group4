import time
import queue
from threading import Thread

import RPi.GPIO as GPIO

from hal.hal_lcd import lcd
from hal.hal_servo import set_servo_position
from hal.hal_usonic import init as usonic_init, get_distance
from hal.hal_keypad import init as keypad_init, get_key
from barcode_scanner import scan_barcode
from database import get_db_connection

# 🔄 Queue for keypad input
shared_keypad_queue = queue.Queue()

def key_pressed(key):
    """Callback function to store keypress in queue."""
    shared_keypad_queue.put(key)
    print(f" Key Pressed: {key}")  # Debugging

def wait_for_keypress():
    """Wait for a key press and return its value."""
    key = shared_keypad_queue.get()
    return key

def main():
    #  Initialize hardware components
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    usonic_init()
    keypad_init(key_pressed)  #  Fix: Assign callback function

    #  Start keypad polling in background thread
    keypad_thread = Thread(target=get_key, daemon=True)
    keypad_thread.start()

    lcd_display = lcd()
    lcd_display.lcd_display_string("Hello",1)
    
    print("System ready... Waiting for user presence.")

    while True:
        distance = get_distance()
        if distance < 10:  # Detect presence
            lcd_display.lcd_clear()
            lcd_display.lcd_display_string("1. Collect Book", 1)
            lcd_display.lcd_display_string("2. Return Book", 2)
            time.sleep(2)
            lcd_display.lcd_clear()

            print("Waiting for key press...")
            key = wait_for_keypress()  # Fix: Properly wait for key press

            if key == 1:  # Collect Book Process
                lcd_display.lcd_display_string("Scan Your QR Code", 1)
                user = scan_barcode()

                if user:
                    lcd_display.lcd_clear()
                    lcd_display.lcd_display_string("Enter Book Code", 1)
                    time.sleep(2)
                    lcd_display.lcd_clear()

                    print("Waiting for book code entry...")
                    book_code = wait_for_keypress()  # Fix: Properly wait for book code entry
                    print(f" Book Code Entered: {book_code}")  # Debugging

                    if verify_book_code(book_code, user['id']):
                        lcd_display.lcd_display_string("Book Dispensing", 1)
                        set_servo_position(90)  # Unlock book compartment
                        time.sleep(3)
                        set_servo_position(0)  # Lock again
                        lcd_display.lcd_clear()
                        lcd_display.lcd_display_string("Take Your Book", 1)
                        time.sleep(3)
                        lcd_display.lcd_clear()
                    else:
                        lcd_display.lcd_display_string("Invalid Book Code", 1)
                        time.sleep(2)
                        lcd_display.lcd_clear()

        time.sleep(1)  # Avoid unnecessary CPU usage

def verify_book_code(book_code, user_id):
    """Verify if the book is reserved by the user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM loans WHERE bookId = ? AND userId = ? AND returnDate IS NULL", (book_code, user_id))
    book = cursor.fetchone()
    conn.close()
    return bool(book)

if __name__ == "__main__":
    main()