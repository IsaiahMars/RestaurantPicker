# This file will be used to create our other routes (randomizer page, map page, etc...)
from flask import Blueprint, render_template
from flask_login import current_user

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html", user=current_user)

