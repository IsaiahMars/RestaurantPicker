# This file is used to define the tables (as well as their relationships) used within our database.
from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256))
    userImage = db.Column(db.String(256))
    primaryColor = db.Column(db.String(10))
    secondaryColor = db.Column(db.String(10))
    tokens = db.relationship('Token')
    preferences = db.relationship('Preferences')
    reviews = db.relationship('Reviews')
    recentlyviewed = db.relationship('RecentlyViewed')
    questionnaireresponse = db.relationship('QuestionnaireResponse')

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    token = db.Column(db.String(256), unique=True)
    email = db.Column(db.String(50))
    time_created = db.Column(db.DateTime(timezone=True))

class Preferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    business_id = db.Column(db.String(30))
    business_name = db.Column(db.String(50))
    business_image_url = db.Column(db.String(100))
    business_rating = db.Column(db.Float)
    business_rating_count = db.Column(db.Integer)
    likes = db.Column(db.Boolean)
    dislikes = db.Column(db.Boolean)


class Reviews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    business_id = db.Column(db.String(30))
    business_name = db.Column(db.String(50))
    business_image_url = db.Column(db.String(100))
    username = db.Column(db.String(20))
    text = db.Column(db.String(120))
    date_visited = db.Column(db.String(11))
    rating = db.Column(db.Float)
    flags = db.Column(db.Integer)

class RecentlyViewed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    business_id = db.Column(db.String(30))
    business_name = db.Column(db.String(50))
    business_image_url = db.Column(db.String(100))
    business_rating = db.Column(db.Float)
    business_rating_count = db.Column(db.Integer)
class QuestionnaireResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    response_type = db.Column(db.String(30))
    responses = db.Column(db.Text(1000))

    
    