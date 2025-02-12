from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from picamera2 import Picamera2, Preview
from pyzbar.pyzbar import decode
import cv2

app = Flask(__name__, static_folder='static', template_folder='templates')
DB_NAME = "/Users/gamalieltun/Documents/DevOp/DCPE_2A_21_Group4/database.py" #change this file path to the database file path

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
    cursor.execute("INSERT INTO reservations (user_id, book_id, status) VALUES (?, ?, 'Reserved')", (user_id, book_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Book successfully reserved."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
