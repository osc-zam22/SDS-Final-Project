from flask import Flask, request, redirect, render_template, session , url_for
from flask_pymongo import PyMongo
import pymongo
from bson.objectid import ObjectId
import secrets
import bcrypt
import random

#Initialize application
app = Flask(__name__)

#Connecting to Marverse database
app.config['MONGO_DBNAME'] = 'Marverse'
app.config['MONGO_URI'] = "mongodb+srv://admin:sY6xkooh42p1oyK1@cluster0.uhnly.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

#Initializing pymongo
mongo = PyMongo(app)
client = pymongo.MongoClient("mongodb+srv://admin:sY6xkooh42p1oyK1@cluster0.uhnly.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

#Initializing database
db = client.Marverse

#Setting secret key
app.secret_key = secrets.token_urlsafe(17)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/directory')
def directory():
    return render_template('directory.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/thread')
def thread():
    return render_template('thread.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/logout')
def logout():
    return render_template('index.html')