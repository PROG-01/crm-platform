import os

from cs50 import SQL
from flask import Flask, render_template, request, redirect
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///crm.db")

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
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

        return redirect ('/dashboard.html')

    else:
        return render_template('register.html')