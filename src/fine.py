import time
import sys
import os
import firebase_admin
from firebase_admin import credentials, firestore
# Get the absolute path of the project root
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(project_path, "src"))

from hal.hal_rfid_reader import SimpleMFRC522
from hal import hal_lcd

# Initialize LCD and RFID reader
lcd = hal_lcd.lcd()
reader = SimpleMFRC522()

# Initialize Firebase
cred = credentials.Certificate("/home/pi/ET0735/DCPE_2A_21_Group4/DCPE_2A_21_Group4/serviceAccountKey.json")  
firebase_admin.initialize_app(cred)
db = firestore.client()

def display_message(line1, line2=""):
    """Display a message on the LCD."""
    lcd.lcd_clear()
    lcd.lcd_display_string(line1, 1)
    lcd.lcd_display_string(line2, 2)
    time.sleep(2)

def get_user_data(user_id):
    """Fetch user data from Firebase based on RFID number."""
    users_ref = db.collection("users")

    print(f"Fetching data for User ID: {user_id}")  # Debug log ✅

    try:
        query = users_ref.where("rfidNumber", "==", str(user_id)).stream()
        for doc in query:
            user_data = doc.to_dict()
            print(f"User Data Found: {user_data}")  # ✅ Debug log
            return user_data

        print("No matching user found.")  # Debug log ✅
        return None

    except Exception as e:
        print(f"Error fetching user data: {e}")  # Debug error message ✅
        return None

def main():
    """Main function to scan a card and fetch user data."""
    display_message("System Ready", "Scan your card")

    while True:
        display_message("Waiting for scan...")

        user_id, _ = reader.read()  # Read RFID card

        if user_id is None:
            display_message("Error!", "No card detected")
            continue

        user_id = str(user_id).strip()  # Ensure it's a string
        display_message("Card detected", "Fetching data...")

        # 🔹 Get user data from Firebase
        user_data = get_user_data(user_id)
        
        if user_data:
            student_card_qr = user_data.get("studentCardQR", "N/A")
            payable_fine = user_data.get("payableFine", 0)

            display_message("Student QR:", student_card_qr)
            time.sleep(2)  # Show student QR first

            display_message("Payable Fine:", f"${payable_fine:.2f}")  # Show fine amount
        else:
            display_message("Unknown card!", "Try again")

        time.sleep(2)  # Pause before next scan

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        display_message("System exiting.")
    finally:
        display_message("RFID Reader off.")
