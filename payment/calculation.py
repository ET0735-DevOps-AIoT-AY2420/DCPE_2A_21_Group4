import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Initialize Firebase
cred = credentials.Certificate("/home/pi/ET0735/DCPE_2A_21_Group4/DCPE_2A_21_Group4/serviceAccountKey.json")  # Replace with your Firebase credentials file
firebase_admin.initialize_app(cred)
db = firestore.client()

# Fine settings
LOAN_PERIOD = 18  # Days
EXTENSION_PERIOD = 7  # Days
FINE_PER_DAY = 0.15  # SGD

def calculate_fines():
    loans_ref = db.collection("Loans")
    loans = loans_ref.stream()
    
    user_fines = {}
    
    for loan in loans:
        data = loan.to_dict()
        borrow_date = datetime.strptime(data["borrowDate"], "%Y-%m-%dT%H:%M:%S.%fZ")
        extended = data.get("extendStatus", "No") == "Yes"
        return_date = data.get("returnDate")
        
        # Calculate due date
        due_date = borrow_date + timedelta(days=LOAN_PERIOD + (EXTENSION_PERIOD if extended else 0))
        
        # Determine if book is overdue
        today = datetime.utcnow()
        if return_date:
            return_date = datetime.strptime(return_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        overdue_days = max(0, ((return_date or today) - due_date).days)
        fine = overdue_days * FINE_PER_DAY
        
        # Add fine to user's total
        user_id = data["userId"]
        if user_id not in user_fines:
            user_fines[user_id] = 0.0
        user_fines[user_id] += fine
    
    return user_fines

if __name__ == "__main__":
    fines = calculate_fines()
    for user, fine in fines.items():
        print(f"User {user} has a total fine of SGD {fine:.2f}")
