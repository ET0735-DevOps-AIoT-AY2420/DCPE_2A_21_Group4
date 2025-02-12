from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from datetime import datetime
from picamera2 import Picamera2, Preview
from pyzbar.pyzbar import decode
import cv2

<<<<<<< HEAD
app = Flask(__name__, static_folder='static', template_folder='templates')
DB_NAME = "library.db"
=======
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure session key

DB_NAME = "/home/pi/ET0735/DCPE_2A_21_Group4/DCPE_2A_21_Group4/library.db"
>>>>>>> collection

def get_db_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------- Serve Web Pages ----------------------
@app.route('/')
def home():
    """Render the Home Page."""
    return render_template('HomePage.html')

@app.route('/signin')
def signin():
    """Render the Sign-in Page."""
    return render_template('signin.html')

@app.route('/signup')
def signup():
    """Render the Sign-up Page."""
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    """Render the User Dashboard."""
    return render_template('userdashboard.html')

@app.route('/reserve')
def reserve_page():
    """Render the Reserved Books Page."""
    return render_template('reserved.html')

# ---------------------- API: Get Fine Amount ----------------------
@app.route("/api/get_fine", methods=["GET"])
def get_fine():
    """Retrieve the fine amount for a specific user."""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT payableFines FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

<<<<<<< HEAD
    if user:
        return jsonify({"fine": user["payableFines"]}), 200
    else:
        return jsonify({"error": "User not found"}), 404
=======
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for("signin"))

    return render_template("signin.html")

@app.route("/additional_info", methods=["GET", "POST"])
def additional_info():
    if "user_email" not in session or "user_id" not in session:
        flash("Please sign in to access this page.", "danger")
        return redirect(url_for("signin"))

    if request.method == "POST":
        fin_number = request.form["finNumber"].strip()
        student_card_qr = request.form["studentCardQR"].strip()

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET finNumber = ?, studentCardQR = ? WHERE id = ?",
                           (fin_number, student_card_qr, session["user_id"]))
            conn.commit()
            conn.close()

            flash("Additional info saved successfully!", "success")
            return redirect(url_for("homepage"))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for("additional_info"))

    return render_template("additional_info.html")


# ---------------------- MAIN PAGES ----------------------
@app.route('/homepage')
def homepage():
    return render_template("HomePage.html", user_id=session.get("user_id"))

@app.route('/viewmore.html')
def viewmore():
    return render_template("viewmore.html")

@app.route('/reserved.html')
def reserved():
    return render_template("reserved.html")

@app.route('/branch.html')
def branch():
    """Branch selection page."""
    book_id = request.args.get('bookId')  # Get bookId from the URL
    if not book_id:
        flash("Book ID is missing!", "danger")
        return redirect(url_for("homepage"))

    return render_template("branch.html", book_id=book_id)

@app.route("/borrow", methods=["POST"])
def borrow_book():
    """API to handle book borrowing and prevent duplicate reservations."""
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 403
>>>>>>> collection

# ---------------------- API: Book Reservation ----------------------
@app.route("/api/reserve", methods=["POST"])
def reserve_book():
    """Allow a user to reserve a book if they have no outstanding fines."""
    data = request.get_json()
    user_id = data.get("user_id")
    book_id = data.get("book_id")

    if not user_id or not book_id:
        return jsonify({"error": "Missing user_id or book_id"}), 400

<<<<<<< HEAD
    conn = get_db_connection()
=======
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Check if the book is already borrowed by this user at the same branch
        cursor.execute("""
            SELECT id FROM loans WHERE bookId = ? AND userId = ? AND returnDate IS NULL
        """, (book_id, user_id))
        existing_loan = cursor.fetchone()

        if existing_loan:
            return jsonify({"error": "You have already borrowed this book!"}), 409

        # ✅ Insert into Loans table
        cursor.execute("""
            INSERT INTO loans (bookId, userId, borrowDate, branch, cancelStatus)
            VALUES (?, ?, datetime('now'), ?, 'No')
        """, (book_id, user_id, branch))

        conn.commit()
        conn.close()

        return jsonify({"success": "Book borrowed successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/userdashboard")
def userdashboard():
    if "user_email" not in session:
        flash("Please sign in to access your dashboard.", "danger")
        return redirect(url_for("signin"))

    return render_template("userdashboard.html", email=session["user_email"])
@app.route("/view_users")
def view_users():
    conn = sqlite3.connect(DB_NAME)
>>>>>>> collection
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
    """Allow a user to collect a reserved book."""
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
    """Process the return of a borrowed book and calculate fines if overdue."""
    data = request.get_json()
    user_id = data.get("user_id")
    book_id = data.get("book_id")

<<<<<<< HEAD
    if not user_id or not book_id:
        return jsonify({"error": "Missing user_id or book_id"}), 400
=======
@app.route("/reserve_books", methods=["POST"])
def reserve_books():
    """API to reserve books and prevent duplicate reservations."""
    if "user_id" not in session:
        return jsonify({"error": "Please sign in to reserve books."}), 403
>>>>>>> collection

    conn = get_db_connection()
    cursor = conn.cursor()

<<<<<<< HEAD
    # Check if the book is borrowed by the user
    cursor.execute("SELECT loan_date FROM reservations WHERE user_id = ? AND book_id = ? AND status = 'Collected'", (user_id, book_id))
    reservation = cursor.fetchone()
    if not reservation:
=======
        if not borrowed_books:
            return jsonify({"error": "No books selected for reservation."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        for book in borrowed_books:
            book_id = book["id"]
            branch = book["branch"]

            # ✅ Check if the book is already reserved by this user
            cursor.execute("""
                SELECT id FROM loans WHERE bookId = ? AND userId = ? AND returnDate IS NULL
            """, (book_id, user_id))
            existing_reservation = cursor.fetchone()

            if existing_reservation:
                print(f"Skipping duplicate reservation for book {book_id}")
                continue  # Skip duplicate reservation

            # ✅ Reserve book and mark it as unavailable
            cursor.execute("""
                INSERT INTO loans (bookId, userId, branch, borrowDate, cancelStatus, extendStatus)
                VALUES (?, ?, ?, datetime('now'), 'No', 'No')
            """, (book_id, user_id, branch))

        conn.commit()
>>>>>>> collection
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
    port = int(os.environ.get("PORT", 5000))  # Default to 5000, but can be changed
    app.run(host="0.0.0.0", port=port, debug=True)

<<<<<<< HEAD
=======

# ---------------------- RUN SERVER ----------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
>>>>>>> collection
