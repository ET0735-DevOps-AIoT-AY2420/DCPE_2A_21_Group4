import sqlite3
from database import get_db_connection

def get_user_fines(barcode_id):
    """Retrieve the payable fines of a user using Student Card QR Code."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT payableFines FROM users WHERE studentCardQR = ?", (barcode_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def process_payment(barcode_id, amount):
    """Process fine payment and update the user's payable fines."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT payableFines FROM users WHERE studentCardQR = ?", (barcode_id,))
        result = cursor.fetchone()
        
        if not result:
            return "User not found."
        
        current_fines = result[0]
        if current_fines == 0:
            return "No outstanding fines."
        
        if amount > current_fines:
            return "Payment exceeds outstanding fines."
        
        new_fines = current_fines - amount
        cursor.execute("UPDATE users SET payableFines = ? WHERE studentCardQR = ?", (new_fines, barcode_id))
        conn.commit()
        
        return f"Payment successful. Remaining fines: {new_fines} SGD"

if __name__ == "__main__":
    barcode_id = input("Enter Student Card QR Code: ")
    action = input("Check fines or make payment? (check/pay): ").strip().lower()
    
    if action == "check":
        fines = get_user_fines(barcode_id)
        if fines is None:
            print("User not found.")
        else:
            print(f"Outstanding fines: {fines} SGD")
    elif action == "pay":
        amount = float(input("Enter payment amount: "))
        message = process_payment(barcode_id, amount)
        print(message)
    else:
        print("Invalid action.")
