from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure secret key for session management

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

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists! Please sign in.", "warning")
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

        user = User.query.get(session["user_id"])
        if user:
            user.fin_number = fin_number
            user.student_card_qr = student_card_qr
            db.session.commit()
            flash("Additional info saved successfully!", "success")
            return redirect(url_for("homepage"))

    return render_template("additional_info.html")

# ---------------------- MAIN PAGES ----------------------
@app.route('/HomePage.html')
def homepage():
    user_id = session.get("user_id")
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

@app.route("/userdashboard")
def userdashboard():
    if "user_email" not in session:
        flash("Please sign in to access your dashboard.", "danger")
        return redirect(url_for("signin"))

    return render_template("userdashboard.html", email=session["user_email"])

# ---------------------- RUN SERVER ----------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
