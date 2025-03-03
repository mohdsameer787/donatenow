from flask import Flask, render_template, request, redirect, url_for, flash,jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt  # Secure Password Storage

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB file size
app.secret_key = "your_secret_key"  # Required for `flash()`
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.secret_key = "your_secret_key_here"

class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Store hashed passwords
    addr = db.Column(db.String(50), nullable=False)
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
class Donatebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    image_filename = db.Column(db.String(200), nullable=False)
    condition = db.Column(db.String(255), nullable=False)
with app.app_context():
    db.create_all()  # Create tables

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']

        # Check if email already exists
        existing_user = Signup.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists. Please login.", "warning")
            return redirect(url_for('login'))

        # Hash password before storing
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Save to database
        new_user = Signup(name=name, email=email, password=hashed_password, addr=address,date=datetime.utcnow())
        db.session.add(new_user)
        db.session.commit()

        flash("Signup successful! You can now login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = Signup.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id  # Store user session
            session["user_name"] = user.name
            return jsonify({"success": True, "message": "Login successful!"})
        else:
            return jsonify({"success": False, "message": "Invalid email or password."})

    return render_template("login.html")
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    return f"Welcome {session['user_name']}! You are logged in."


@app.route("/donationform", methods=["GET", "POST"])
def donationform():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        date_str = request.form.get("pyear")  # This is a string like "2025-03-02"
        condition = request.form.get("condition")

        # Convert the string to a datetime.date object
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return "Invalid date format", 400

        # Handle file upload
        if 'imgfile' not in request.files:
            return "No file part", 400
        file = request.files['imgfile']
        if file.filename == '':
            return "No selected file", 400

        # Secure filename and save
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Insert into database
        donation = Donatebook(title=title, author=author, date=date_obj, image_filename=filename, condition=condition)
        db.session.add(donation)
        db.session.commit()

        return "Data submitted successfully"

    return render_template("donationform.html")


if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=4444)
