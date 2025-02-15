import pytest
import sqlite3
from database import get_user_by_barcode, get_db_connection

DB_NAME = "/home/pi/ET0735/DCPE_2A_21_Group4/DCPE_2A_21_Group4/library.db"

@pytest.fixture(scope="module")
def db_connection():
    """Set up a real database connection."""
    conn = get_db_connection()
    yield conn
    conn.close()

def test_get_user_by_barcode(db_connection):
    """Test retrieving user details using the real database."""
    barcode_id = "user-00001"  # Should exist in `insert_users()`
    
    user = get_user_by_barcode(barcode_id)
    
    assert user is not None, "No user found for the barcode!"
    assert user["name"] == "John Doe", " Incorrect user name!"
    assert user["email"] == "john.doe@example.com", " Incorrect user email!"
    assert user["studentCardQR"] == barcode_id, " Barcode ID mismatch!"

    print("✅ Test Passed: User retrieval from real database works correctly!")
