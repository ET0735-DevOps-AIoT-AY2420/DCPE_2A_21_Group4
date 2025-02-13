from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from database import borrow_book
import sqlite3
import os
import subprocess
import atexit


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))



DB_NAME = "/home/pi/ET0735/DCPE_2A_21_Group4/DCPE_2A_21_Group4/library.db"  # Adjust path when deploying

lcd_process = subprocess.Popen(
    ["python3", "/home/pi/ET0735/DCPE_2A_21_Group4/DCPE_2A_21_Group4/src/lcd_menu.py"],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)

# Read LCD output periodically (for debugging)
def check_lcd_output():
    if lcd_process.poll() is None:
        stdout, stderr = lcd_process.communicate(timeout=1)
        print("LCD Output:", stdout)
        print("LCD Errors:", stderr)


# Function to stop the LCD menu subprocess
def stop_lcd_menu():
    if lcd_process.poll() is None:  # Check if the process is still running
        lcd_process.terminate()  # Terminate the process
        lcd_process.wait()  # Wait for the process to exit
        print("LCD menu script stopped.")

# Register the cleanup function to run when the Flask app exits
atexit.register(stop_lcd_menu)

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Fetch results as dictionaries
    return conn

# ---------------------- SIGN UP ----------------------
@app.route("/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirmPassword"].strip()

        if not name or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("signup"))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if user already exists
            cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Email already exists! Please sign in.", "warning")
                return redirect(url_for("signin"))

            # Insert new user into database
            cursor.execute(
                "INSERT INTO users (name, email, password, finNumber, studentCardQR, payableFines) VALUES (?, ?, ?, NULL, NULL, 0)",
                (name, email, password),
            )
            conn.commit()
            conn.close()

            flash("Sign-up successful! Please sign in.", "success")
            return redirect(url_for("signin"))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for("signup"))

    return render_template("signup.html")

# ---------------------- SIGN IN ----------------------
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user and user["password"] == password:
                session["user_id"] = user["id"]
                session["user_email"] = user["email"]

                if user["finNumber"] is None or user["studentCardQR"] is None:
                    flash("Please provide additional information.", "warning")
                    return redirect(url_for("additional_info"))

                flash("Sign-in successful!", "success")
                return redirect(url_for("selectBranch"))

            flash("Invalid email or password!", "danger")
            print("DEBUG: Login failed due to incorrect credentials")
            return redirect(url_for("signin"))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            print("DEBUG: Exception occurred:", str(e))  # 🔍 Debugging output
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
    
# ---------------------- API: Get Books for a Specific Branch ----------------------
@app.route("/api/branch_books/<branch_id>", methods=["GET"])
def get_branch_books(branch_id):
    """Fetch available books in a specific branch."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT books.*, branch_books.status FROM books 
            INNER JOIN branch_books ON books.bookId = branch_books.bookId
            WHERE branch_books.branchId = ? 
        """, (branch_id,))
        
        columns = [column[0] for column in cursor.description]
        books = cursor.fetchall()
        books = [dict(zip(columns, row)) for row in books]  # <-- FIX applied
        conn.close()

        return jsonify(books)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------- API: Get Book Availability in a Branch ----------------------
