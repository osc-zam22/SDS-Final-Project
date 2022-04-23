from flask import Flask, request, redirect, render_template, session , url_for
from flask_pymongo import PyMongo
import pymongo
from bson.objectid import ObjectId
import secrets
import bcrypt
import random
import os

#Initialize application
app = Flask(__name__)

#Connecting to Marverse database
app.config['MONGO_DBNAME'] = 'Marverse'
# app.config['MONGO_URI'] = "mongodb+srv://admin:sY6xkooh42p1oyK1@cluster0.uhnly.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

#Initializing pymongo
mongo = PyMongo(app)
# client = pymongo.MongoClient("mongodb+srv://admin:sY6xkooh42p1oyK1@cluster0.uhnly.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
client = pymongo.MongoClient(os.environ.get('MONGO_URI'))
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

@app.route('/sub_directory/<film>')
def sub_directory(film):
    if film == '0':
        contents = db.Films.find()
        return render_template('sub-directory.html' , contents = contents , category=0)
    elif film == '1':
        contents = db.Shows.find()
        return render_template('sub-directory.html' , contents= contents, category=1)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = db.Users

        user_email = users.find_one({"Email": request.form["Email/Username"]})
        user_username = users.find_one({"Username": request.form["Email/Username"]})
        user = None

        #if user with email exists
        if user_username or user_email:
            if user_email:
                user = user_email
            elif user_username:
                user = user_username

            #Gets actual password tied to user
            actual_password = user['Password']
            #encodes attempted password
            attempted_password = request.form['Password'].encode("utf-8")

            if bcrypt.checkpw(attempted_password, actual_password):
                #store in session
                user_email = user['Email']
                session['Email'] = user_email
                return redirect(url_for('index'))
            else:
                return render_template('login.html', prompt = "Invalid password... try again.")
        
        else:
            return render_template('login.html', prompt = "User not found... try again.")
    else:
        return render_template('login.html')


@app.route('/signup' , methods = ['GET' , 'POST'])
def sign_up():
    if request.method == 'POST':
        users = db.Users

        existing_user = users.find_one({"Email": request.form['Email']})

        if not existing_user:
            username = request.form['Username']
            email = request.form['Email']
            
            #encrypting password
            password = request.form['Password'].encode("utf-8")

            #Makes sure all fields were filled in
            if not username or not email or not password:
                return render_template("signup.html", prompt = "Invalid sign up. Make sure to fill in every field.")
            #hashing password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password, salt)

            #adding to users database
            users.insert_one({'Username': username, 'Email': email, 'Password': hashed_password , 'Posts' : []})

            #creating new session
            session['Email'] = request.form['Email']

            return redirect(url_for('index'))

        else:
            return render_template("signup.html", prompt = "username is already registered... try logging in.")
    else:
        return render_template("signup.html")
    


@app.route('/thread/<title>/<episode>')
@app.route('/thread/<title>')
@app.route('/thread/<postId>')
def thread(title=None , episode=None , postId=None):
    posts = None
    
    if title and episode:
        posts = db.shows.find({'Title' : title , 'Episode' : episode})
    elif title and not episode:
        posts = db.Film.find({'Title' : title })
    else:
        posts = db.Posts.find({'_id' : postId })
    return render_template('thread.html' , posts=posts , title=title , postId=postId)

@app.route('/profile')
def profile():
    if not session:
        return redirect(url_for('index'))
    profile = db.Users.find_one({'Email' : session['Email']})
  
    return render_template('profile.html' , profile = profile)

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')


