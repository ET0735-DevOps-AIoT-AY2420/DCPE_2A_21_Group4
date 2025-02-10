import time
import sqlite3
import sys

sys.path.append('/home/pi/ET0735/DCPE_2A_21_Group4/DCPE_2A_21_Group4/src')
from hal.hal_rfid_reader import SimpleMFRC522
from hal.hal_lcd import lcd
from hal.hal_keypad import get_key  # Import keypad function

# Initialize hardware
reader = SimpleMFRC522()
lcd_display = lcd()

def display_message_on_lcd(message, line=1, clear=True):
    """Display a message on the LCD screen."""
    if clear:
        lcd_display.lcd_clear()
    lcd_display.lcd_display_string(message, line)

def get_user_info(rfid_id):
    """Retrieve user information and payable fines from the database using RFID ID."""
    conn = sqlite3.connect('/home/pi/ET0735/DCPE_2A_21_Group4/DCPE_2A_21_Group4/library.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, payableFines FROM users WHERE rfid_id = ?", (rfid_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    return user if user else ("User Not Found", 0)

def process_rfid_scan():
    """Main function to handle RFID scanning and actions."""
    try:
        display_message_on_lcd("Scan your RFID...", line=1)
        print("Waiting for RFID scan...")

        # Wait for user to scan RFID
        rfid_id, text = reader.read()
        print(f"RFID ID: {rfid_id}, Text: {text}")

        # Fetch user info from database
        user_name, payable_fine = get_user_info(rfid_id)

        # Display user name for 3 seconds
        display_message_on_lcd(f"Hello, {user_name}!", line=1)
        time.sleep(2)

        # Show payable fine and next step on LCD
        if payable_fine > 0:
            display_message_on_lcd(f"Fine: ${payable_fine}", line=1)
            lcd_display.lcd_display_string("Press 1 to Pay", line=2)
        else:
            display_message_on_lcd("No Fine", line=1)
            lcd_display.lcd_display_string("Press 1 to Book", line=2)

        # Wait for key input
        print("Waiting for key input...")
        while True:
            key = get_key()
            if key == "1":
                break
            time.sleep(0.2)  # Avoid CPU overuse

        print(f"Key pressed: {key}")
        handle_keypad_action(rfid_id, payable_fine)

    except Exception as e:
        print(f"Error: {e}")

def handle_keypad_action(rfid_id, payable_fine):
    """Handle keypad action after pressing 1."""
    if payable_fine > 0:
        display_message_on_lcd("Scan RFID to Pay", line=1)
        print("Waiting for RFID scan to pay...")

        # Wait for second RFID scan to confirm payment
        new_rfid_id, _ = reader.read()
        print(f"Second RFID scan: {new_rfid_id}")

        if new_rfid_id == rfid_id:  # Ensure same user scans again
            # Clear fine in database
            conn = sqlite3.connect('/home/pi/ET0735/DCPE_2A_21_Group4/DCPE_2A_21_Group4/library.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET payableFines = 0 WHERE rfid_id = ?", (rfid_id,))
            conn.commit()
            conn.close()

            display_message_on_lcd("Fine Cleared", line=1)
            lcd_display.lcd_display_string("Press 1 to Book", line=2)

            print("Waiting for key input to proceed...")
            while True:
                key = get_key()
                if key == "1":
                    break
                time.sleep(0.2)  # Avoid CPU overuse

            print(f"Key pressed: {key}")
            display_message_on_lcd("Proceeding Booking", line=1)

    else:
        display_message_on_lcd("Proceeding Booking", line=1)

if __name__ == "__main__":
    process_rfid_scan()
