# This file will be used to create our other routes (randomizer page, map page, etc...)
from flask import Blueprint, render_template
from flask_login import current_user, UserMixin
from .auth import get_img_url_with_blob_sas_token


views = Blueprint('views', __name__)

@views.route('/')
def home():
    if current_user.is_authenticated:
        return render_template("home.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))
    else:
        return render_template("home.html", user=current_user)

