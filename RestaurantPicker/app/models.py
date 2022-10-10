# This file is used to define the tables (as well as their relationships) used within our database.
from . import db
from flask_login import UserMixin



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256))
    bio = db.Column(db.String(150))
    userImage = db.Column(db.String(256))
    primaryColor = db.Column(db.String(10))
    secondaryColor = db.Column(db.String(10))
    
    


