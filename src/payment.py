import time
import sqlite3
import sys
import queue
from threading import Thread

sys.path.append('D:\GamayDCPE2A21_Group4\DCPE_2A_21_Group4\library.db')
from barcode_scanner import scan_barcode  # Import barcode scanner function
from hal.hal_lcd import lcd
from hal.hal_keypad import get_key  # Import keypad function

# Initialize hardware
lcd_display = lcd()
shared_keypad_queue = queue.Queue()

def key_pressed(key):
    """Callback function to store keypress in queue."""
    shared_keypad_queue.put(key)
    print(f"🔢 Key Pressed: {key}")  # Debugging

def wait_for_keypress():
    """Wait for a key press and return its value."""
    key = shared_keypad_queue.get()
    return key

def display_message_on_lcd(message, line=1, clear=True):
    """Display a message on the LCD screen."""
    if clear:
        lcd_display.lcd_clear()
    lcd_display.lcd_display_string(message, line)

def get_user_info(user_id):
    """Retrieve user information and payable fines from the database using barcode ID."""
    conn = sqlite3.connect('D:\GamayDCPE2A21_Group4\DCPE_2A_21_Group4\library.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, payableFines FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    return user if user else ("User Not Found", 0)

def process_barcode_scan():
    """Main function to handle barcode scanning and actions."""
    try:
        display_message_on_lcd("Scan your barcode...", line=1)
        print("Waiting for barcode scan...")

        # Wait for user to scan barcode
        user = scan_barcode()
        if not user:
            display_message_on_lcd("Invalid Barcode", line=1)
            time.sleep(2)
            return

        user_id = user['id']
        user_name, payable_fine = get_user_info(user_id)

        display_message_on_lcd(f"Hello, {user_name}!", line=1)
        time.sleep(2)

        if payable_fine > 0:
            display_message_on_lcd(f"Fine: ${payable_fine}", line=1)
            lcd_display.lcd_display_string("Press 1 to Pay", line=2)
        else:
            display_message_on_lcd("No Fine", line=1)
            lcd_display.lcd_display_string("Press 1 to Book", line=2)

        print("🕹️ Waiting for key press...")
        key = wait_for_keypress()
        print(f"Key pressed: {key}")

        if key == "1":
            handle_keypad_action(user_id, payable_fine)

    except Exception as e:
        print(f"Error: {e}")

def handle_keypad_action(user_id, payable_fine):
    """Handle keypad action after pressing 1."""
    if payable_fine > 0:
        display_message_on_lcd("Confirm Payment?", line=1)
        lcd_display.lcd_display_string("Press 1 to Confirm", line=2)

        print("🕹️ Waiting for key press...")
        key = wait_for_keypress()
        print(f"Key pressed: {key}")

        if key == "1":
            conn = sqlite3.connect('D:\GamayDCPE2A21_Group4\DCPE_2A_21_Group4\library.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET payableFines = 0 WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()

            display_message_on_lcd("Fine Cleared", line=1)
            lcd_display.lcd_display_string("Press 1 to Book", line=2)
            print("🕹️ Waiting for key press...")
            key = wait_for_keypress()
            print(f"Key pressed: {key}")

    display_message_on_lcd("Proceeding Booking", line=1)

if __name__ == "__main__":
    keypad_thread = Thread(target=get_key, daemon=True)
    keypad_thread.start()
    process_barcode_scan()
    time.sleep(1)  # Avoid unnecessary CPU usage