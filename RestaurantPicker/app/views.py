# This file will be used to create our other routes (randomizer page, map page, etc...)
import requests, json
from flask import Blueprint, render_template, request
from flask_login import current_user, login_required
from .auth import get_img_url_with_blob_sas_token
from .models import Preferences
from . import db, simple_geoip

views = Blueprint('views', __name__)

# Definining the API Key, Search Type, and Header
MY_API_KEY = 'YELP API KEY'
BUSINESS_SEARCH = 'https://api.yelp.com/v3/businesses/search'
BUSINESS_DETAILS = 'https://api.yelp.com/v3/businesses/'
HEADERS = {'Authorization': 'bearer %s' % MY_API_KEY}

@views.route('/', methods=["GET","POST"])
def home():
    if current_user.is_authenticated:                                       # Checking to see if the current user is authenticated to determine whether or not to display 'liked' restaurants.                           
        #geoip_data = simple_geoip.get_geoip_data('173.59.215.59')          # Here, the API request to GeoIPify is commented out in order to save the limited number of requests that come with the free trial.
        geoip_data = {'location':{'city':'Plattsburgh'}}                    # Additionally, the IP '173.59.215.59' is passed due to the fact that this project is still being locally hosted and remote_addr cannot be retrieved.
        PARAMETERS = {'location':geoip_data['location']['city'],            
            'radius':2500,
            'limit':10,
            'sort_by': 'rating',
            'term':'restaurant'
            }
        response = requests.get(url=BUSINESS_SEARCH,                        # These are get requests used to retrieve 'trending' and 'all nearby'/'top 50 nearby' businesses from the YelpAPI's 'Business Search' endpoint.
                                params=PARAMETERS,                          # This code is roughly based on a Python YelpAPI tutorial provided here: https://www.youtube.com/watch?v=oggMBtza80E
                                headers=HEADERS)                            # In the tutorial, you will find that this professor's tutorial is based on a different YouTuber's code, so I will also link
        parsed = json.loads(response.text)                                  # their repository here: https://github.com/areed1192/sigma_coding_youtube/blob/master/python/python-api/yelp-api/Yelp%20API%20-%20Other%20Search%20%26%20Categories.py
        trendingBusinesses = parsed["businesses"]

        PARAMETERS = {'location':geoip_data['location']['city'], 
            'radius':2500,
            'limit': 50,
            'term':'restaurant'
            }
        response = requests.get(url=BUSINESS_SEARCH, 
                                params=PARAMETERS, 
                                headers=HEADERS)
        parsed = json.loads(response.text)
        allBusinesses = parsed["businesses"]
        likedRestaurants = Preferences.query.filter_by(user_id=current_user.id, likes=True).all()   # Simple SQLAlchemy query used to retrieve all of the current user's 'liked' restaurants.
        return render_template("home.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), trendingBusinesses=trendingBusinesses, allBusinesses=allBusinesses, likedRestaurants=likedRestaurants, location=geoip_data['location']['city'])

    else:
        #geoip_data = simple_geoip.get_geoip_data('137.142.211.54')  #temp user location
        geoip_data = {'location':{'city':'Plattsburgh'}}
        PARAMETERS = {'location':geoip_data['location']['city'],   
              'radius':2500,
              'limit':10,
              'sort_by': 'rating',
              'term':'restaurant'
            }
        response = requests.get(url=BUSINESS_SEARCH, 
                                params=PARAMETERS, 
                                headers=HEADERS)
        parsed = json.loads(response.text)
        trendingBusinesses = parsed["businesses"]

        PARAMETERS = {'location':geoip_data['location']['city'],    #temp user location
              'radius':2500,
              'limit': 50,
              'term':'restaurant'
            }
        response = requests.get(url=BUSINESS_SEARCH, 
                                params=PARAMETERS, 
                                headers=HEADERS)
        parsed = json.loads(response.text)
        allBusinesses = parsed["businesses"]
        return render_template("home.html", user=current_user, trendingBusinesses=trendingBusinesses, allBusinesses=allBusinesses, location=geoip_data['location']['city'])

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