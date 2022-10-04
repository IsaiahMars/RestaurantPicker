# This file is used to create the routes associated with user accounts
# The code used in our login, sign-up, and logout routes is roughly based on code provided by
# a Youtube Channel named 'Tech With Tim', link provided here: https://www.youtube.com/watch?v=dam0GPOAvVI

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])                                  # Creating the url route for our login page and passing the methods used to access our database. 
def login():                                                     
    if request.method == 'POST':
        email = request.form.get('email')                                       # Gathering the data entered into the login form.
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()                        # Querying our User table to check if an account with this email exists within our database.

        if user:
            if check_password_hash(user.password, password):                    # Hashing the password entered and checking it against the hashed password stored within our database.
                flash('Logged in successfully!', category='success')
                login_user(user, remember=False)                                # Once authentication is successfull, flashes a message and redirects to homepage.
                return redirect(url_for("views.home"))
            else:
                flash('Check your password and try again.', category='error')   
        else:
            flash('Account with this email does not exist', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/sign-up', methods=['GET', 'POST'])                                    # Creating the url route for our sign-up page and passing the methods used to access our database.
def signUp():
    if request.method == 'POST':
        email = request.form.get('email')                                           # Gathering the data entered into the login form.
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()                            # Querying our User table to check if an account with this email already exists within our database.

        if user: 
            flash('An account with this email already exists!', category='error')   # Series of conditionals used to make sure the columns within our database can store the data entered by a user.
        elif len(email) < 9: 
            flash('Email must be longer than 8 characters.', category='error')
        elif len(email) > 49:
            flash('Email must be less than 50 characters.', category='error')
        elif len(username) < 4:
            flash('Username must be longer than 3 characters', category='error')
        elif len(username) > 19:
            flash('Username must be less than 20 characters long.', category='error')
        elif password1 != password2:                                               
            flash('Passwords do not match!', category='error')
        elif len(password1) < 8:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method="sha256"))  
            db.session.add(new_user)
            db.session.commit()                                                     # Creating a new object within our database, storing a user's password as its hashed value for security.

            flash('Account created!', category="success")
            return redirect(url_for("views.home"))                                  # Flashing a message and redirecting to homepage upon successful account creation.



    return render_template("sign-up.html", user=current_user)

        

@auth.route('/account-settings')
def account():
    return render_template("account.html")

@auth.route('/logout')
def logout():
    flash('Logged out successfully!', category='success')
    logout_user()                                                                    # Logging out the current user, flashing a message, and redirecting to login page.
    return redirect(url_for("auth.login"))


