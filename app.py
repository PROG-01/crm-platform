import os

from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

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

@app.route('/dashboard')
@login_required
def dashboard():

    name_rows = db.execute("SELECT name FROM users WHERE id = ?", session['user_id'])
    name = name_rows[0]['name']

    client_rows = db.execute("SELECT COUNT(*) AS client_count FROM clients WHERE user_id = ?", session['user_id'])
    client_count = client_rows[0]['client_count']

    return render_template('dashboard.html', name=name, client_count=client_count)

@app.route('/logout')
@login_required
def logout():
    # Clear session
    session.clear()

    # Redirect to login page
    return redirect('/')


@app.route('/clients')
@login_required
def clients():
    # Fetch clients for the logged-in user
    clients = db.execute("SELECT * FROM clients WHERE user_id = ?", session['user_id'])

    return render_template('clients/index.html', clients=clients)

@app.route('/clients/new', methods=['GET', 'POST'])
@login_required
def new_client():
    if request.method == 'POST':

        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()

        # Validate form data
        if not name:
            return render_template('clients/create.html', error='Please fill the required field')

        # Insert new client into the database
        db.execute("INSERT INTO clients (user_id, name, email, phone) VALUES (?, ?, ?, ?)", session['user_id'], name, email, phone)

        return redirect('/clients')
    else: 
        return render_template('clients/create.html')


@app.route('/clients/<int:id>')
@login_required
def view_client(id):
    # Fetch client details for the logged-in user
    client = db.execute("SELECT * FROM clients WHERE id = ? AND user_id = ?", id, session['user_id'])

    if not client:
        return redirect('/clients')

    return render_template('clients/details.html', client=client[0])    

@app.route('/clients/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(id):
    # Fetch client details for the logged-in user
    client = db.execute("SELECT * FROM clients WHERE id = ? AND user_id = ?", id, session['user_id'])

    if not client:
        return redirect('/clients')

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()

        # Validate form data
        if not name:
            return render_template('clients/edit.html', client=client[0], error='Please fill the required field')

        # Update client details in the database
        db.execute("UPDATE clients SET name = ?, email = ?, phone = ? WHERE id = ? AND user_id = ?", name, email, phone, id, session['user_id'])

        return redirect(f'/clients/{id}')

    else:
        return render_template('clients/edit.html', client=client[0])

@app.route('/clients/<int:id>/delete', methods=['POST'])
@login_required
def delete_client(id):

    # Delete client for the logged-in user

    db.execute("DELETE FROM clients WHERE id = ? AND user_id = ?", id, session['user_id'])
    return redirect('/clients')

@app.route('/projects')
@login_required
def projects():
    # Fetch projects for the logged-in user
    projects = db.execute("SELECT projects.name AS project_name, clients.name AS client_name, projects.status, projects.due_date FROM projects JOIN clients ON projects.client_id = clients.id WHERE projects.user_id = ?", session['user_id'])

    return render_template('projects/index.html', projects=projects)