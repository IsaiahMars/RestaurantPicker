# This file will be used to create our other routes (randomizer page, map page, etc...)
import json

import requests
from flask import Blueprint, flash, render_template, request
from flask_googlemaps import Map
from flask_login import current_user, login_required

from . import db, simple_geoip
from .auth import get_img_url_with_blob_sas_token
from .models import Preferences, RecentlyViewed, Reviews

views = Blueprint('views', __name__)

# Definining the API Key, Search Type, and Header
MY_API_KEY = 'POsgwBET3VXFgJA6YXuddB_zNXaHKTY-qwxAU4v0xUfMaS6vL1BaOdfJbrEJ9LFNNjmoJ15fLdJ2UjPXmt98Pa7tHOwkXmZLPUiBjjpX9RfVeESy8Hl4XT5-4NokY3Yx'
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
        likedRestaurants = Preferences.query.filter_by(user_id=current_user.id, likes=True).order_by(Preferences.id.desc()).all()    # Simple SQLAlchemy query used to retrieve all of the current user's 'liked' restaurants.
        return render_template("home.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), trendingBusinesses=trendingBusinesses, allBusinesses=allBusinesses, likedRestaurants=likedRestaurants, location=geoip_data['location']['city'])

    else:
        #geoip_data = simple_geoip.get_geoip_data('137.142.211.54') 
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

@views.route('/restaurant/<businessId>', methods=["GET", "POST"]) # Parametrized URL's explained here: https://stackoverflow.com/questions/24892035/how-can-i-get-the-named-parameters-from-a-url-using-flask
def restaurant(businessId):
    if current_user.is_authenticated:
        PARAMETERS = {}                                                     # This is a different type of YelpAPI request which uses the 'Business Details' endpoint in order to retrieve data 
        response = requests.get(url=BUSINESS_DETAILS + businessId,          # about a restaurant when the restaurant's anchor tag is clicked on from the home page.
                                params=PARAMETERS, 
                                headers=HEADERS)
        parsed = json.loads(response.text)
        ###########
        newRV = RecentlyViewed(user_id=current_user.id, business_id=businessId, business_name=parsed["name"], business_image_url=parsed["image_url"], business_rating=parsed["rating"], business_rating_count=parsed["review_count"])
        queryRV = RecentlyViewed.query.filter_by(user_id=current_user.id, business_id=businessId).first()
        allRV = RecentlyViewed.query.filter_by(user_id=current_user.id).all()
        if queryRV:     
            db.session.delete(queryRV)                              # marking new code so I can comment on it later
        if len(allRV) > 11:
            db.session.delete(allRV[0])
        db.session.add(newRV)
        db.session.commit()
        ###########
        restaurantMap = Map(                                                # This is a Google Map's element which is fed the longitude and latitude data from the 'Business Details' get request       
        identifier="restaurantMap",                                         # in order to display a restaurant's location. 
        lat=parsed["coordinates"]["latitude"],                              # Roughly based on the documentation, linked here: https://pypi.org/project/flask-googlemaps/
        lng=parsed["coordinates"]["longitude"],
        zoom=16,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
             'lat': parsed["coordinates"]["latitude"],
             'lng': parsed["coordinates"]["longitude"],
             'infobox': parsed["name"]
          }
        ],
        maptype_control=False,                                              # Disabling certain Map UI elements in order to prevent clutter within a small window.
        streetview_control=False,                                           
        zoom_control=False,
        fullscreen_control=False
        )

        allReviews = Reviews.query.filter_by(business_id=businessId).all()      # Retrieving all reviews that match this restaurant's businessId in order to display them on the page.
        
        if request.method == 'POST':                                            
            if 'like' in request.form:  # This is kind of a mess, but basically, it checks to see if a user has a preference for this restaurant, and then either creates one or alters the old preference based on which button was pressed.
                queryPreference = Preferences.query.filter_by(user_id=current_user.id, business_id=businessId).first()
                if queryPreference:
                    queryPreference.likes = not queryPreference.likes
                    queryPreference.dislikes = not queryPreference.dislikes
                    db.session.commit()
                    return render_template("restaurant.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), preference=queryPreference, business=parsed, restaurantMap=restaurantMap, reviews=allReviews)
                else:    
                    newPreference = Preferences(user_id=current_user.id, business_id=businessId, business_name=parsed["name"], business_image_url=parsed["image_url"], business_rating=parsed["rating"], business_rating_count=parsed["review_count"], likes=True, dislikes=False)
                    db.session.add(newPreference)
                    db.session.commit()
                    return render_template("restaurant.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), preference=newPreference, business=parsed, restaurantMap=restaurantMap, reviews=allReviews)
            if 'dislike' in request.form:
                queryPreference = Preferences.query.filter_by(user_id=current_user.id, business_id=businessId).first()
                if queryPreference:
                    queryPreference.likes = not queryPreference.likes
                    queryPreference.dislikes = not queryPreference.dislikes
                    db.session.commit()
                    return render_template("restaurant.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), preference=queryPreference, business=parsed, restaurantMap=restaurantMap, reviews=allReviews)
                else:    
                    newPreference = Preferences(user_id=current_user.id, business_id=businessId, business_name=parsed["name"], business_image_url=parsed["image_url"], business_rating=parsed["rating"], business_rating_count=parsed["review_count"], likes=False, dislikes=True)
                    db.session.add(newPreference)
                    db.session.commit()
                    return render_template("restaurant.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), preference=newPreference, business=parsed, restaurantMap=restaurantMap, reviews=allReviews)

            if 'submit-review' in request.form:             
                reviewText = request.form.get('review')                                                                     
                dateVisited = request.form.get('date-visited')
                rating = request.form.get('rating')
                             
                queryReview = Reviews.query.filter_by(username=current_user.username, business_id=businessId).first()       # Retrieving the data from the review form, checking to see if a user hasn't previously written a review for 
                if queryReview:                                                                                             # this restaurant (not currently allowed, functionality for editing and deleting reviews will be added later),
                    flash('You have already written a review for this business!', category='error')                         # and then creating a new Review object within our databse and committing the change.
                elif len(reviewText) > 120:
                    flash('Review cannot be more than 120 characters long!', category='error')
                elif len(reviewText) < 4:
                    flash('Review cannot be less than 4 characters long!', category='error')
                else:
                    newReview = Reviews(user_id=current_user.id, business_id=businessId, username=current_user.username, text=reviewText, date_visited=dateVisited, rating=rating, image=parsed["image_url"], restaurant_name=parsed["name"])
                    db.session.add(newReview)
                    db.session.commit()

                    flash('Review successfully submitted!', category='success')
                    
                    allReviews = Reviews.query.filter_by(business_id=businessId).all()
                    queryPreference = Preferences.query.filter_by(user_id=current_user.id, business_id=businessId).first()
                    return render_template("restaurant.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), preference=queryPreference, business=parsed, restaurantMap=restaurantMap, reviews=allReviews)

        queryPreference = Preferences.query.filter_by(user_id=current_user.id, business_id=businessId).first()
        return render_template("restaurant.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), preference=queryPreference, business=parsed, restaurantMap=restaurantMap, reviews=allReviews)
        
    else:
        PARAMETERS = {}
        response = requests.get(url=BUSINESS_DETAILS + businessId, 
                                params=PARAMETERS, 
                                headers=HEADERS)
        parsed = json.loads(response.text)

        restaurantMap = Map(
        identifier="restaurantMap",
        lat=parsed["coordinates"]["latitude"],
        lng=parsed["coordinates"]["longitude"],
        zoom=16,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
             'lat': parsed["coordinates"]["latitude"],
             'lng': parsed["coordinates"]["longitude"],
             'infobox': parsed["name"]
          }
        ],
        maptype_control=False,
        streetview_control=False,
        zoom_control=False,
        fullscreen_control=False
        )

        allReviews = Reviews.query.filter_by(business_id=businessId).all()

        return render_template("restaurant.html", user=current_user, business=parsed, restaurantMap=restaurantMap, reviews=allReviews)

@views.route('/recently-viewed')
@login_required
def recentlyViewed():
    recentlyViewedPages = RecentlyViewed.query.filter_by(user_id=current_user.id).order_by(RecentlyViewed.id.desc()).all()
    return render_template("recently-viewed.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), recentlyViewedPages=recentlyViewedPages)

@views.route('/my-reviews')
@login_required
def myReviews():
    #return render_template("my-reviews.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage))
    if(request.method=='POST'):
        queryReviewsDesc = Reviews.query.filter_by(user_id=current_user.id).order_by(Reviews.id.desc()).all()
        return render_template("my-reviews.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), reviews=queryReviewsDesc)

    queryReviews = Reviews.query.filter_by(user_id=current_user.id).all()
    return render_template("my-reviews.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage)
, reviews=queryReviews)


