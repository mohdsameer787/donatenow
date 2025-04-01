from flask import Flask, render_template, request, redirect, url_for, flash,jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB file size
app.secret_key = "your_secret_key"  # Required for `flash()`
db = SQLAlchemy(app)

app.secret_key = "your_secret_key_here"

# List of prohibited drugs
prohibited_drugs = [
    "Marijuana", "Cocaine", "Heroin", "LSD", "Ecstasy",
    "Methamphetamine", "Opium", "Ketamine", "GHB", "Psilocybin"
]

class Signup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Store hashed passwords
    addr = db.Column(db.String(50), nullable=False)
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    phonenum = db.Column(db.String(50), nullable=False)
class Donatebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    image_filename = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100),nullable=False)
    condition = db.Column(db.String(255), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('signup.id'), nullable=False)
    donor = db.relationship('Signup', backref='donated_books')
    datep = db.Column(db.TIMESTAMP, default=datetime.utcnow)
class Donatemed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    exdate = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    mfgdate = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    category = db.Column(db.String(100),nullable=False)
    quantity = db.Column(db.String(100),nullable=False)
    dosage = db.Column(db.String(100),nullable=False)
    condition = db.Column(db.String(255), nullable=False)
    manufacturer = db.Column(db.String(100),nullable=False)
    image_filename = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(255), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('signup.id'), nullable=False)
    donor = db.relationship('Signup', backref='donated_med')
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
class Donatecloth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.String(255),  nullable=False)
    color = db.Column(db.String(255), nullable=False)
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    image_filename = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(255),  nullable=False)
    desc = db.Column(db.String(255), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('signup.id'), nullable=False)
    donor = db.relationship('Signup', backref='donated_cloth')
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
        contact = request.form['phonenum']

        # Check if email already exists
        existing_user = Signup.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists. Please login.", "warning")
            return redirect(url_for('login'))
        print(request.form)
        # Hash password before storing
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Save to database
        new_user = Signup(name=name, email=email, phonenum=contact, password=hashed_password, addr=address,date=datetime.utcnow())
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

    else:
        id = session["user_id"]
        user = Signup.query.filter_by(id=id).first()
        donations = Donatebook.query.all()  # Fetch data from the database
    return render_template('dashboard.html', donation=donations,user=user)

'''@app.route("/product")
def product():
       id = session["user_id"]
       donations = Donatebook.query.all() 
       return render_template("product.html",donations=donations,user=user)

'''

'''@app.route('/product/<int:id>')
def product(id):
    # Check in each table for the product based on the ID
    product = Donatebook.query.get(id) or Donatemed.query.get(id) or Donatecloth.query.get(id)
   
    if not product:
        return "Product not found", 404
    
    return render_template('product.html', product=product,user=user)
'''

@app.route('/product/<int:id>')
def product(id):
    category = request.args.get('category')
    user = Signup.query.filter_by(id=id).first()

    # Determine which table to query
    if category == 'book':
        product = Donatebook.query.get_or_404(id)
    elif category == 'medicine':
        product = Donatemed.query.get_or_404(id)
    elif category == 'cloth':
        product = Donatecloth.query.get_or_404(id)
    else:
        return "Invalid category", 400

    return render_template('product.html', product=product, category=category,user=user)

@app.route('/productlisting')
def productlisting():
        id = session["user_id"]
        user = Signup.query.filter_by(id=id).first()
        donations = Donatebook.query.all()  # Fetch data from the database
        donations1 = Donatemed.query.all()
        donations2 = Donatecloth.query.all()
        return render_template('productlisting.html', donation=donations,donation1=donations1,donation2=donations2,user=user)
   


@app.route("/donationformedi",methods=["GET", "POST"])
def donationformedi():
    if 'user_id' not in session:
        flash("Please log in to donate.")
        return redirect(url_for('login'))
    if request.method == "POST":
        name = request.form.get("name")
        manufacturer = request.form.get("manufacturer")
        exdate = request.form.get("exdate")  # This is a string like "2025-03-02"
        mfgdate = request.form.get("mfgdate")
        category = request.form.get("category")
        quantity = request.form.get("quantity")
        dosage = request.form.get("dosage")
        condition = request.form.get("condition")
        desc = request.form.get("desc")
        donor_id = session['user_id']
        # Check for prohibited drugs
        if any(drug.lower() in name.lower() for drug in prohibited_drugs):
              return "Donation rejected. This medicine is prohibited for donation.", 400
 
       # Convert the string to a datetime.date object
        try:
            exdate_obj = datetime.strptime(exdate, "%Y-%m-%d").date()
            mfgdate_obj = datetime.strptime(exdate, "%Y-%m-%d").date()

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
        donation = Donatemed(name=name, manufacturer=manufacturer, exdate=exdate_obj, mfgdate=mfgdate_obj, image_filename=filename, desc=desc, category=category, quantity=quantity, dosage=dosage, condition=condition, donor_id=donor_id, date=datetime.utcnow())
        db.session.add(donation)
        db.session.commit()

        return "Data submitted successfully"

    return render_template("donationformedi.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")



@app.route("/donationforcloth",methods=["GET", "POST"])
def donationforcloth():
    if 'user_id' not in session:
        flash("Please log in to donate.")
        return redirect(url_for('login')) 

    if request.method == "POST":
        type = request.form.get("type")
        condition = request.form.get("condition")
        size = request.form.get("size")  # This is a string like "2025-03-02"
        gender = request.form.get("gender")
        quantity = request.form.get("quantity")
        color = request.form.get("color")
        desc = request.form.get("desc")
        donor_id = session['user_id']

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
        donation = Donatecloth(type=type, condition=condition, date=datetime.utcnow(), image_filename=filename, size=size, gender=gender, quantity=quantity, color=color, desc=desc, donor_id=donor_id)
        db.session.add(donation)
        db.session.commit()

        return "Data submitted successfully"

    return render_template("donationforcloth.html")


@app.route("/donatebook", methods=["GET", "POST"])
def donatebook():
    if 'user_id' not in session:
        flash("Please log in to donate.")
        return redirect(url_for('login'))

    if request.method == "POST":
        title = request.form.get("title")
        author = request.form.get("author")
        date_str = request.form.get("pyear")  # This is a string like "2025-03-02"
        condition = request.form.get("condition")
        category = request.form.get("category")
        donor_id = session['user_id']
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
        donation = Donatebook(title=title, author=author, date=date_obj, image_filename=filename, category=category, condition=condition, donor_id=donor_id, datep=datetime.utcnow())
        db.session.add(donation)
        db.session.commit()

        return "Data submitted successfully"

    return render_template("donatebook.html")
@app.route("/logout")
def logout():
     session.pop('user_id')
     session.pop('user_name')
     return redirect("/")

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=4444)


