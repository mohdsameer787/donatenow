from flask import Flask, render_template, request, redirect, url_for, flash,jsonify, session, send_file
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime,date
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

from flask_login import current_user,LoginManager,UserMixin,login_user
from sqlalchemy import func


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB file size
app.secret_key = "sms0123456789abcdef1234567890" # Required for `flash()`
# Load signatures and logo
SONU_SIGNATURE = "static/IMG_20250405_081516.jpg"  # Your signature image
SANDEEP_SIGNATURE = "static/signature_sandeep.png"  # Sandeep's signature
SAMEER_SIGNATURE = "static/signature_sameer.png"  # Sameer's signature
LOGO_PATH = "static/logo2.png"  # DonateNow logo
# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
db = SQLAlchemy(app)


# List of prohibited drugs
prohibited_drugs = [
    "Marijuana", "Cocaine", "Heroin", "LSD", "Ecstasy",
    "Methamphetamine", "Opium", "Ketamine", "GHB", "Psilocybin"
]

class Signup(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Store hashed passwords
    addr = db.Column(db.String(50), nullable=False)
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    phonenum = db.Column(db.String(50), nullable=False)
    donation_count = db.Column(db.Integer, default=0)
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
class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('signup.id'))
    item = db.Column(db.String(50))  # e.g., 'books', 'clothes', 'medicines'
    campaign = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.utcnow)
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    desc = db.Column(db.Text)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
class Contact(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_num = db.Column(db.String(15), nullable=False)  # Adjust to match your schema
    massage = db.Column(db.Text, nullable=True)
    subject = db.Column(db.Text, nullable=True)
    date = db.Column(db.TIMESTAMP, default=datetime.utcnow)


with app.app_context():
    db.create_all()  # Create tables

def __repr__(self):
        return f"<Campaign {self.title}>"
def remove_expired_medicines():
    today = date.today()
    expired = Donatemed.query.filter(Donatemed.exdate < today).all()
    for med in expired:
        db.session.delete(med)
    db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return Signup.query.get(int(user_id))
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
            login_user(user)
            session["user_id"] = user.id  # Store user session
            session["user_name"] = user.name
            return jsonify({"success": True, "message": "Login successful!"})
        else:
            return jsonify({"success": False, "message": "Invalid email or password."})

    return render_template("login.html")
@app.route('/dashboard')
#@login_required
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    else:
        id = session["user_id"]
        user = Signup.query.filter_by(id=id).first()
        #donations = Donatebook.query.all()  # Fetch data from the database
        # Fetch current user donations
        donations = Donation.query.filter_by(user_id=current_user.id).all()

        # Calculate total donation count
        total_donations = len(donations)

        # Group by campaign if needed or just pass
        campaigns = Campaign.query.all()  # assuming campaigns exist
        return render_template('dashboard.html', donation=donations,user=user,campaigns=campaigns,donation_count=total_donations)

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
        remove_expired_medicines()
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
        user = current_user
        # Check for prohibited drugs
        if any(drug.lower() in name.lower() for drug in prohibited_drugs):
              return "Donation rejected. This medicine is prohibited for donation.", 400
 
       # Convert the string to a datetime.date object
        try:
            exdate_obj = datetime.strptime(exdate, "%Y-%m-%d").date()
            mfgdate_obj = datetime.strptime(mfgdate, "%Y-%m-%d").date()


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
        user.donation_count += 1
        db.session.commit()
        new_donation = Donation(user_id=current_user.id,item='medition',campaign='medition donation',date=datetime.utcnow())
        db.session.add(new_donation)
        db.session.commit()
        return "Data submitted successfully"

    return render_template("donationformedi.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact",methods=["GET", "POST"])
def contact():
    if 'user_id' not in session:
        flash("Please log in to donate.")
        return redirect(url_for('login'))

    if request.method == "POST":
        name=request.form['name']
        email=request.form['email']
        whatsapp=request.form['whatsapp']
        subject=request.form['subject']
        msg=request.form['message']
        contact = Contact(name=name,email=email,phone_num=whatsapp,subject=subject,massage=msg)
        db.session.add(contact)
        db.session.commit()
        return "Massage send successfully"
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
        user = current_user
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
        user.donation_count += 1
        db.session.commit()
        new_donation = Donation(user_id=current_user.id,item='cloth',campaign="help with cloth",date=datetime.utcnow())
        db.session.add(new_donation)
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
        user = current_user
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
        user.donation_count += 1
        db.session.commit()

        new_donation = Donation(user_id=current_user.id,item='book',campaign="donate education",date=datetime.utcnow())
        db.session.add(new_donation)
        db.session.commit()
        return "Data submitted successfully"

    return render_template("donatebook.html")
@app.route("/generate_certificate", methods=["GET"])
def generate_certificate():
    user = Signup.query.get(session['user_id'])

    milestones = [10, 50, 100, 200, 300]
    achieved = next((m for m in reversed(milestones) if user.donation_count >= m), None)

    if not achieved:
        return jsonify({'status': 'error', 'message': f'You have only donated {user.donation_count} items. Minimum 10 required to generate certificate.'})
    user_name = request.args.get("name", "User")
    milestone = request.args.get("milestone", "10")  # Default milestone

    # Ensure the certificates directory exists
    if not os.path.exists("certificates"):
        os.makedirs("certificates")
        # PDF file path
    pdf_path = f"certificates/{user_name}_certificate.pdf"

    # Create a PDF
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Set Background Color (White)
    c.setFillColor(black)
# Certificate Heading
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height - 100, "CERTIFICATE")

    # Slogan
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 130, "Of Achievement")

    # User Name
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(blue)
    c.drawCentredString(width / 2, height - 200, user_name)

    # Certificate Body Text
    c.setFillColor(black)
    c.setFont("Helvetica", 14)
    text = f"Mr./Mrs. {user_name} has successfully completed {milestone} donations."
    c.drawCentredString(width / 2, height - 250, text)
    c.drawCentredString(width / 2, height - 270, "Their loyalty helps someone in need.")
    c.drawCentredString(width / 2, height - 290, "Thank you for your generosity!")
