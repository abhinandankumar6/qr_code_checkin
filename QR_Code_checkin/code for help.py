import os
import pandas as pd
import qrcode
import random
import string
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
mail = Mail(app)

# Paths
CSV_FILE = 'data/users.csv'
QR_CODE_DIR = 'static/qrcodes'

# Ensure directories exist
os.makedirs(QR_CODE_DIR, exist_ok=True)

# Generate random 11-digit alphanumeric code
def generate_unique_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(11))

# Read CSV and generate unique codes
def process_csv():
    df = pd.read_csv(CSV_FILE)
    if 'unique_code' not in df.columns:
        df['unique_code'] = [generate_unique_code() for _ in range(len(df))]
        df.to_csv(CSV_FILE, index=False)
    return df

# Generate QR codes
def generate_qr_codes(df):
    for _, row in df.iterrows():
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(row['unique_code'])
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save(f"{QR_CODE_DIR}/{row['unique_code']}.png")

# Send emails with QR codes
def send_emails(df):
    for _, row in df.iterrows():
        msg = Message('Your QR Code', sender='your_email@gmail.com', recipients=[row['email']])
        msg.body = f"Hello {row['name']}, your unique QR code is attached."
        with app.open_resource(f"{QR_CODE_DIR}/{row['unique_code']}.png") as qr:
            msg.attach(f"{row['unique_code']}.png", "image/png", qr.read())
        mail.send(msg)

# Track scan counts
scan_counts = {}

# Home page with scanner
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        unique_code = request.form.get('unique_code')
        if unique_code in scan_counts:
            if scan_counts[unique_code] < 2:
                scan_counts[unique_code] += 1
                return redirect(url_for('welcome'))
            else:
                return "Max attempts reached."
        else:
            scan_counts[unique_code] = 1
            return redirect(url_for('welcome'))
    return render_template('home.html')

# Welcome page
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# Summary page
@app.route('/summary')
def summary():
    df = pd.read_csv(CSV_FILE)
    scanned = sum(1 for code in df['unique_code'] if scan_counts.get(code, 0) > 0)
    left = len(df) - scanned
    return render_template('summary.html', scanned=scanned, left=left)

# Register new user
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    emp_id = StringField('Employee ID', validators=[DataRequired()])
    master_code = PasswordField('Master Code', validators=[DataRequired()])
    submit = SubmitField('Register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        df = pd.read_csv(CSV_FILE)
        new_user = pd.DataFrame([{
            'name': form.name.data,
            'email': form.email.data,
            'emp_id': form.emp_id.data,
            'unique_code': generate_unique_code(),
            'email_status': 'pending',
            'checkin_status': 'pending',
            'count': 'pending'
        }])
        df = pd.concat([df, new_user], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        generate_qr_codes(new_user)
        #send_emails(new_user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
    df = process_csv()
    generate_qr_codes(df)
    #send_emails(df)
    app.run(debug=True)