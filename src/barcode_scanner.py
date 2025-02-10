import sys
sys.path.append("./src")  # Ensure 'src' is included in Python path

from picamera2 import Picamera2, Preview
from pyzbar.pyzbar import decode
import cv2
import numpy as np
from hal import hal_servo as servo  # Import HAL Servo module
from hal import hal_led as led      # Import HAL LED module
from hal import hal_buzzer as buzzer  # Import HAL Buzzer module
from firebase_admin import firestore, initialize_app, credentials
import time

# ✅ Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")  # Ensure this file is in the root directory
initialize_app(cred)
db = firestore.client()

# ✅ Initialize Servo
servo.init()
SERVO_ANGLE = 90  # Angle to move the servo when barcode is matched

# ✅ Initialize LED & Buzzer
led.init()
buzzer.init()

# ✅ Initialize Camera
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})  
picam2.configure(preview_config)
picam2.start_preview(Preview.NULL)
picam2.start()

print("📷 Camera started. Point it at a barcode.")

def check_barcode_in_database(barcode):
    """
    Check if the scanned barcode exists in the Firestore 'Books' collection (ISBN field).
    """
    try:
        books_ref = db.collection("Books")
        print(f"🔎 Searching Firestore for ISBN: {barcode}")
        query = books_ref.where("ISBN", "==", barcode).stream()
        book_found = None

        for doc in query:
            book_found = doc.to_dict()
            break  # Exit after first match

        if book_found:
            print(f"✅ Matched Book: {book_found.get('Title', 'Unknown Title')} - ISBN: {book_found.get('ISBN')}")
            return True
        else:
            print("❌ No match found in database.")
            return False

    except Exception as e:
        print(f"🔥 Error checking database: {e}")
        return False

# ✅ Main Loop
try:
    while True:
        frame = picam2.capture_array()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        decoded_objects = decode(gray)

        for obj in decoded_objects:
            barcode_data = obj.data.decode('utf-8')
            print(f"📌 Detected Barcode: {barcode_data}")

            # ✅ If the barcode exists in Firestore
            if check_barcode_in_database(barcode_data):
                print("🚀 Matched ISBN! Turning the servo.")
                servo.set_servo_position(SERVO_ANGLE)  # Move servo
                time.sleep(1)  # Small delay before resetting
                servo.set_servo_position(0)  # Reset servo
            else:
                # ❌ If barcode is not found in the database, turn on LED & Buzzer
                print("⚠️ Invalid Barcode! Activating LED and Buzzer.")
                led.set_output(24, 1)  # Turn LED ON
                buzzer.turn_on()
                time.sleep(2)  # Keep LED & Buzzer ON for 2 seconds
                led.set_output(24, 0)  # Turn LED OFF
                buzzer.turn_off()

        # ✅ Save the image instead of displaying it (for headless setup)
        cv2.imwrite("barcode_output.jpg", frame)
        print("📸 Image saved as barcode_output.jpg")

except KeyboardInterrupt:
    print("🛑 Stopping barcode detection...")
finally:
    picam2.stop_preview()
    picam2.stop()
    print("📷 Camera stopped.")
