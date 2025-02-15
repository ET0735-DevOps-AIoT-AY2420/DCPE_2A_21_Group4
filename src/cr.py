import time
import queue
from threading import Thread

import RPi.GPIO as GPIO

from hal.hal_lcd import lcd
from hal.hal_servo import set_servo_position
from hal.hal_usonic import init as usonic_init, get_distance
from hal.hal_keypad import init as keypad_init, get_key
from barcode_scanner import scan_barcode
from hal.hal_rfid_reader import SimpleMFRC522
from database import get_db_connection

# 🔄 Queue for keypad input
shared_keypad_queue = queue.Queue()
current_user_id = None  # Store authenticated user ID
reader = SimpleMFRC522()

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
    
def wait_for_book_code():
    """Collect multiple keypresses until '#' is pressed."""
    book_code = ""
    lcd_display.lcd_display_string("Enter Book Code", 1)

    while True:
        key = shared_keypad_queue.get()
        
        if key == "#":  # User finished entering
            return book_code  
        else:
            book_code += str(key)  # Append pressed key
            lcd_display.lcd_display_string(book_code, 2)  # Display entered digits

def verify_book_code(book_code, user_id):
    """Verify if the book is reserved by the user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM loans WHERE bookId = ? AND userId = ? AND returnDate IS NULL", (book_code, user_id))
    book = cursor.fetchone()
    conn.close()
    return bool(book)

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
    
    # ✅ Ensure LCD starts with a clear screen
    lcd_display.lcd_clear()
    lcd_display.lcd_display_string("System Ready", 1)
    time.sleep(2)  # ✅ Allow LCD to show the message
    
    print(" System ready... Waiting for user presence.")

    while True:
        distance = get_distance()
        if distance < 10:  # Detect presence
            print("👤 User detected! Asking for QR scan...")
            lcd_display.lcd_clear()
            lcd_display.lcd_display_string("Log In Using", 1)
            lcd_display.lcd_display_string("Your Barcode", 2)
            time.sleep(1)  # ✅ Allow message display

            user = scan_barcode()

            if user:
                if user and 'data' in user and 'id' in user['data']:
                    current_user_id = user['data']['id']  # ✅ Access user ID correctly
                else:
                    print("Authentication failed: Invalid user data.")
                    lcd_display.lcd_clear()
                    lcd_display.lcd_display_string("Auth Failed", 1)
                    time.sleep(2)
                    continue  # Retry

                lcd_display.lcd_clear()
                lcd_display.lcd_display_string("1. Collect 2. Return", 1)
                lcd_display.lcd_display_string("3. Payment 4. Check", 2)
                print(f" User authenticated (ID: {current_user_id}). Options displayed.")
                
                # Wait until the user responds
                while shared_keypad_queue.empty():
                    time.sleep(0.1)  # Avoid excessive CPU usage

                key = shared_keypad_queue.get()
                print(f" User selected option: {key}")

                if key == "1":  # Collect Book Process
                    lcd_display.lcd_clear()
                    print(" Waiting for book code entry...")
                    book_code = wait_for_book_code()  # ✅ Collect full book code
                    print(f" Book Code Entered: {book_code}")  # Debugging

                    if verify_book_code(book_code, user['id']):
                        lcd_display.lcd_display_string("Book Dispensing", 1)

                        GPIO.setup(26, GPIO.OUT)  # ✅ Ensure GPIO 26 is still set as output before using servo
                        set_servo_position(90)  # ✅ Unlock book compartment
                        time.sleep(3)
                        set_servo_position(0)  # ✅ Lock again
                        lcd_display.lcd_clear()
                        lcd_display.lcd_display_string("Take Your Book", 1)
                        time.sleep(3)
                        lcd_display.lcd_display_string("Book Dispensed", 1)
                        time.sleep(2)
                        lcd_display.lcd_clear()
                    else:
                        lcd_display.lcd_display_string("Invalid Book Code", 1)
                        time.sleep(2)
                        lcd_display.lcd_clear()

                if key == "2":  # Return Book Process
                    print("📖 User selected RETURN BOOK.")
                    lcd_display.lcd_clear()
                    lcd_display.lcd_display_string("Scan Book Code", 1)
                    time.sleep(1)  # ✅ Allow message display
                    
                    book_isbn = scan_barcode()
                    print(f"📚 Scanned Book ISBN: {book_isbn}")
                    
                    if verify_and_remove_loan(book_isbn, current_user_id):
                        print(f"✅ Valid Loan Found for Book: {book_isbn}")
                        lcd_display.lcd_clear()
                        lcd_display.lcd_display_string("Returning Book", 1)
                        time.sleep(2)  # ✅ Allow display
                        
                        set_servo_position(90)  # ✅ Unlock book return slot
                        time.sleep(3)
                        set_servo_position(0)  # ✅ Lock again
                        
                        lcd_display.lcd_clear()
                        lcd_display.lcd_display_string("Return Successful", 1)
                    else:
                        print(" Invalid Loan or No Loan Found.")
                        lcd_display.lcd_clear()
                        lcd_display.lcd_display_string("Invalid Loan", 1)
                    
                    time.sleep(2)
                

                if key == "3":  # Payment Process
                    print("💰 User selected PAYMENT.")
                    lcd_display.lcd_clear()
                    lcd_display.lcd_display_string("Checking Fines...", 1)
                    time.sleep(1)

                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # ✅ Use authenticated user's ID to check fines
                    cursor.execute("SELECT payableFines FROM users WHERE id = ?", (current_user_id,))
                    result = cursor.fetchone()
                    
                    if result and result[0] > 0:
                        fine_amount = result[0]
                        print(f"💰 User has ${fine_amount:.2f} in fines.")
                        lcd_display.lcd_clear() 
                        lcd_display.lcd_display_string(f"Fine: ${fine_amount:.2f}", 1)
                        lcd_display.lcd_display_string("1: Pay | 2: Exit", 2)

                        while shared_keypad_queue.empty():
                            time.sleep(0.1)  # Wait for user input

                        pay_key = shared_keypad_queue.get()
                        if pay_key == "1":  # User chooses to pay
                            print("📌 Scan to Pay:")
                            lcd_display.lcd_clear()
                            lcd_display.lcd_display_string("Scan to Pay:", 1)

                            # ✅ Initiate RFID reader and wait for scan
                            scanned_rfid = None
                            while not scanned_rfid:
                                scanned_rfid, _ = reader.read()  # Read RFID tag

                            print(f"RFID Scanned: {scanned_rfid}")

                            # ✅ Display processing for 2 seconds
                            print("💳 Processing payment...")
                            lcd_display.lcd_clear()
                            lcd_display.lcd_display_string("Processing...", 1)
                            time.sleep(2)

                            # ✅ Update fines using authenticated user's ID
                            cursor.execute("UPDATE users SET payableFines = 0 WHERE id = ?", (current_user_id,))
                            conn.commit()

                            print("✅ Payment Successful.")
                            lcd_display.lcd_clear()
                            lcd_display.lcd_display_string("Payment Successful", 1)
                        else:
                            print("❌ Payment Canceled.")
                            lcd_display.lcd_clear()
                            lcd_display.lcd_display_string("Payment Canceled", 1)
                    else:
                        print("✅ No outstanding fines.")
                        lcd_display.lcd_clear()
                        lcd_display.lcd_display_string("No Fines Due", 1)
                    
                    conn.close()
                    time.sleep(2)  # Allow time to display message

# Reset user session after the process is complete
                current_user_id = None
                lcd_display.lcd_clear()
                lcd_display.lcd_display_string("Session Ended", 1)
                time.sleep(2)
                lcd_display.lcd_clear()

            else:
                print("No user detected. Returning to idle state.")
                lcd_display.lcd_clear()
                lcd_display.lcd_display_string("Scan Failed", 1)
                time.sleep(2)
                lcd_display.lcd_clear()

        time.sleep(1)  # Avoid unnecessary CPU usage

if __name__ == "__main__":
    main()