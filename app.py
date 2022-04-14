from flask import Flask, request, redirect, render_template, session , url_for
from flask_pymongo import PyMongo
import pymongo
from bson.objectid import ObjectId
import secrets
import bcrypt
import random


app = Flask(__name__)



@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/directory')
def directory():
    return render_template('directory.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.hmtl')