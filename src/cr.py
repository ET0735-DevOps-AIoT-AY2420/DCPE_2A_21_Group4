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
current_user_id = None  # Store authenticated user ID

def key_pressed(key):
    """Callback function to store keypress in queue."""
    shared_keypad_queue.put(str(key))  # Convert to string
    print(f" Key Pressed: {key}")  # Debugging

def verify_and_remove_loan(book_isbn, user_id):
    """Check if the book is loaned by the authenticated user and remove it on return."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if isinstance(book_isbn, dict) and "data" in book_isbn and "isbn" in book_isbn["data"]:
        book_isbn = book_isbn["data"]["isbn"]  # ✅ Extract the ISBN correctly

    print(f"🔍 Checking loan for Book ISBN: {book_isbn}, User ID: {user_id}")

    cursor.execute("SELECT * FROM loans WHERE isbn = ? AND userId = ? AND returnDate IS NULL", 
                   (book_isbn, user_id))
    loan = cursor.fetchone()
    
    if loan:
        print(f"✅ Loan Found: {loan}. Returning the book...")
        cursor.execute("DELETE FROM loans WHERE isbn = ? AND userId = ?", 
                       (book_isbn, user_id))
        conn.commit()
        print(f"✅ Book {book_isbn} returned and removed from loans.")
        conn.close()
        return True
    else:
        print("❌ No valid loan found.")
        conn.close()
        return False


def main():
    global current_user_id  # Allow modifying the global variable

    # ✅ Initialize hardware components
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    usonic_init()
    keypad_init(key_pressed)  # ✅ Fix: Assign callback function
    GPIO.setup(26, GPIO.OUT)  # ✅ Set GPIO 26 as output for the servo

    # ✅ Start keypad polling in background thread
    keypad_thread = Thread(target=get_key, daemon=True)
    keypad_thread.start()

    global lcd_display
    lcd_display = lcd()
    lcd_display.lcd_display_string("System Ready", 1)
    
    print(" System ready... Waiting for user presence.")

    while True:
        distance = get_distance()
        if distance < 10:  # Detect presence
            lcd_display.lcd_clear()
            lcd_display.lcd_display_string("Scan Your QR Code", 1)
            user = scan_barcode()

            if user:
                if user and 'data' in user and 'id' in user['data']:
                    current_user_id = user['data']['id']  # ✅ Access user ID correctly
                    print(f" User authenticated (ID: {current_user_id}).")
                else:
                    print(" Authentication failed: Invalid user data.")
                    lcd_display.lcd_display_string("Auth Failed", 1)
                    time.sleep(2)
                    lcd_display.lcd_clear()
                    continue  

                lcd_display.lcd_clear()
                lcd_display.lcd_display_string("1. Collect Book", 1)
                lcd_display.lcd_display_string("2. Return Book", 2)
                print(f" Waiting for user selection...")

                # Wait until the user responds
                while shared_keypad_queue.empty():
                    time.sleep(0.1)  # Avoid excessive CPU usage

                key = shared_keypad_queue.get()
                print(f" User selected option: {key}")
                
                if key == "2":  # Return Book Process
                    lcd_display.lcd_clear()
                    lcd_display.lcd_display_string("Scan Book Code", 1)
                    book_isbn = scan_barcode()
                    
                    if book_isbn is None:
                        print(" Error: No barcode detected.")
                        lcd_display.lcd_display_string("Scan Failed", 1)
                        time.sleep(2)
                        continue

                    if verify_and_remove_loan(book_isbn, current_user_id):
                        print(f" Valid Loan Found for Book: {book_isbn}")
                        lcd_display.lcd_display_string("Returning Book...", 1)
                        set_servo_position(90)  # ✅ Unlock book return slot
                        time.sleep(3)
                        set_servo_position(0)  # ✅ Lock again
                        lcd_display.lcd_display_string("Return Successful", 1)
                    else:
                        print(" Invalid or No Loan Found.")
                        lcd_display.lcd_display_string("Invalid Loan", 1)
                    
                    time.sleep(2)
                
                # Reset user session after the process is complete
                current_user_id = None
                lcd_display.lcd_clear()
            else:
                lcd_display.lcd_display_string("Authentication Failed", 1)
                time.sleep(2)
                lcd_display.lcd_clear()

        time.sleep(1)  # Avoid unnecessary CPU usage

if __name__ == "__main__":
    main()
