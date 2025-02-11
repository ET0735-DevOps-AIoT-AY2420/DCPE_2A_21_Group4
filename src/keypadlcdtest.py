import sqlite3
import time
import sys
import os
from datetime import datetime, timedelta
from hal import hal_keypad, hal_lcd

db_path = "D:\GamayDCPE2A21_Group4\DCPE_2A_21_Group4\library.db"  #change the path to your own path

lcd = hal_lcd.lcd()

MENU_STATES = [
    ("1. Enter Book Code", "Fetching..."),  
    ("2. Choose Branch", "Enter Branch Number"),  
    ("3. Reserve Book", "Collect within 5 days"),  
    ("4. Pls scan ID", "To authenticate"),  
    ("5. Loan Period: 18 days", ""),  
    ("6. Renew for (7d)", ""),
    ("7. Scan Book Code", "Waiting..."),  
    ("8. Check Fine: $0.15/day", ""), 
    ("9. Scan RFID to Pay", ""),  
    ("10. Successful", ""),
]

current_state = 0 
reservation_time = None  
reservation_duration = 5 * 24 * 60 * 60  # 5 days in seconds
loan_period = 18 * 24 * 60 * 60  # 18 days in seconds
renewal_period = 7 * 24 * 60 * 60  # 7 days in seconds
loan_start_time = None  
fines_due = 0  
book_returned = False
renewed = False

def fetch_branch():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT branch_name FROM branches LIMIT 1")
    branch = cursor.fetchone()
    conn.close()
    return branch[0] if branch else "No Branch Selected"

def fetch_book_code():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT bookId FROM loans ORDER BY borrowDate DESC LIMIT 1")
    book_id = cursor.fetchone()
    if book_id:
        cursor.execute("SELECT ISBN FROM books WHERE bookId = ?", (book_id[0],))
        isbn = cursor.fetchone()
        conn.close()
        return isbn[0] if isbn else "No ISBN Found"
    conn.close()
    return "No Book Code Found"

def calculate_fine():
    global fines_due
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT borrowDate FROM loans ORDER BY borrowDate DESC LIMIT 1")
    loan_date = cursor.fetchone()
    conn.close()
    if not loan_date:
        return 0
    loan_date = datetime.strptime(loan_date[0], "%Y-%m-%d")
    due_date = loan_date + timedelta(days=18)
    overdue_days = max(0, (datetime.now() - due_date).days)
    fines_due = overdue_days * 0.15  # $0.15 per day
    return fines_due

def update_display():
    lcd.lcd_clear()
    line1, line2 = MENU_STATES[current_state]
    if current_state == 1:  
        line2 = fetch_branch()  
    if current_state == 0:  
        line2 = fetch_book_code()
    if current_state == 8:
        line2 = f"Fine: ${calculate_fine():.2f}"
    lcd.lcd_display_string(line1, 1)  
    lcd.lcd_display_string(line2, 2)

def handle_keypress(key):
    global current_state, fines_due, reservation_time, loan_start_time, book_returned, renewed
    if key == "#":
        current_state = (current_state + 1) % len(MENU_STATES)
        update_display()
    elif key == "*":
        current_state = (current_state - 1) % len(MENU_STATES)
        update_display()
    elif current_state == 2:
        reservation_time = time.time()
        lcd.lcd_clear()
        lcd.lcd_display_string("Book Reserved", 1)
        lcd.lcd_display_string("Collect within 5 days", 2)
        time.sleep(2)
        update_display()
    elif current_state == 3:
        if reservation_time and (time.time() - reservation_time) > reservation_duration:
            lcd.lcd_clear()
            lcd.lcd_display_string("Reservation Exceeded", 1)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM loans WHERE borrowDate < ?", 
                           (datetime.now() - timedelta(days=5),))
            conn.commit()
            conn.close()
            reservation_time = None
            time.sleep(2)
            update_display()
    elif key == "6" and current_state == 5:
        if loan_start_time is None:
            lcd.lcd_clear()
            lcd.lcd_display_string("No Active Loan", 1)
            time.sleep(2)
        elif not renewed:
            loan_start_time += renewal_period  
            renewed = True
            lcd.lcd_clear()
            lcd.lcd_display_string("Renewed for 7 days", 1)
            time.sleep(2)
        else:
            lcd.lcd_clear()
            lcd.lcd_display_string("Already Renewed", 1)
            time.sleep(2)
        update_display()
    elif key == "7" and current_state == 6:
        if loan_start_time is None:
            lcd.lcd_clear()
            lcd.lcd_display_string("No Active Loan", 1)
        else:
            fines_due = calculate_fine()
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE books SET status = 'available' WHERE bookId = ?", (fetch_book_code(),))
            conn.commit()
            conn.close()
            lcd.lcd_clear()
            lcd.lcd_display_string("Book Returned", 1)
        time.sleep(2)
        update_display()
    elif key == "9" and current_state == 8:
        if fines_due > 0:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE loans SET fine = 0 WHERE borrowDate < ?", (datetime.now(),))
            conn.commit()
            conn.close()
            lcd.lcd_clear()
            lcd.lcd_display_string(f"Paid: ${fines_due:.2f}", 1)
            fines_due = 0  
        time.sleep(2)
        update_display()
    else:
        print(f"Key Pressed: {key}")  

hal_keypad.init(handle_keypress)
update_display()
while True:
    hal_keypad.get_key() 
    time.sleep(0.1)
    if not os.path.exists("/dev/input/event0"):
        sys.exit(0)