import os

from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///crm.db")

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate form data
        if not name or not email or not password or not confirm_password:
            return render_template('register.html', error='Please fill in all fields')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        # Handle duplicate email
        if db.execute("SELECT * FROM users WHERE email = ?", email):
            return render_template('register.html', error='Email already registered')

        # Hash password
        password_hash = generate_password_hash(password)

        # Insert data into users table
        db.execute("INSERT INTO users (name, email, hash) VALUES (?, ?, ?)", name, email, password_hash)

        return redirect ('/')

    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])    
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        # Validate form data
        if not email or not password:
            return render_template('login.html', error='Please fill in all fields')

        # Check if user exists
        user = db.execute("SELECT * FROM users WHERE email = ?", email)
        if not user:
            return render_template('login.html', error='Invalid email or password')

        # Verify password
        if not check_password_hash(user[0]['hash'], password):
            return render_template('login.html', error='Invalid email or password')

        # Clear any existing session
        session.clear()

        # Store user ID session
        session['user_id'] = user[0]['id']

        # Redirect to dashboard
        return redirect('/dashboard')

    else:
        return render_template('login.html')

    