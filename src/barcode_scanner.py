from picamera2 import Picamera2, Preview
from pyzbar.pyzbar import decode
import cv2
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add parent directory to path

from database import get_user_by_barcode  # Import function to check user in DB
from database import get_db_connection

def scan_barcode():
    """Scans barcode and returns user data if found."""
    print("[INFO] Starting barcode scanner... Please scan your QR Code.")

    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(preview_config)
    picam2.start_preview(Preview.NULL)
    picam2.start()

    user = None

    try:
        while True:
            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decoded_objects = decode(gray)

            for obj in decoded_objects:
                barcode_data = obj.data.decode('utf-8').strip()
                print(f"[INFO] Scanned QR Code: {barcode_data}")

                # Check if the barcode belongs to a registered user
                user = get_user_by_barcode(barcode_data)
                if user:
                    print(f"[SUCCESS] User authenticated: {user['name']} ({user['email']})")
                    picam2.stop()
                    cv2.destroyAllWindows()
                    return user  # ✅ Return user details if found
                else:
                    print("[WARNING] Invalid barcode. Try again.")

            cv2.imshow("Barcode Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("[INFO] Stopping barcode scanner...")
    except Exception as e:
        print(f"[ERROR] Scanner failed: {e}")
    finally:
        try:
            picam2.stop()
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"[WARNING] Cleanup issue: {e}")

    return None

if __name__ == "__main__":
    user = scan_barcode()
    if user:
        print("[INFO] Login Successful!")
    else:
        print("[INFO] Login Failed.")
