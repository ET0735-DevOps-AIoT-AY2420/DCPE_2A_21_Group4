from flask import Flask, request, render_template, redirect, url_for, flash, session
from firebase_setup import db  # Import Firestore client
import os, re

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure secret key for session management

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
            users_ref = db.collection("users")
            existing_user = users_ref.where("email", "==", email).stream()

            if any(existing_user):
                flash("Email already exists! Please sign in.", "warning")
                return redirect(url_for("signin"))

            new_user = users_ref.add({
                "name": name,
                "email": email,
                "password": password,
                "finNumber": None,
                "studentCardQR": None,
                "payableFines": 0,
                "createdAt": db.collection("users").document().get().create_time
            })

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
            users_ref = db.collection("users")
            query = users_ref.where("email", "==", email).stream()
            user = None
            user_id = None

            for doc in query:
                user = doc.to_dict()
                user_id = doc.id  # Firestore Document ID

                if user and user["password"] == password:
                    session["user_email"] = email
                    session["user_id"] = user_id  # Store User ID in session

                    if not user.get("finNumber") or not user.get("studentCardQR"):
                        flash("Please provide additional information.", "warning")
                        return redirect(url_for("additional_info"))

                    flash("Sign-in successful!", "success")
                    return redirect(url_for("homepage"))
                else:
                    flash("Incorrect Password.","danger")
                    return redirect(url_for("signin"))


            flash("Invalid email or password!", "danger")
            return redirect(url_for("signin"))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for("signin"))

    return render_template("signin.html")

# ---------------------- ADDITIONAL INFO ----------------------
@app.route("/additional_info", methods=["GET", "POST"])
def additional_info():
    if "user_email" not in session or "user_id" not in session:
        flash("Please sign in to access this page.", "danger")
        return redirect(url_for("signin"))

    if request.method == "POST":
        fin_number = request.form["finNumber"].strip()
        student_card_qr = request.form["studentCardQR"].strip()

         # FIN number format 
        fin_pattern = r"^[A-Z]\d{7}[A-Z]$"

        qr_pattern = r"^\d{7}$"

        if not re.match(fin_pattern, fin_number):
            flash("Incorrect FIN number format! It should follow this pattern: A1234567Z", "danger")
            return redirect(url_for("additional_info"))
        
        if not re.match(qr_pattern, student_card_qr):
            flash("Incorrect Student Card QR format! It must be exactly 7 digits.", "danger")
            return redirect(url_for("additional_info"))

        try:
            user_doc_ref = db.collection("users").document(session["user_id"])
            user_doc_ref.update({
                "finNumber": fin_number,
                "studentCardQR": student_card_qr
            })

            flash("Additional info saved successfully!", "success")
            return redirect(url_for("homepage"))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for("additional_info"))

    return render_template("additional_info.html")

# ---------------------- MAIN PAGES ----------------------
@app.route('/HomePage.html')
def homepage():
    user_id = session.get("user_id")  # Get user ID from session
    return render_template("HomePage.html", user_id=user_id)

@app.route('/viewmore.html')
def viewmore():
    return render_template("viewmore.html")

@app.route('/bookinfo.html')
def bookinfo():
    document_id = request.args.get('documentId')
    return render_template("bookinfo.html", document_id=document_id)

@app.route('/branch.html')
def branch():
    document_id = request.args.get('documentId')
    return render_template("branch.html", document_id=document_id)

@app.route('/reserved.html')
def reserved():
    return render_template("reserved.html")


@app.route("/userdashboard.html")
def userdashboard():
    if "user_email" not in session:
        flash("Please sign in to access your dashboard.", "danger")
        return redirect(url_for("signin"))

    return render_template("userdashboard.html", email=session["user_email"])


# ---------------------- RUN SERVER ----------------------
if __name__ == '__main__':
    app.run(debug=True, port = 5001)
