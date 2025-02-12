import time
import sqlite3
from hal.hal_lcd import lcd
from hal.hal_keypad import init as keypad_init, get_key
from barcode_scanner import scan_barcode

# Function to establish a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('library.db') # Update the database file path for RPI or local environment
    conn.row_factory = sqlite3.Row
    return conn

# Function to retrieve user details based on scanned barcode
def get_user_by_barcode(barcode):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, payableFines FROM users WHERE studentCardQR = ?", (barcode,))
    user = cursor.fetchone()
    conn.close()
    return user if user else None

# Function to handle the fine payment process
def process_payment(user_id, fine_amount):
    lcd_display = lcd()
    lcd_display.lcd_clear()
    lcd_display.lcd_display_string(f"Fine: ${fine_amount}", 1)
    lcd_display.lcd_display_string("Press # to pay", 2)
    
    # Initialize keypad for user input
    keypad_init(lambda key: handle_keypress(key, user_id, fine_amount, lcd_display))

# Function to handle keypress events during payment
def handle_keypress(key, user_id, fine_amount, lcd_display):
    if key == '#':
        lcd_display.lcd_clear()
        lcd_display.lcd_display_string("Processing...", 1)
        time.sleep(2)
        
        # Update the database to clear fines after payment
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE loans SET returnDate = date('now') WHERE userId = ? AND returnDate IS NULL", (user_id,))
        cursor.execute("UPDATE users SET payableFines = 0 WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        lcd_display.lcd_clear()
        lcd_display.lcd_display_string("Payment Success!", 1)
        time.sleep(2)
    else:
        lcd_display.lcd_clear()
        lcd_display.lcd_display_string("Payment Canceled", 1)
        time.sleep(2)

if __name__ == "__main__":
    lcd_display = lcd()
    lcd_display.lcd_clear()
    
    # Display welcome message and prompt user to scan ID
    lcd_display.lcd_display_string("Welcome!", 1)
    lcd_display.lcd_display_string("Scan your ID", 2)
    
    # Keep displaying the message until the user scans their barcode
    while True:
        barcode_id = scan_barcode()
        if barcode_id:
            break
    
    # Retrieve user details from the database
    user = get_user_by_barcode(barcode_id)
    
    if user:
        user_id, user_name, fine_amount = user["id"], user["name"], user["payableFines"]
        
        # Display greeting message with user's name for 4 seconds
        lcd_display.lcd_clear()
        lcd_display.lcd_display_string(f"Hello {user_name}", 1)
        time.sleep(4)
        lcd_display.lcd_clear()
        
        # Proceed to fine payment if applicable
        if fine_amount > 0:
            process_payment(user_id, fine_amount)
        else:
            lcd_display.lcd_display_string("No fine due.", 1)
            time.sleep(2)
            lcd_display.lcd_clear()
    else:
        # Handle scan failure
        lcd_display.lcd_display_string("Scan Failed", 1)
        time.sleep(2)
        lcd_display.lcd_clear()
