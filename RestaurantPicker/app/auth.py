# This file is used to create the routes associated with user accounts
# The code used in our login, sign-up, and logout routes is roughly based on code provided by
# a Youtube Channel named 'Tech With Tim', link provided here: https://www.youtube.com/watch?v=dam0GPOAvVI
# https://stackoverflow.com/questions/59944361/retrieval-and-display-from-azure-blob-storage-to-flask-python-to-html-js <- very nice man who provided SAS token generator

import os
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from azure.storage.blob import BlobServiceClient
from .models import User
from . import db

auth = Blueprint('auth', __name__)


blob_service = BlobServiceClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=restaurantpicker;AccountKey=BHyo+0c75/6uLVNF0WvqsKbtu/g07bSpw6VIdrG1WgMcJHNiw6PGlOKiSVCavKzi6Z44jMr/og8w+ASt/F8mkg==;EndpointSuffix=core.windows.net")

try:
    container_client = blob_service.get_container_client(container="user-images")  # Connecting to Azure Blob Storage and accessing the container used to store user images
    container_client.get_container_properties()                                    # NOT ORIGINALLY OUR CODE - This code was provided by a YouTube channel named Thomas Gauvin
except Exception as e:                                                             # during a video in which he displays how to use Azure Blob Storage with a Flask app.
    container_client = blob_service.create_container("user-images")                # https://www.youtube.com/watch?v=wToHU8Hts9c


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
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method="sha256"), bio="None.", userImage="default", primaryColor="#8a111f", secondaryColor="#7d7d7d")  
            db.session.add(new_user)
            db.session.commit()                                                     # Creating a new object within our database, storing a user's password as its hashed value for security.

            flash('Account created!', category="success")
            login_user(new_user, remember=False)
            return redirect(url_for("views.home"))                                  # Flashing a message, logging in the user, redirecting to homepage upon successful account creation.

    return render_template("sign-up.html", user=current_user)

        

