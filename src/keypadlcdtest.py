import sys
import os

# Get the absolute path of the project root
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
sys.path.append(project_path)  # Add src/ to sys.path

# Now import the modules
from hal import hal_keypad  
from hal import hal_lcd

    
from time import sleep

lcd = hal_lcd.lcd()

MENU_STATES = [
    ("1. Enter Book Code", "****************"),  # REQ-01
    ("1. Reserve Book", "2. Make Payment"),  # REQ-02
    ("1. Type in your ID", "123456789"),  # REQ-03
    ("1. Choose Branch", "2. Enter Branch Number"),  # REQ-04
    ("Collect book within", "5 days"),  # REQ-05
    ("Loan Period: 18 days", ""),  # REQ-06
    ("Exceeds Limit", ""),  # REQ-07
    ("Scan Book Code", "Waiting..."),  # REQ-08
    ("Fine: $0.15 per day", ""),  # REQ-09
    ("Scan RFID to Pay", ""),  # REQ-10
    ("Please scan QR code", ""),  # REQ-11
    ("Successful", ""),  # REQ-11 
]

current_state = 0  # Track the current menu state
max_books = 10  # Maximum books a user can borrow
borrowed_books = 0  # Number of books the user has borrowed
fines_due = 0  # Placeholder for fines amount

def update_display():
    """Update LCD with the current menu state"""
    lcd.lcd_clear()
    line1, line2 = MENU_STATES[current_state]
    lcd.lcd_display_string(line1, 1)  
    lcd.lcd_display_string(line2, 2)  


def handle_keypress(key):
    """Handle keypress events from the keypad"""
    global current_state, borrowed_books, fines_due

    if key == "#":  # Move to the next menu
        current_state = (current_state + 1) % len(MENU_STATES)
        update_display()
    elif key == "*":  # Go back to the previous menu
        current_state = (current_state - 1) % len(MENU_STATES)
        update_display()
    elif key == "1" and current_state == 6:  # REQ-07: Exceeds Limit
        if borrowed_books >= max_books:
            lcd.lcd_clear()
            lcd.lcd_display_string("Exceeds Limit", 1)
            sleep(2)
            update_display()
    elif key == "2" and current_state == 9:  # REQ-10: Check fines
        if fines_due > 0:
            lcd.lcd_clear()
            lcd.lcd_display_string(f"Fine Due: ${fines_due:.2f}", 1)
            sleep(2)
        update_display()
    elif current_state == 11:  # REQ-11: Scan QR Code
        lcd.lcd_clear()
        lcd.lcd_display_string("Successful", 1)
        sleep(2)
        update_display()
    else:
        print(f"Key Pressed: {key}")  # Print key in terminal


# Initialize Keypad with callback function
hal_keypad.init(handle_keypress)

# Show initial menu
update_display()

# Main loop to check for key presses
print("Press a key on the keypad to navigate...")

while True:
    hal_keypad.get_key()  # Check for keypress
    sleep(0.1)  
