from flask import Flask, request, redirect, render_template, session , url_for
from flask_pymongo import PyMongo
import pymongo
from bson.objectid import ObjectId
import secrets
import bcrypt
import random
import os
from model import increment_likes

#Initialize application
app = Flask(__name__)

#Connecting to Marverse database
app.config['MONGO_DBNAME'] = 'Marverse'
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

#Initializing pymongo
mongo = PyMongo(app)
client = pymongo.MongoClient(os.environ.get('MONGO_URI'))
#Initializing database
db = client.Marverse

#Setting secret key
app.secret_key = secrets.token_urlsafe(17)

'''
Route to / and /index
This is the landing page.
'''
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

'''
Route to /directory and /directory/<title>
Directory is used to load up and navigate movies, shows, and episodes.
The directory will determine what is loaded up by passing in the title.
Once the directory has been passed in with a specific movie/episode
it will redirect to the thread route for that specific title.
'''
@app.route('/directory')
@app.route('/directory/<title>')
def directory(title = None):
    if title:
        #Load directory with all shows
        if title == "Shows":
            shows = db.Shows.find({})
            return render_template('directory.html', contents = shows)

        #Load directory with all movies
        elif title == "Movies":
            movies = db.Films.find({})
            return render_template('directory.html', contents = movies)

        else:
            movie = db.Films.find_one({"Title": title})
            show = db.Shows.find_one({"Title": title})
            #Is movies and will redirect to thread
            if movie:
                return redirect(url_for('thread', title = title))
            #Is show and will load up directory with episodes
            elif show:
                return render_template('directory.html', contents = show)
            #Is episode and will redirect to thread
            else:
                show_episode_arr = title.split()
                show_episode_arr.insert(len(show_episode_arr) -1, "Episode")
                show_episode_str = " ".join(show_episode_arr)
                return redirect(url_for('thread', title = show_episode_str))
    #Render base directory
    else:
        return render_template('directory.html')

'''
Route to /thread/<title>
Displays thread for specific title.
Renders thread.html with posts.
'''
@app.route('/thread/<title>')
def thread(title = None):
    if title:
        #Searching for all posts with title
        posts = db.Posts.find({"Title": title})
        posts_length = 0
        posts_arr = []
        
        for post in posts:
            posts_arr.append(post)
            posts_length += 1

        #Returns all posts for title
        if posts_length != 0:
            return render_template('thread.html', posts = posts_arr, title = title)
        #Returns thread with no posts
        else:
            return render_template('thread.html', title = title)

    else:
        return redirect(url_for('index'))

'''
Route to /login
Takes in username/email and password from form.
Validates the username/email and password by checking with the mongodb Users database.
If successful a new session with user's email is initiated.
'''
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

'''
Route to /signup
Takes in username, email, and password from form.
Validates that it is a new user by checking with the mongodb Users database.
Encrypts password and adds new User to Users database.
If successful a new session with user's email is initiated.
'''
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

'''
Route to /profile
Finds profile by checking the User database with the session email.
Renders profile.html with the profile document.
'''
@app.route('/profile')
def profile():
    if not session:
        return redirect(url_for('index'))
    profile = db.Users.find_one({'Email' : session['Email']})
  
    return render_template('profile.html' , profile = profile)

'''
Route to /logout
Clears the session and renders index.html
'''
@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')

'''
Route /post_page/<title>
Renders post.html for title.
If not in session it will redirect to login-signup.html
'''
@app.route('/post_page/<title>')
def post_page(title):
    if session:
        return render_template('post.html', title = title)
    else:
        return render_template('login-signup.html')

'''
Route to /like/<postID>
Will find post based on postID and increment the like count by 1.
After incrementing like it will render thread again for the title of post.
If not in session it will redirect to login-signup.html
'''
@app.route('/like/<postID>')
def like(postID):
    if session:
        post = db.Posts.find_one({"_id": ObjectId(postID)})
        updated_likes = increment_likes(post["Likes"])

        db.Posts.update_one({"_id": ObjectId(postID)}, {"$set":{"Likes": updated_likes}})

        return redirect(url_for('thread', title = post['Title']))
    else:
        return render_template('login-signup.html')

'''
Route to /comment_page/<postID>
Will find post based on postID.
Renders comment.html with postID and post.
'''
@app.route('/comment_page/<postID>')
def comment_page(postID):
    post = db.Posts.find_one({"_id": ObjectId(postID)})
    return render_template('comment.html', postID = postID, post = post)

'''
Route to /post/<title>
Will get content from form and user based on session email.
Inserts post document into Posts database and Users database.
After successful post it will redirect to thread.html with title.
If not in session it will redirect to login-signup.html
'''
@app.route('/post/<title>',  methods = ['GET','POST'])
def post(title):
    if session:
        content = request.form["content"]
        user = db.Users.find_one({"Email": session["Email"]})
        
        #Inserts into Posts dabase and User's posts array
        db.Posts.insert_one({"Username": user["Username"], "Likes": 0, "Content": content, "Title": title, "Comments": []})
        db.Users.update_one({"Email": session["Email"]}, {"$push" : {"Posts" : {"Username": user["Username"], "Likes": 0, "Content": content, "Title": title, "Comments": []}}})
        return redirect(url_for('thread', title = title))

    else:
        return render_template('login-signup.html')

'''
Route to /comment/<postID>
Will get content from form and user based on session email.
Inserts comment document into post comments array.
After successful comment post it will redirect to thread.html with title.
'''
@app.route('/comment/<postID>', methods = ['GET', 'POST'])
def comment(postID):
    content = request.form['content']
    user = db.Users.find_one({"Email": session["Email"]})

    db.Posts.update_one({"_id": ObjectId(postID)}, {"$push" : {"Comments": {"Username": user["Username"], "Content": content}}})
    return redirect(url_for('comment_page', postID = postID))