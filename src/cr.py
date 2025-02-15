import time
import queue
from threading import Thread

import RPi.GPIO as GPIO

from hal.hal_lcd import lcd
from hal.hal_servo import set_servo_position
from hal.hal_usonic import init as usonic_init, get_distance
from hal.hal_keypad import init as keypad_init, get_key
from hal.hal_buzzer import init as buzzer_init, beep
from barcode_scanner import scan_barcode
from hal.hal_rfid_reader import SimpleMFRC522
from database import get_db_connection

print("Displaying message...", flush=True)

# 🔄 Queue for keypad input
shared_keypad_queue = queue.Queue()
current_user_id = None  # Store authenticated user ID
reader = SimpleMFRC522()

def key_pressed(key):
    """Callback function to store keypress in queue."""
    shared_keypad_queue.put(str(key))  # Convert to string
    print(f" Key Pressed: {key}")  # Debugging
    beep(0.1, 0.1, 1)  # Beep once for 0.1 seconds

def lcd_display_message(line1, line2=""):
    """Display two-line message on LCD with safe truncation."""
    print(f"LCD Display:\n  Line 1: {line1}\n  Line 2: {line2}", flush=True)  # Debugging output
    lcd_display.lcd_clear()
    time.sleep(0.1)  # Allow LCD to clear properly
    lcd_display.lcd_display_string(line1[:16], 1)  # First line (max 16 chars)
    lcd_display.lcd_display_string(line2[:16], 2)  # Second line (max 16 chars)

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
        print("❌ No valid loan found.", flush=True)
        conn.close()
        return False

def wait_for_book_code():
    """Collect multiple keypresses until '#' is pressed."""
    book_code = ""
    lcd_display_message("Enter Book Code", "")

    while True:
        key = shared_keypad_queue.get()
        
        if key == "#":  # User finished entering
            return book_code  
        else:
            book_code += str(key)  # Append pressed key
            lcd_display_message("Enter Book Code", book_code)  # Display entered digits

