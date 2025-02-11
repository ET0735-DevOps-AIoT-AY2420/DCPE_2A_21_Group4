import time
import queue
from threading import Thread

from database import get_user_by_barcode, get_db_connection
from barcode_scanner import scan_barcode
from hal.hal_lcd import lcd
from hal.hal_keypad import init as keypad_init, get_key

# Queue for keypad input
shared_keypad_queue = queue.Queue()

def key_pressed(key):
    """Callback function to store keypress in queue."""
    shared_keypad_queue.put(key)
    print(f" Key Pressed: {key}")  # Debugging

def wait_for_keypress():
    """Wait for a key press and return its value."""
    key = shared_keypad_queue.get()
    return key

def get_fine_amount(user_id):
    """Retrieve the fine amount for a given user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(fineAmount) FROM fines WHERE userId = ? AND paid = 0", (user_id,))
    fine = cursor.fetchone()[0]  # Fetch the fine amount
    conn.close()
    return fine if fine else 0.0  # Return fine amount or 0 if none

def main():
    # Initialize hardware components
    keypad_init(key_pressed)  # Assign callback function
    keypad_thread = Thread(target=get_key, daemon=True)
    keypad_thread.start()

    lcd_display = lcd()
    lcd_display.lcd_clear()
    lcd_display.lcd_display_string("Welcome!", 1)
    time.sleep(2)
    lcd_display.lcd_clear()
    lcd_display.lcd_display_string("Scan Your Card", 1)

    user = scan_barcode()
    
    if user:
        lcd_display.lcd_clear()
        lcd_display.lcd_display_string(f"Hello, {user['name']}", 1)
        time.sleep(2)
        
        fine_amount = get_fine_amount(user['id'])
        lcd_display.lcd_clear()
        lcd_display.lcd_display_string("Fine Amount:", 1)
        lcd_display.lcd_display_string(f"${fine_amount:.2f}", 2)
    else:
        lcd_display.lcd_clear()
        lcd_display.lcd_display_string("Invalid Card", 1)
        time.sleep(2)
        lcd_display.lcd_clear()

if __name__ == "__main__":
    main()
