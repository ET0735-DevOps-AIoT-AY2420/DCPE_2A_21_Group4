import sqlite3
from datetime import datetime, timedelta

# Database path
db_path = "/mnt/data/DCPE_2A_21_Group4/DCPE_2A_21_Group4/library.db"

# Fine settings
LOAN_PERIOD = 18  # Days
EXTENSION_PERIOD = 7  # Days
FINE_PER_DAY = 0.15  # SGD

def calculate_fines():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query all loans
    cursor.execute("SELECT userId, borrowDate, dueDate, extendStatus, returnDate FROM loans")
    loans = cursor.fetchall()
    
    user_fines = {}
    
    for user_id, borrow_date, due_date, extend_status, return_date in loans:
        borrow_date = datetime.strptime(borrow_date, "%Y-%m-%d %H:%M:%S")
        due_date = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S") if due_date else borrow_date + timedelta(days=LOAN_PERIOD)
        
        if extend_status == "Yes":
            due_date += timedelta(days=EXTENSION_PERIOD)
        
        today = datetime.utcnow()
        return_date = datetime.strptime(return_date, "%Y-%m-%d %H:%M:%S") if return_date else None
        overdue_days = max(0, ((return_date or today) - due_date).days)
        fine = overdue_days * FINE_PER_DAY
        
        if user_id not in user_fines:
            user_fines[user_id] = 0.0
        user_fines[user_id] += fine
    
    conn.close()
    return user_fines

if __name__ == "__main__":
    fines = calculate_fines()
    for user, fine in fines.items():
        print(f"User {user} has a total fine of SGD {fine:.2f}")