def verify_book_code(book_code, user_id):
    """Verify if the book is reserved by the user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM loans WHERE bookId = ? AND userId = ? AND returnDate IS NULL", (book_code, user_id))
    book = cursor.fetchone()
    conn.close()
    return bool(book)

def exit_session():
    """Exit the session and return to user authentication."""
    global current_user_id  # Reset user session
    print("🔄 Exiting session... Returning to authentication.", flush=True)
    
    lcd_display_message("Session Ended", "")
    time.sleep(2)
    
    current_user_id = None  # Clear authenticated user ID
    lcd_display_message("System Ready", "")
    time.sleep(2)  # Display system ready message

def main():
    global current_user_id  # Allow modifying the global variable

    # ✅ Initialize hardware components
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    usonic_init()
    keypad_init(key_pressed)  # ✅ Fix: Assign callback function
    GPIO.setup(26, GPIO.OUT)  # ✅ Set GPIO 26 as output for the servo
    buzzer_init()  # Initialize the buzzer

    # ✅ Start keypad polling in background thread
    keypad_thread = Thread(target=get_key, daemon=True)
    keypad_thread.start()

    global lcd_display
    lcd_display = lcd()
    
    # ✅ Ensure LCD starts with a clear screen
    lcd_display_message("System Ready", "")
    time.sleep(2)  # ✅ Allow message to display properly
    
    print(" System ready... Waiting for user presence.", flush=True)

    while True:
        distance = get_distance()
        if distance < 10:  # Detect presence
            print("👤 User detected! Asking for QR scan...", flush=True)
            lcd_display_message("Log In Using", "Your Barcode")
            time.sleep(1)  # ✅ Allow message display

            user = scan_barcode()

            if user:
                if user and 'data' in user and 'id' in user['data']:
                    current_user_id = user['data']['id']  # ✅ Access user ID correctly
                    beep(0.1, 0.1, 2)  # Beep twice for successful authentication
                else:
                    print("Authentication failed: Invalid user data.", flush=True)
                    lcd_display_message("Auth Failed", "")
                    time.sleep(2)
                    continue  # Retry

                while True:  # Main menu loop
                    lcd_display_message("1Collect 2Return", "3Payment 4Exit")
                    print(f" User authenticated (ID: {current_user_id}). Options displayed.", flush=True)
                    
                    # Wait until the user responds
                    while shared_keypad_queue.empty():
                        time.sleep(0.1)  # Avoid excessive CPU usage

                    key = shared_keypad_queue.get()
                    print(f" User selected option: {key}")

                    if key == "1":  # Collect Book Process
                        lcd_display_message("Enter Book Code", "")
                        print(" Waiting for book code entry...", flush=True)
                        book_code = wait_for_book_code()  # ✅ Collect full book code
                        print(f" Book Code Entered: {book_code}")  # Debugging

                        if verify_book_code(book_code, user.get('data', {}).get('id')):
                            lcd_display_message("Book Dispensing", "")
                            beep(0.1, 0.1, 1)  # Beep once for book dispensing

                            GPIO.setup(26, GPIO.OUT)  # ✅ Ensure GPIO 26 is still set as output before using servo
                            set_servo_position(90)  # ✅ Unlock book compartment
                            time.sleep(3)
                            set_servo_position(0)  # ✅ Lock again
                            lcd_display_message("Take Your Book", "")
                            time.sleep(3)
                        else:
                            lcd_display_message("Invalid Book Code", "")
                            time.sleep(2)

                        # Exit option after Collect
                        lcd_display_message("Press # to Exit", "")
                        while True:
                            if not shared_keypad_queue.empty():
                                exit_key = shared_keypad_queue.get()
                                if exit_key == "#":
                                    break  # Exit Collect process and return to main menu

                    if key == "2":  # Return Book Process
                        print("📖 User selected RETURN BOOK.", flush=True)
                        lcd_display_message("Scan Book Code", "")
                        time.sleep(1)  # ✅ Allow message display
                        
                        book_isbn = scan_barcode()
                        print(f"📚 Scanned Book ISBN: {book_isbn}")
                        
                        if verify_and_remove_loan(book_isbn, current_user_id):
                            print(f"✅ Valid Loan Found for Book: {book_isbn}", flush=True)
                            lcd_display_message("Returning Book", "")
                            time.sleep(2)  # ✅ Allow display
                            
                            set_servo_position(90)  # ✅ Unlock book return slot
                            time.sleep(3)
                            set_servo_position(0)  # ✅ Lock again
                            
                            lcd_display_message("Return Successful", "")
                            beep(0.1, 0.1, 1)  # Beep once for successful return
                        else:
                            print(" Invalid Loan or No Loan Found.", flush=True)
                            lcd_display_message("Invalid Loan", "")
                        
                        time.sleep(2)

                        # Exit option after Return
                        lcd_display_message("Press # to Exit", "")
                        while True:
                            if not shared_keypad_queue.empty():
                                exit_key = shared_keypad_queue.get()
                                if exit_key == "#":
                                    break  # Exit Return process and return to main menu

                    if key == "3":  # Payment Process
                        print("💰 User selected PAYMENT.", flush=True)
                        lcd_display_message("Checking Fines...", "")
                        time.sleep(1)

                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        # ✅ Use authenticated user's ID to check fines
                        cursor.execute("SELECT payableFines FROM users WHERE id = ?", (current_user_id,))
                        result = cursor.fetchone()
                        
                        if result and result[0] > 0:
                            fine_amount = result[0]
                            print(f"💰 User has ${fine_amount:.2f} in fines.", flush=True)
                            lcd_display_message(f"Fine: ${fine_amount:.2f}", "1: Pay | 2: Exit")

                            while shared_keypad_queue.empty():
                                time.sleep(0.1)  # Wait for user input

                            pay_key = shared_keypad_queue.get()
                            if pay_key == "1":  # User chooses to pay
                                print("📌 Scan to Pay:", flush=True)
                                lcd_display_message("Scan to Pay:", "",)

                                # ✅ Initiate RFID reader and wait for scan
                                scanned_rfid = None
                                while not scanned_rfid:
                                    scanned_rfid, _ = reader.read()  # Read RFID tag

                                print(f"RFID Scanned: {scanned_rfid}", flush=True)

                                # ✅ Display processing for 2 seconds
                                print("💳 Processing payment...", flush=True)
                                lcd_display_message("Processing...", "")
                                time.sleep(2)

                                # ✅ Update fines using authenticated user's ID
                                cursor.execute("UPDATE users SET payableFines = 0 WHERE id = ?", (current_user_id,))
                                conn.commit()

                                print("✅ Payment Successful.", flush=True)
                                lcd_display_message("Payment Successful", "")
                                beep(0.1, 0.1, 1)  # Beep once for payment success
                            else:
                                print("❌ Payment Canceled.", flush=True)
                                lcd_display_message("Payment Canceled", "")
                        else:
                            print("✅ No outstanding fines.", flush=True)
                            lcd_display_message("No Fines Due", "")
                        
                        conn.close()
                        time.sleep(2)  # Allow time to display message

                        # Exit option after Payment
                        lcd_display_message("Press # to Exit", "")
                        while True:
                            if not shared_keypad_queue.empty():
                                exit_key = shared_keypad_queue.get()
                                if exit_key == "#":
                                    break  # Exit Payment process and return to main menu

                    if key == "4":  # Exit Process
                        print("🚪 User selected EXIT.", flush=True)
                        exit_session()
                        break  # Exit the main menu loop

            else:
                print("No user detected. Returning to idle state.")
                lcd_display_message("Scan Failed", "")
                time.sleep(2)

        time.sleep(1)  # Avoid unnecessary CPU usage

if __name__ == "__main__":
    main()