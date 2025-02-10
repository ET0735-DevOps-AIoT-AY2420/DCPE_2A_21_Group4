<<<<<<< HEAD
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
=======
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
import sqlite3
>>>>>>> demo
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure session key

DB_NAME = "library.db"

def get_db_connection():
    """Create a new database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Fetch results as dictionaries
    return conn

# ---------------------- API: Get All Books ----------------------
@app.route("/api/books", methods=["GET"])
def get_books():
    """API to fetch all books from SQLite."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT bookId, title, author, genre, image FROM books")
        books = cursor.fetchall()
        conn.close()

        books_list = [dict(book) for book in books]
        return jsonify(books_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------- API: Get Book Details ----------------------
@app.route("/api/book/<book_id>", methods=["GET"])
def get_book_info(book_id):
    """API to fetch book details from SQLite."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE bookId = ?", (book_id,))
        book = cursor.fetchone()
        conn.close()

        if book:
            return jsonify(dict(book))
        else:
            return jsonify({"error": "Book not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------- BOOK INFO PAGE ----------------------
@app.route("/bookinfo.html")
def bookinfo():
    """Book info page (loads data via API)."""
    return render_template("bookinfo.html")

# SQLite Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    fin_number = db.Column(db.String(50), nullable=True)
    student_card_qr = db.Column(db.String(255), nullable=True)
    payable_fines = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create database tables
with app.app_context():
    db.create_all()

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

<<<<<<< HEAD
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists! Please sign in.", "warning")
=======
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
>>>>>>> demo
            return redirect(url_for("signin"))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Sign-up successful! Please sign in.", "success")
        return redirect(url_for("signin"))

    return render_template("signup.html")

# ---------------------- SIGN IN ----------------------
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

<<<<<<< HEAD
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session["user_email"] = email
            session["user_id"] = user.id

            if not user.fin_number or not user.student_card_qr:
                flash("Please provide additional information.", "warning")
                return redirect(url_for("additional_info"))

            flash("Sign-in successful!", "success")
            return redirect(url_for("homepage"))

        flash("Invalid email or password!", "danger")
        return redirect(url_for("signin"))
=======
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
                return redirect(url_for("homepage"))

            flash("Invalid email or password!", "danger")
            return redirect(url_for("signin"))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for("signin"))
>>>>>>> demo

    return render_template("signin.html")

@app.route("/additional_info", methods=["GET", "POST"])
def additional_info():
    if "user_email" not in session or "user_id" not in session:
        flash("Please sign in to access this page.", "danger")
        return redirect(url_for("signin"))

    if request.method == "POST":
        fin_number = request.form["finNumber"].strip()
        student_card_qr = request.form["studentCardQR"].strip()

<<<<<<< HEAD
        user = User.query.get(session["user_id"])
        if user:
            user.fin_number = fin_number
            user.student_card_qr = student_card_qr
            db.session.commit()
=======
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET finNumber = ?, studentCardQR = ? WHERE id = ?",
                           (fin_number, student_card_qr, session["user_id"]))
            conn.commit()
            conn.close()

>>>>>>> demo
            flash("Additional info saved successfully!", "success")
            return redirect(url_for("homepage"))

    return render_template("additional_info.html")


# ---------------------- MAIN PAGES ----------------------
@app.route('/homepage')
def homepage():
<<<<<<< HEAD
    user_id = session.get("user_id")
    return render_template("HomePage.html", user_id=user_id)
=======
    return render_template("HomePage.html", user_id=session.get("user_id"))
>>>>>>> demo

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
    """API to handle book borrowing."""
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 403

    data = request.get_json()
    user_id = session["user_id"]
    book_id = data.get("bookId")
    branch = data.get("branch")

    if not book_id or not branch:
        return jsonify({"error": "Missing book ID or branch"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the book is already borrowed
        cursor.execute("SELECT * FROM loans WHERE bookId = ? AND userId = ?", (book_id, user_id))
        existing_loan = cursor.fetchone()

        if existing_loan:
            return jsonify({"error": "Book already borrowed"}), 409

        # Insert into Loans table
        cursor.execute("""
            INSERT INTO loans (bookId, userId, borrowDate, branch, cancelStatus, extendStatus)
            VALUES (?, ?, datetime('now'), ?, 'No', 'No')
        """, (book_id, user_id, branch))

        conn.commit()
        conn.close()

        return jsonify({"success": "Book borrowed successfully!"})

    except Exception as e:
        print("Error:", str(e))  # Debugging log
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
    """API to reserve books and store in the database."""
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
            cursor.execute(
                "INSERT INTO loans (bookId, userId, branch, borrowDate, cancelStatus, extendStatus) VALUES (?, ?, ?, datetime('now'), 'No', 'No')",
                (book["id"], user_id, book["branch"]),
            )

        conn.commit()
        conn.close()

        return jsonify({"success": "Books successfully reserved!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# ---------------------- RUN SERVER ----------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')