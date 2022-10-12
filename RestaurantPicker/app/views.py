# This file will be used to create our other routes (randomizer page, map page, etc...)
from flask import Blueprint, render_template
from flask_login import current_user, login_required, UserMixin
from .auth import get_img_url_with_blob_sas_token


views = Blueprint('views', __name__)

@views.route('/')
def home():
    if current_user.is_authenticated:
        return render_template("home.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))
    else:
        return render_template("home.html", user=current_user)

@views.route('/locations')
def locations():
    if current_user.is_authenticated:
        return render_template("locations.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))
    else:
        return render_template("locations.html", user=current_user)

@views.route('/questionnaire')
@login_required
def questionnaire():
    return render_template("questionnaire.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))

@views.route('/randomizer')
@login_required
def randomizer():
    return render_template("randomizer.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))

@views.route('/restaurant')
def restaurant():
    if current_user.is_authenticated:
        return render_template("restaurant.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))
    else:
        return render_template("restaurant.html", user=current_user)

@views.route('/recently-viewed')
@login_required
def recentlyViewed():
    return render_template("recently-viewed.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))

@views.route('/my-reviews')
@login_required
def myReviews():
    return render_template("my-reviews.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))