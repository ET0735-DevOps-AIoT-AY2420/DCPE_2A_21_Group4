import time
import sys
sys.path.append("./src") 
from hal.hal_rfid_reader import SimpleMFRC522
from hal import hal_lcd

lcd = hal_lcd.lcd()
reader = SimpleMFRC522()

# Initialize user with a fine of $1.50
initial_user_id = 123456789
user_fines = {initial_user_id: 1.50}  

def display_message(line1, line2=""):
    """Display a message on the LCD."""
    lcd.lcd_clear()
    lcd.lcd_display_string(line1, 1)
    lcd.lcd_display_string(line2, 2)
    time.sleep(2)

def process_payment(user_id):
    """Process the fine payment when an RFID card is tapped."""
    fine_amount = user_fines.get(user_id, 0.00)
    
    if fine_amount > 0:
        display_message("Fine detected!", f"${fine_amount:.2f}")
        display_message("Processing payment...")
        user_fines[user_id] = 0.00  # Clear the fine after payment
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

        if user_id in user_fines:
            process_payment(user_id)
        else:
            display_message("Unknown card!", "Try again")

        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        display_message("System exiting.")
    finally:
        display_message("RFID Reader off.")

