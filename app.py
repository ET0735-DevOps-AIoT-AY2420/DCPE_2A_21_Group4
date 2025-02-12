from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from datetime import datetime
from picamera2 import Picamera2, Preview
from pyzbar.pyzbar import decode
import cv2

app = Flask(__name__, static_folder='static', template_folder='templates')
DB_NAME = "library.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------- Serve Web Pages ----------------------
@app.route('/')
def home():
    return render_template('HomePage.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('userdashboard.html')

@app.route('/reserve')
def reserve_page():
    return render_template('reserved.html')

# ---------------------- API: Get Fine Amount ----------------------
@app.route("/api/get_fine", methods=["GET"])
def get_fine():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT payableFines FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"fine": user["payableFines"]}), 200
    else:
        return jsonify({"error": "User not found"}), 404

# ---------------------- API: Book Reservation ----------------------
@app.route("/api/reserve", methods=["POST"])
def reserve_book():
    data = request.get_json()
    user_id = data.get("user_id")
    book_id = data.get("book_id")

    if not user_id or not book_id:
        return jsonify({"error": "Missing user_id or book_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user has outstanding fines
    cursor.execute("SELECT payableFines FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user and user["payableFines"] > 0:
        conn.close()
        return jsonify({"error": "User has outstanding fines. Payment required."}), 403

    # Check if user already has 10 books reserved
    cursor.execute("SELECT COUNT(*) FROM reservations WHERE user_id = ?", (user_id,))
    book_count = cursor.fetchone()[0]
    if book_count >= 10:
        conn.close()
        return jsonify({"error": "User has reached the maximum borrowing limit (10 books)."}), 403

    # Reserve the book
    cursor.execute("INSERT INTO reservations (user_id, book_id, status, loan_date) VALUES (?, ?, 'Reserved', ?)" , (user_id, book_id, datetime.now().strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

    return jsonify({"message": "Book successfully reserved."}), 200

# ---------------------- API: Book Collection ----------------------
@app.route("/api/collect", methods=["POST"])
def collect_book():
    data = request.get_json()
    user_id = data.get("user_id")
    book_id = data.get("book_id")

    if not user_id or not book_id:
        return jsonify({"error": "Missing user_id or book_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user has outstanding fines
    cursor.execute("SELECT payableFines FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user and user["payableFines"] > 0:
        conn.close()
        return jsonify({"error": "User has outstanding fines. Payment required before collection."}), 403

    # Check if the book is reserved by the user
    cursor.execute("SELECT * FROM reservations WHERE user_id = ? AND book_id = ? AND status = 'Reserved'", (user_id, book_id))
    reservation = cursor.fetchone()
    if not reservation:
        conn.close()
        return jsonify({"error": "No active reservation found for this book."}), 404

    # Mark the book as collected
    cursor.execute("UPDATE reservations SET status = 'Collected' WHERE user_id = ? AND book_id = ?", (user_id, book_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Book successfully collected."}), 200

# ---------------------- API: Book Return ----------------------
@app.route("/api/return", methods=["POST"])
def return_book():
    data = request.get_json()
    user_id = data.get("user_id")
    book_id = data.get("book_id")

    if not user_id or not book_id:
        return jsonify({"error": "Missing user_id or book_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the book is borrowed by the user
    cursor.execute("SELECT loan_date FROM reservations WHERE user_id = ? AND book_id = ? AND status = 'Collected'", (user_id, book_id))
    reservation = cursor.fetchone()
    if not reservation:
        conn.close()
        return jsonify({"error": "No active loan found for this book."}), 404

    # Calculate overdue fines
    loan_date = datetime.strptime(reservation["loan_date"], '%Y-%m-%d')
    due_date = loan_date.replace(day=loan_date.day + 18)
    overdue_days = max((datetime.now() - due_date).days, 0)
    fine_amount = overdue_days * 0.15

    if fine_amount > 0:
        cursor.execute("UPDATE users SET payableFines = payableFines + ? WHERE id = ?", (fine_amount, user_id))

    # Mark the book as returned
    cursor.execute("UPDATE reservations SET status = 'Returned' WHERE user_id = ? AND book_id = ?", (user_id, book_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Book successfully returned.", "fine": fine_amount}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
