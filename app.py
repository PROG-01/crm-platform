import os

from cs50 import SQL
from flask import Flask, render_template, request

app = Flask(__name__)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///crm.db")

@app.route('/')
def index():
    return render_template('landing.html')