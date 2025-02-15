from picamera2 import Picamera2, Preview
from pyzbar.pyzbar import decode
import cv2
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add parent directory to path

from database import get_user_by_barcode, get_book_by_barcode  # Import functions

def scan_barcode():
    """Scans barcode and returns user or book data if found."""
    print("Starting barcode scanner... Please scan your QR Code or Book ISBN.")

    try:
        picam2 = Picamera2()
        preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(preview_config)

        # ✅ FIX: Use Preview.NULL to prevent GUI errors
        picam2.start_preview(Preview.NULL)  
        picam2.start()

        while True:
            frame = picam2.capture_array()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decoded_objects = decode(gray)

            for obj in decoded_objects:
                barcode_data = obj.data.decode('utf-8').strip()
                print(f" Scanned Code: {barcode_data}")

                # 🔹 Check if it's a USER QR Code
                user = get_user_by_barcode(barcode_data)
                if user:
                    print(f"🎉 User authenticated: {user['name']} ({user['email']})")
                    picam2.stop()
                    picam2.close()
                    cv2.destroyAllWindows()
                    return {"type": "user", "data": user}

                # 🔹 Check if it's a BOOK ISBN
                book = get_book_by_barcode(barcode_data)
                if book:
                    print(f"📚 Book Found: {book['title']} by {book['author']}")
                    picam2.stop()
                    picam2.close()
                    cv2.destroyAllWindows()
                    return {"type": "book", "data": book}

                print("❌ Invalid barcode. Try again.")

            # Show camera feed
            cv2.imshow("Barcode Scanner", frame)

            # Stop scanning if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except RuntimeError as e:
        print(f"❌ Camera error: {e}")
        try:
            picam2.stop()
            picam2.close()
        except Exception:
            pass

    except KeyboardInterrupt:
        print("Stopping barcode scanner...")

    finally:
        try:
            picam2.stop()
            picam2.close()
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Warning: {e}")

    return None