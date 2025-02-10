import sqlite3
import time
import sys
import os
from datetime import datetime, timedelta
from hal.hal_rfid_reader import SimpleMFRC522
from hal import hal_lcd

# Database path
db_path = r"D:\GamayDCPE2A21_Group4\DCPE_2A_21_Group4\library.db"

# Fine settings
LOAN_PERIOD = 18  # Days
EXTENSION_PERIOD = 7  # Days
FINE_PER_DAY = 0.15  # SGD

lcd = hal_lcd.lcd()
reader = SimpleMFRC522()

def display_message(line1, line2=""):
    """Display a message on the LCD."""
    lcd.lcd_clear()
    lcd.lcd_display_string(line1, 1)
    lcd.lcd_display_string(line2, 2)
    time.sleep(2)

def get_user_fine(user_id):
    """Retrieve the fine amount for a user from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(fine) FROM loans WHERE userId = ?", (user_id,))
    fine = cursor.fetchone()[0] or 0.00
    conn.close()
    return fine

def clear_user_fine(user_id):
    """Clear the fine for a user after payment."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE loans SET fine = 0 WHERE userId = ?", (user_id,))
    conn.commit()
    conn.close()

def process_payment(user_id):
    """Process the fine payment when an RFID card is tapped."""
    fine_amount = get_user_fine(user_id)
    
    if fine_amount > 0:
        display_message("Fine detected!", f"${fine_amount:.2f}")
        display_message("Processing payment...")
        clear_user_fine(user_id)
        display_message("Payment Done", "Fine cleared!")
    else:
        display_message("No fines.", "You're clear!")

def main():
    display_message("System Ready", "Scan your card")
    
    while True:
        display_message("Waiting for scan...")
        
        user_id, _ = reader.read()
        
        if user_id is None:
            display_message("Error!", "No card detected")
            continue
        
        display_message("Card detected", f"ID: {user_id}")
        process_payment(user_id)
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        display_message("System exiting.")
    finally:
        display_message("RFID Reader off.")
        reader.cleanup()