@app.route("/api/book/<book_id>/<branch_id>", methods=["GET"])
def get_book_availability(book_id, branch_id):
    """Fetch book details and check its availability in a specific branch."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT books.*, branch_books.status 
            FROM books
            INNER JOIN branch_books ON books.bookId = branch_books.bookId
            WHERE books.bookId = ? AND branch_books.branchId = ?
        """, (book_id, branch_id))
        book = cursor.fetchone()
        conn.close()

        if book:
            columns = [column[0] for column in cursor.description]
            book_dict = dict(zip(columns, book))  # <-- FIX applied
            return jsonify(book_dict)
        else:
            return jsonify({"error": "Book not found in this branch"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------- API: Borrow a Book ----------------------
@app.route("/borrow", methods=["POST"])
def borrow_book_api():
    """Mark a book as borrowed in a specific branch."""
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 403

    data = request.get_json()
    user_id = session["user_id"]
    book_id = data.get("bookId")
    branch_id = data.get("branchId")

    if not book_id or not branch_id:
        return jsonify({"error": "Missing book ID or branch ID"}), 400

    try:
        result = borrow_book(branch_id, book_id, user_id)
        return jsonify({"success": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------- BOOK INFO PAGE ----------------------
@app.route("/bookinfo.html")
def bookinfo():
    """Book info page (loads data via API)."""
    return render_template("bookinfo.html")

# ---------------------- Select branch ----------------------
@app.route("/selectBranch", methods=["GET", "POST"])
def selectBranch():
    """Render the branch selection page and handle branch selection."""
    if request.method == "POST":
        branch_id = request.form.get("branch_id")  # Get the selected branch ID
        print(f"Setting branchId to: {branch_id}") 
        if not branch_id:
            flash("Please select a branch.", "warning")
            return redirect(url_for("selectBranch"))
        

        session["branchId"] = branch_id  # Save the branch_id in session

        print(f"Branch ID set to: {session.get('branchId')}")

        print(f"Redirecting to homepage...")
        # Redirect to the homepage with the selected branch ID
        return redirect("/homepage")

    return render_template("selectBranch.html")

# ---------------------- MAIN PAGES ----------------------
@app.route("/homepage")
def homepage():
    """Render homepage and check if a branch is selected."""
    # Get branchId from Flask session
    branch_id = session.get("branchId")
    print(f"Session branchId: {branch_id}")

    # If branch_id is not found in session, redirect to selectBranch
    if not branch_id:
        flash("Please select a branch first.", "warning")
        return redirect(url_for("selectBranch"))

    # If user is not signed in, redirect to sign-in page
    user_id = session.get("user_id")
    print(f"User Id: {user_id}")
    if not user_id:
        flash("Please sign in to access the homepage.", "danger")
        return redirect(url_for("signin"))

    # Fetch books for the selected branch
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT books.*, branch_books.status AS branch_status
                          FROM books
                          INNER JOIN branch_books ON books.bookId = branch_books.bookId
                          WHERE branch_books.branchId = ?''', (branch_id,))
    books = cursor.fetchall()
    conn.close()

    return render_template("homepage.html", branch_id=branch_id, user_id=user_id, books=books)

@app.route('/viewmore')
def viewmore():
    return render_template("viewmore.html")

@app.route('/reserved.html')
def reserved():
    return render_template("reserved.html")

@app.route('/borrowed_books.html')
def borrowed_books():
    return render_template("borrowed_books.html")

@app.route('/branch.html')
def branch():
    """Branch selection page."""
    book_id = request.args.get('bookId')  # Get bookId from the URL
    if not book_id:
        flash("Book ID is missing!", "danger")
        return redirect(url_for("homepage"))

    return render_template("branch.html", book_id=book_id)

@app.route("/userdashboard")
def userdashboard():
    if "user_email" not in session:
        flash("Please sign in to access your dashboard.", "danger")
        return redirect(url_for("signin"))

    return render_template("userdashboard.html", email=session["user_email"])

@app.route("/view_users")
def view_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    return jsonify(users)

@app.route("/view_loans")
def view_loans():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM loans")
    loans = cursor.fetchall()
    conn.close()

    return jsonify(loans)

@app.route("/reserve_books", methods=["POST"])
def reserve_books():
    """API to reserve books and prevent duplicate reservations."""
    if "user_id" not in session:
        return jsonify({"error": "Please sign in to reserve books."}), 403

    try:
        data = request.get_json()
        user_id = session["user_id"]
        borrowed_books = data.get("borrowedBooks", [])

        if not borrowed_books:
            return jsonify({"error": "No books selected for reservation."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        for book in borrowed_books:
            book_id = book["id"]
            branch = book["branch"]

            # Check if the book is already reserved by this user
            cursor.execute("""
                SELECT id FROM loans WHERE bookId = ? AND userId = ? AND returnDate IS NULL
            """, (book_id, user_id))
            existing_reservation = cursor.fetchone()

            if existing_reservation:
                print(f"Skipping duplicate reservation for book {book_id}")
                continue  # Skip duplicate reservation

            # Reserve book and mark it as unavailable
            cursor.execute("""
                INSERT INTO loans (bookId, userId, branch, borrowDate, cancelStatus, extendStatus)
                VALUES (?, ?, ?, datetime('now'), 'No', 'No')
            """, (book_id, user_id, branch))

        conn.commit()
        conn.close()

        return jsonify({"success": "Books successfully reserved!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------- RUN SERVER ----------------------
if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
 