# Load and Draw Logo
    try:
        logo = Image.open(LOGO_PATH)
        c.drawInlineImage(LOGO_PATH, 50, height - 100, width=120, height=50)
    except Exception as e:
        print(f"Logo not found: {e}")

    # Load and Draw Signatures
    try:
        c.drawInlineImage(SONU_SIGNATURE, 100, 80, width=100, height=50)
        c.drawInlineImage(SANDEEP_SIGNATURE, width / 2 - 50, 80, width=100, height=50)
        c.drawInlineImage(SAMEER_SIGNATURE, width - 200, 80, width=100, height=50)
    except Exception as e:
        print(f"Error loading signatures: {e}")

    # Signature Names
    c.setFont("Helvetica-Bold", 12)
    c.drawString(110, 60, "Sonu Sharma")
    c.drawString(width / 2 - 40, 60, "Sandeep Yadav")
    c.drawString(width - 190, 60, "Mohammed Sameer")
# Save the PDF
    c.save()

    return send_file(pdf_path, as_attachment=True)
@app.route("/logout")
def logout():
     session.pop('user_id')
     session.pop('user_name')
     return redirect("/")
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "POST":
        email =request.form['email'] 
        password = request.form['password']
        if email == 'admin@gmail.com' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('adminlogin.html')
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin_login'))
@app.route('/admin/dashboard?#campaigns' , methods=['GET', 'POST'])
def campaign():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if request.method == "POST":
        name = request.form["name"]
        desc = request.form["desc"]
        date = request.form["date"]
        mdate = datetime.strptime(date, "%Y-%m-%d").date()
        camp = Campaign(name=name,desc=desc,date=mdate)
        db.session.add(camp)
        db.session.commit()
        return "campaign add seccuessfully"
@app.route('/admin/dashboard',methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if request.method == "POST":
        name = request.form["name"]
        desc = request.form["desc"]
        date = request.form["date"]
        mdate = datetime.strptime(date, "%Y-%m-%d").date()
        camp = Campaign(name=name,desc=desc,date=mdate)
        db.session.add(camp)
        db.session.commit()
        return "campaign add seccuessfully"
    users = Signup.query.all()
    books = Donatebook.query.all()
    meds = Donatemed.query.all()
    clothes = Donatecloth.query.all()
    campaigns = Campaign.query.all()
    donations = Donation.query.all()
    countcontact = db.session.query(Contact).count()
    count_book_donation = db.session.query(Donatebook).count()
    count_med_donation = db.session.query(Donatemed).count()
    count_cloth_donation = db.session.query(Donatecloth).count()
    totaldonation = count_book_donation + count_med_donation + count_cloth_donation
    totalcampaign = db.session.query(Campaign).count()
    contact = Contact.query.all()
    return render_template('admin_dashboard.html',msg=contact,totalcampaign=totalcampaign,totaldonation=totaldonation,countcontact=countcontact, users=users, books=books, meds=meds, clothes=clothes,campaigns=campaigns,donations=donations)
@app.route('/admin/delete_user/<int:user_id>')
def delete_user(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    user = Signup.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_donation/<string:table>/<int:donation_id>')
def delete_donation(table, donation_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    table_map = {
        'book': Donatebook,
        'medicine': Donatemed,
        'cloth': Donatecloth
    }

    model = table_map.get(table)
    if not model:
        return 'Invalid table', 400

    donation = model.query.get_or_404(donation_id)
    db.session.delete(donation)
    db.session.commit()
    flash('Donation deleted', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=4444)