@auth.route('/account-settings', methods=["GET", "POST"])
@login_required
def account():
    if request.method == 'POST':
        if 'update-profile-picture' in request.form:                                        # If statements to check which form was submitted.  
            file = request.files['user-image']                                              # Checking to see if a file was provided, then checking to see if   
            if 'user-image' not in request.files:                                           # the file type is support by html <img> tags.
                flash('No file selected to upload!', category='error')                      
            if allowed_file(file.filename) == False:
                flash('Uploaded files must be .png, .jpg, .jpeg, .svg, or .gif!')
            else: 
                user = User.query.filter_by(id=current_user.id).first()                     # Creating a temporary object used to store the file name of the old image,
                tempImg = user.userImage                                                    # encrypting the file name of the new image and storing it as an attribute of the user,
                user.userImage = generate_password_hash(file.filename, method="sha256")     # then using the temporary object to remove the old image from Azure Blob Storage 
                db.session.commit()                                                         # before uploading the new image.

                container_client.upload_blob(user.userImage, file)
                if(tempImg != 'default'):
                    container_client.delete_blob(blob=tempImg)

                flash('Profile picture updated successfully!', category='success')
                return render_template("account.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))

        if 'update-email' in request.form:
            newEmail = request.form.get('email')

            user = User.query.filter_by(email=newEmail).first()                                     # Retrieving the email entered into the form, checking to see
                                                                                                    # if the new email is acceptable, and then changing the current user's
            if(newEmail == current_user.email):                                                     # email and committing the change to the database.
                flash('The email provided matches your current email.', category='error')
            if user:
                flash('An account with this email already exists!', category='error')
            elif len(newEmail) < 9: 
                flash('Email must be longer than 8 characters.', category='error')
            elif len(newEmail) > 49:
                flash('Email must be less than 50 characters.', category='error')
            else:
                user = User.query.filter_by(id=current_user.id).first()
                user.email = newEmail
                db.session.commit()
    
                flash('Email updated successfully!', category='success')
                return render_template("account.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))

        if 'update-username' in request.form:
            newUsername = request.form.get('username')

            if len(newUsername) < 4:                                                                    # Retrieving the username entered into the form, checking to see
                flash('Username must be longer than 3 characters', category='error')                    # if the new username is acceptable, and then changing the current user's
            elif len(newUsername) > 19:                                                                 # username and committing the change to the database.
                flash('Username must be less than 20 characters long.', category='error')
            else:
                user = User.query.filter_by(id=current_user.id).first()
                user.username = newUsername
                db.session.commit()
    
                flash('Username updated successfully!', category='success')
                return render_template("account.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))
            
        if 'update-password' in request.form:
            newPassword1 = request.form.get('new-password1')
            newPassword2 = request.form.get('new-password2')
            currentPassword = request.form.get('current-password')

            if newPassword1 != newPassword2:                                               
                flash('Passwords do not match!', category='error')
            elif newPassword1 == currentPassword:
                flash('New password matches current password!', category='error')
            elif len(newPassword1) < 8:
                flash('Password must be at least 7 characters.', category='error')
            elif not check_password_hash(current_user.password, currentPassword):
                flash("'Current' password entered does not match current password!", category='error')
            else:
                user = User.query.filter_by(id=current_user.id).first()
                user.password = generate_password_hash(newPassword1, method="sha256")
                db.session.commit()

                flash('Password updated successfully!', category='success')
                return render_template("account.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))

        if 'update-theme' in request.form:
            primaryColor = request.form.get('primary-color')    
            secondaryColor = request.form.get('secondary-color')                # Retrieving the primary and secondary color entered into the form,
                                                                                # changing the current user's respective attributes, and then committing
            user = User.query.filter_by(id=current_user.id).first()             # the change to the database.            
            user.primaryColor = primaryColor
            user.secondaryColor = secondaryColor
            db.session.commit()
    
            flash('Theme updated successfully!', category='success')
            return render_template("account.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))

    return render_template("account.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))

@auth.route('/logout')
@login_required
def logout():
    flash('Logged out successfully!', category='success')
    logout_user()                                                                    # Logging out the current user, flashing a message, and redirecting to login page.
    return redirect(url_for("auth.login"))


###################################
# This function is a URL token generator with SAS. This function creates the URL of our stored images to be accessed by our HTML and used in our project. 
# NOT ORIGINALLY OUR CODE - This code was provided by a very nice man by the name of 'Peter Pan' on Stack Overflow, link provided below:
# https://stackoverflow.com/questions/59944361/retrieval-and-display-from-azure-blob-storage-to-flask-python-to-html-js
from datetime import datetime, timedelta
from azure.storage.blob import generate_container_sas, ContainerSasPermissions

account_name = "restaurantpicker"
account_key = "BHyo+0c75/6uLVNF0WvqsKbtu/g07bSpw6VIdrG1WgMcJHNiw6PGlOKiSVCavKzi6Z44jMr/og8w+ASt/F8mkg==;EndpointSuffix=core.windows.net"
container_name = "user-images"

from azure.storage.blob import generate_blob_sas, BlobSasPermissions

# using generate_blob_sas                                                                                       
def get_img_url_with_blob_sas_token(blob_name):
    blob_sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_name,
        account_key=account_key,
        permission=ContainerSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    blob_url_with_blob_sas_token = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}?{blob_sas_token}"
    return blob_url_with_blob_sas_token

#############################################

allowedExtensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg')            # Creating a basic function that checks the file extension of upload images.
                                                                         # https://www.geeksforgeeks.org/how-to-get-file-extension-in-python/
def allowed_file(filename):
    split_tup = os.path.splitext(filename)
    file_extension = split_tup[1].lower()
    print(file_extension)

    if file_extension in allowedExtensions:
        return True
    else:
        return False

#############################################
