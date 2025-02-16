from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from database import get_db_connection
import sqlite3
import os
import subprocess
import atexit
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))



DB_NAME = "C:\Local_Git_Repository\LibraryMS\DCPE_2A_21_Group4\library.db" 

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

# ---------------------- Borrow Book Func ----------------------

def borrow_book(branch_bookId, book_id, user_id, isbn, branch_id):
    """Mark a book as borrowed in a specific branch."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            print(f"Receiving Data: {branch_bookId},{book_id},{user_id},{isbn},{branch_id}")

            # Check if the book is available in the selected branch
            cursor.execute(''' 
                SELECT id FROM branch_books
                WHERE branchId = ? AND bookId = ? AND status = 'Available'
            ''', (branch_id, book_id))
            branch_book = cursor.fetchone()

            if branch_book:
                branch_book_id = branch_book[0]

                # Insert a borrow request (status = 'pending')
                cursor.execute(''' 
                    INSERT INTO loans (branchBookId, bookId, userId, isbn, borrowDate, branch, status)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?, 'pending')
                ''', (branch_book_id, book_id, user_id, isbn, branch_id))

                conn.commit()

                cursor.execute("""
                    SELECT COUNT(*) FROM loans WHERE userId = ? AND status = 'pending'
                """, (user_id,))
                updated_count = cursor.fetchone()[0]

                return jsonify({"success": "Book borrowed", "updated_count": updated_count})

            else:
                print("Book is already borrowed or not available in this branch.")
                return jsonify({"error": "Book is already borrowed or not available in this branch."}), 400

    except Exception as e:
        print(f"Error while borrowing the book: {e}")
        return jsonify({"error": "Internal server error. Please try again later."}), 500


def get_book_isbn(book_id):
    """Fetch ISBN of a book from the books table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(''' 
            SELECT isbn FROM books WHERE bookId = ?
        ''', (book_id,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return the ISBN
        return None  # Return None if no ISBN is found
    
# ---------------------- EXTEND ----------------------
@app.route('/get_loans', methods=['GET'])
def get_loans():
    """Fetch all loans for a given user with book details."""
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    conn = get_db_connection() 
    cursor = conn.cursor()

    query = """
        SELECT 
            loans.id, 
            books.title, 
            loans.dueDate, 
            loans.extendStatus,
            books.genre, 
            books.image
        FROM loans
        INNER JOIN books ON loans.bookId = books.bookId
        WHERE loans.userId = ? AND loans.status = 'reserved'
    """
    cursor.execute(query, (user_id,))
    loans = cursor.fetchall()

    conn.close()

    return jsonify([
        {
            "id": loan[0],
            "title": loan[1],
            "dueDate": loan[2],  
            "extendStatus": loan[3], 
            "genre": loan[4],
            "image": loan[5]

        }
        for loan in loans
    ])

@app.route('/extend_loan', methods=['POST'])
def extend_loan():
    """Extend the loan due date for a specific loan."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        print(f"Received data: {data}")  # Debugging log

        loan_id = data.get('loanId')
        new_due_date = data.get('newDueDate')

        if not loan_id or not new_due_date:
            return jsonify({"error": "Missing loanId or newDueDate"}), 400
        
        # Parse the 'newDueDate'
        try:
            new_due_date = datetime.strptime(new_due_date, "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as e:
            return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
        
        print(f"Parsed newDueDate: {new_due_date}")

        # Fetch the current loan details
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT dueDate, extendStatus FROM loans WHERE id = ?"
        cursor.execute(query, (loan_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return jsonify({"error": "Loan not found"}), 404

        old_due_date = result[0]  # Get dueDate from database

        if old_due_date is None:
            old_due_date = datetime.today().strftime("%Y-%m-%d")

        old_due_date = datetime.strptime(old_due_date, "%Y-%m-%d")
        new_due_date = old_due_date + timedelta(days=7)  # Or use the passed-in date if needed

        update_query = """
            UPDATE loans
            SET dueDate = ?, extendDate = ?, extendStatus = 'Yes'
            WHERE id = ?
        """
        cursor.execute(update_query, (new_due_date.strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d"), loan_id))
        conn.commit()
        conn.close()

        print(f"Loan {loan_id} extended successfully. New due date: {new_due_date.strftime('%Y-%m-%d')}")

        return jsonify({"message": "Loan extended successfully", "new_due_date": new_due_date.strftime("%Y-%m-%d")})

    except Exception as e:
        print(f"Error in /extend_loan: {e}")  # Debugging log
        return jsonify({"error": str(e)}), 500

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
@app.route("/api/borrow_book", methods=["POST"])
def borrow_book_api():
    """Mark a book as borrowed in a specific branch."""
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 403
    
    data = request.get_json()
    print(f"Received data: {data}")  # Log the received data

    user_id = session["user_id"]
    book_id = str(data.get("bookId"))
    branch_bookId = data.get("bookId")
    branch_id = data.get("branchId")

   

    if not book_id or not branch_bookId:
        return jsonify({"error": "Missing book ID or branch ID"}), 400

    try:
        isbn = get_book_isbn(book_id)
        if not isbn:
            return jsonify({"error": "ISBN not found for the given book."}), 400
        
        print(f"Senting Data: {branch_bookId},{book_id},{user_id},{isbn},{branch_id}")
        result = borrow_book(branch_bookId, book_id, user_id, isbn, branch_id)
        if result:
            return jsonify({"success": "Book borrow request created successfully."})
        else:
            return jsonify({"error": "Book is already borrowed or not available."}), 400
        
    except Exception as e:
        print(f"Error in borrow_book_api: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
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

    books_list = []
    for book in books:
        books_list.append({
            "id":book[0],
            "bookId": book[1],  
            "title": book[2],    
            "author": book[3],    
            "genre": book[4],     
            "isbn": book[5],      
            "image": book[6],     
            "language": book[7],  
            "status": book[8],    
            "summary": book[9] 
        })

    return render_template("homepage.html", branch_id=branch_id, user_id=user_id, books=books_list)

# ---------------------- View More ----------------------

@app.route("/viewmore")
def viewmore():
    """Render the viewmore page with books from the selected branch."""
    
    branch_id = session.get("branchId")
    if not branch_id:
        flash("Please select a branch first.", "warning")
        return redirect(url_for("selectBranch"))

   
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT books.*, branch_books.status AS branch_status
        FROM books
        INNER JOIN branch_books ON books.bookId = branch_books.bookId
        WHERE branch_books.branchId = ?
    ''', (branch_id,))
    books = cursor.fetchall()
    conn.close()

    books_list = []
    for book in books:
        books_list.append({
            "id":book[0],
            "bookId": book[1],  
            "title": book[2],    
            "author": book[3],    
            "genre": book[4],     
            "isbn": book[5],      
            "image": book[6],     
            "language": book[7],  
            "status": book[8],    
            "summary": book[9] 
        })

    return render_template("viewmore.html", branch_id=branch_id, books=books_list)

# ---------------------- BOOK INFO PAGE ----------------------
@app.route("/bookinfo")
def bookinfo():
    """Book info page (loads data via API)."""
    book_id = request.args.get('bookId')  # Get the book ID from the query parameter
    branch_id = request.args.get('branchId')  # Get the branch ID from the query parameter
    
    if not book_id or not branch_id:
        flash("Book or branch not selected.", "warning")
        return redirect(url_for("homepage"))

    # Fetch the book details based on book_id
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch book details
    cursor.execute('''SELECT * FROM books WHERE bookId = ?''', (book_id,))
    book = cursor.fetchone()

    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for("viewmore"))

    # Fetch book availability at the specific branch
    cursor.execute('''SELECT status FROM branch_books WHERE bookId = ? AND branchId = ?''', (book_id, branch_id))
    branch_book = cursor.fetchone()

    conn.close()

    if not branch_book:
        flash("Book not available at this branch.", "danger")
        return redirect(url_for("viewmore"))

    # If book and availability at branch are found, pass them to the template
    book_details = {
        "id": book[0],
        "bookId": book[1],  
        "title": book[2],    
        "author": book[3],    
        "genre": book[4],     
        "isbn": book[5],      
        "image": book[6],     
        "language": book[7],  
        "status": book[8],    
        "summary": book[9]  
    }

   
    book_details['branch_status'] = branch_book[0]

    user_id = session.get("user_id")

    return render_template("bookinfo.html", book=book_details,user_id=user_id)



@app.route('/api/reserved')
def reserved():
    """Display the reserved books for the current user."""
    user_id = request.args.get('user_id')  # Get the user_id from the query parameter
    branch_id = request.args.get('branchId')
    
    if  not user_id or not branch_id:
        return redirect(url_for('signin'))  # Redirect to login if user_id is not provided
    
    try:
        # Fetch the reserved books for the user from the loans table
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT b.bookId, b.title, b.author, b.image, l.status, l.branch 
            FROM books b
            INNER JOIN loans l ON b.bookId = l.bookId
            WHERE l.userId = ? AND l.branch = ? AND l.status = 'pending'
        ''', (user_id, branch_id))
        reserved_books = cursor.fetchall()
        conn.close()
        
        # Convert to JSON format
        books_list = [
            {"bookId": row[0], "title": row[1], "author": row[2],  "image": row[3], "status": row[4], "branch": row[5]}
            for row in reserved_books
        ]

        return jsonify(books_list)  # Returns JSON data

    except Exception as e:
        print(f"Error fetching reserved books: {e}")
        return jsonify({"error": "An error occurred while fetching reservations"}), 500
    

@app.route('/reserved')
def reserved_page():
    user_id = request.args.get('user_id')
    branch_id = request.args.get('branchId')

    if not user_id or not branch_id:
        return redirect(url_for('signin'))  # Redirect to login if user_id or branch_id is not provided

    return render_template('reserved.html', user_id=user_id, branch_id=branch_id)



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
    user_id = session.get('user_id')  # Get the logged-in user ID from session
    if not user_id:
        return "User not logged in", 401  # Handle unauthenticated users

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, createdAt, payableFines FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) FROM loans 
        WHERE userId = ? AND status = 'reserved'
    """, (user_id,))
    reservedCount = cursor.fetchone()[0]  # Get count of reserved books

    cursor.execute("""
        SELECT loans.bookId, books.title, books.author, books.genre, 
               loans.borrowDate, loans.returnDate
        FROM loans 
        JOIN books ON loans.bookId = books.bookId
        WHERE loans.userId = ? AND loans.status = 'returned'
        ORDER BY loans.returnDate DESC
    """, (user_id,))

    returned_books = cursor.fetchall()


    conn.close()

    if user:
        return render_template('userdashboard.html', user=user, reservedCount=reservedCount, returned_books=returned_books)
    else:
        return "User not found", 404

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

@app.route("/api/borrowed_books", methods=["GET"])
def get_borrowed_books():
    """Fetch borrowed books for the current user."""
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 403

    user_id = session["user_id"]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT b.bookId, b.title, b.author, l.status FROM books b
                          INNER JOIN loans l ON b.bookId = l.bookId
                          WHERE l.userId = ? AND l.status = 'pending' ''', (user_id,))
        borrowed_books = cursor.fetchall()
        conn.close()

        return jsonify([dict(zip([column[0] for column in cursor.description], row)) for row in borrowed_books])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/cancel_borrowed_book/<book_id>", methods=["POST"])
def cancel_borrowed_book(book_id):
    """Cancel the borrowed book."""
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 403

    user_id = session["user_id"]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get branchBookId before deleting
        cursor.execute("""
            SELECT branchBookId FROM loans 
            WHERE bookId = ? AND userId = ? AND status = 'pending'
        """, (book_id, user_id))
        branch_book = cursor.fetchone()

        if not branch_book:
            return jsonify({"error": "No pending loan found for this book."}), 400

        branch_book_id = branch_book[0]

        cursor.execute('''DELETE FROM loans WHERE bookId = ? AND userId = ? AND status = 'pending' ''', (book_id, user_id))

        cursor.execute("""
            SELECT COUNT(*) FROM loans 
            WHERE bookId = ? AND (status = 'reserved' OR status = 'borrowed')
        """, (book_id,))
        active_loans = cursor.fetchone()[0]

        # If no active loans or reservations exist, make the book "Available" again
        if active_loans == 0:
            cursor.execute("""
                UPDATE branch_books 
                SET status = 'Available' 
                WHERE id = ?
            """, (branch_book_id,))

        conn.commit()
        conn.close()

        return jsonify({"success": "Book cancelled successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reserve_book", methods=["POST"])
def reserve_book():
    """API to reserve multiple books (max 10) and prevent duplicate reservations."""
    if "user_id" not in session:
        return jsonify({"error": "Please sign in to reserve books."}), 403

    try:
        data = request.get_json()
        user_id = session["user_id"]
        borrowed_books = data.get("borrowedBooks", [])

        if not borrowed_books:
            return jsonify({"error": "No books selected for reservation."}), 400

        if len(borrowed_books) > 10:
            return jsonify({"error": "You can reserve a maximum of 10 books at a time."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        reserved_count = 0

        for book in borrowed_books:
            book_id = book["id"]
            branch = book["branch"]

            # Check if the book is already reserved by this user
            cursor.execute("""
                SELECT id FROM loans 
                WHERE bookId = ? AND userId = ? AND status = 'reserved' AND returnDate IS NULL
            """, (book_id, user_id))
            existing_reservation = cursor.fetchone()

            if existing_reservation:
                print(f"Skipping duplicate reservation for book {book_id}")
                continue  # Skip duplicate reservation

            # Reserve book and mark it as reserved
            cursor.execute("""
                UPDATE loans
                SET status = 'reserved'
                WHERE bookId = ? AND userId = ? AND status = 'pending'
            """, (book_id, user_id))

            cursor.execute("""
                UPDATE branch_books
                SET status = 'Unavailable'
                WHERE bookId = ? AND branchId = ? AND status = 'Available'
            """, (book_id, branch))

            reserved_count += 1

        conn.commit()
        conn.close()

        if reserved_count == 0:
            return jsonify({"error": "No new books were reserved. Check for duplicates or pending status."}), 400

        return jsonify({"success": f"{reserved_count} books successfully reserved!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/get_reserved_count', methods=['GET'])
def get_reserved_count():
    user_id = request.args.get('userId')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Count number of reserved books for the current user
    cursor.execute("""
        SELECT COUNT(*) FROM loans WHERE userId = ? AND status = 'pending'
    """, (user_id,))
    
    count = cursor.fetchone()[0]

    conn.close()
    return jsonify({"count": count})


# ---------------------- RUN SERVER ----------------------
if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
 