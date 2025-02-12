import time
import sqlite3
from hal.hal_lcd import lcd
from hal.hal_keypad import init as keypad_init, get_key
from barcode_scanner import scan_barcode

def get_db_connection():
    conn = sqlite3.connect('library.db') # to update the database location file path from RPI or your local file path
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_barcode(barcode):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, payableFines FROM users WHERE studentCardQR = ?", (barcode,))
    user = cursor.fetchone()
    conn.close()
    return user if user else None

def process_payment(user_id, fine_amount):
    lcd_display = lcd()
    lcd_display.lcd_clear()
    lcd_display.lcd_display_string(f"Fine: ${fine_amount}", 1)
    lcd_display.lcd_display_string("Press # to pay", 2)
    
    keypad_init(lambda key: handle_keypress(key, user_id, fine_amount, lcd_display))

def handle_keypress(key, user_id, fine_amount, lcd_display):
    if key == '#':
        lcd_display.lcd_clear()
        lcd_display.lcd_display_string("Processing...", 1)
        time.sleep(2)
        
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
    lcd_display.lcd_display_string("Scan Student Card", 1)
    time.sleep(2)
    lcd_display.lcd_clear()
    
    barcode_id = scan_barcode()
    user = get_user_by_barcode(barcode_id)
    
    if user:
        user_id, fine_amount = user["id"], user["payableFines"]
        if fine_amount > 0:
            process_payment(user_id, fine_amount)
        else:
            lcd_display.lcd_display_string("No fine due.", 1)
            time.sleep(2)
            lcd_display.lcd_clear()
    else:
        lcd_display.lcd_display_string("Scan Failed", 1)
        time.sleep(2)
        lcd_display.lcd_clear()
