# This file will be used to create our other routes (randomizer page, map page, etc...)
import requests, json
from flask import Blueprint, render_template, request, flash
from flask_login import current_user, login_required
from flask_googlemaps import Map
from .auth import get_img_url_with_blob_sas_token
from .models import Preferences, Reviews, RecentlyViewed
from . import db, simple_geoip

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

@views.route('/locations', methods=["GET", "POST"])
def locations():
    #geoip_data = simple_geoip.get_geoip_data('137.142.211.54')  #temp user location
    geoip_data = {'location':{'city':'Plattsburgh'}, 'coordinates':{'latitude':44.693571, 'longitude':-73.4664782}}

    PARAMETERS = {'location':geoip_data['location']['city'], 
            'radius':2500,
            'limit': 50,
            'term':'restaurant'
            }
    response = requests.get(url=BUSINESS_SEARCH, 
                            params=PARAMETERS, 
                            headers=HEADERS)
    parsed = json.loads(response.text)
    allNearbyBusinesses = parsed["businesses"]

    markerArray = []
    for business in allNearbyBusinesses:
        markerArray.append({'icon':'http://maps.google.com/mapfiles/ms/icons/red-dot.png', 'lat': business["coordinates"]["latitude"], 'lng':business["coordinates"]["longitude"]})

    nearbyRestaurantsMap = Map(                                                 
    identifier="nearbyRestaurantsMap",                                         
    lat=geoip_data['coordinates']['latitude'],                              
    lng=geoip_data['coordinates']['longitude'],
    zoom=14, 
    markers=markerArray,
    maptype_control=False,                                              
    streetview_control=False,                                           
    zoom_control=False,
    fullscreen_control=False
    )

    if current_user.is_authenticated:
        return render_template("locations.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), nearbyRestaurantsMap=nearbyRestaurantsMap)
    else:
        return render_template("locations.html", user=current_user, nearbyRestaurantsMap=nearbyRestaurantsMap)

@views.route('/questionnaire', methods=["GET","POST"])
@login_required
def questionnaire():
    if request.method == "POST":
        if "questionnaire-submit" in request.form:
            responseDict = {'regional-response':request.form.getlist('regional-response'), 
                            'foodtype-response':request.form.getlist('foodtype-response'), 
                            'restaurantstyle-response':request.form.getlist('restaurantstyle-response'),
                            'price-response':request.form.getlist('price-response'),
                            'dietary-response':request.form.getlist('dietary-response'),
                            'accessibility-response':request.form.getlist('accessibility-response')}
            queryResponses = QuestionnaireResponse.query.filter_by(user_id=current_user.id).all()
            for response in queryResponses:
                db.session.delete(response)
            for key in responseDict:
                for response in responseDict[key]:
                        newResponse = QuestionnaireResponse(user_id=current_user.id, response_type=key, responses=response)
                        db.session.add(newResponse)
            db.session.commit()
            flash('Questionnaire responses updated successfully!', category='success')
            return redirect(url_for("views.home"))
    queryResponses = QuestionnaireResponse.query.filter_by(user_id=current_user.id).all()
    questionnaireResponses = []
    for response in queryResponses:
        questionnaireResponses.append([response.response_type, response.responses])
    return render_template("questionnaire.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), questionnaireResponses=questionnaireResponses)

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
        ################################
        newRV = RecentlyViewed(user_id=current_user.id, business_id=businessId, business_name=parsed["name"], business_image_url=parsed["image_url"], business_rating=parsed["rating"], business_rating_count=parsed["review_count"])
        queryRV = RecentlyViewed.query.filter_by(user_id=current_user.id, business_id=businessId).first()
        allRV = RecentlyViewed.query.filter_by(user_id=current_user.id).all()
        if queryRV:
            db.session.delete(queryRV)        
        if len(allRV) > 11:
            db.session.delete(allRV[0])
        db.session.add(newRV)
        db.session.commit()
        ##################### NEW CODE
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

        allReviews = Reviews.query.filter_by(business_id=businessId).order_by(Reviews.id.desc()).all()      # Retrieving all reviews that match this restaurant's businessId in order to display them on the page.
        
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
                    newReview = Reviews(user_id=current_user.id, business_id=businessId, business_name=parsed["name"], business_image_url=parsed["image_url"], username=current_user.username, text=reviewText, date_visited=dateVisited, rating=rating, flags=0)
                    db.session.add(newReview)
                    db.session.commit()

                    flash('Review successfully submitted!', category='success')
                    
                    allReviews = Reviews.query.filter_by(business_id=businessId).order_by(Reviews.id.desc()).all() 
                    queryPreference = Preferences.query.filter_by(user_id=current_user.id, business_id=businessId).first()
                    return render_template("restaurant.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), preference=queryPreference, business=parsed, restaurantMap=restaurantMap, reviews=allReviews)
            if 'flag' in request.form:
                reviewId = request.form.get('reviewId')
                queryReview = Reviews.query.filter_by(id=reviewId).first()
                queryReview.flags += 1
                if(queryReview.flags >= 10):
                    db.session.delete(queryReview)
                    flash("This review has been removed due to receiving too many flags. Thank you!", category="success")
                else:
                    flash("Review successfully flagged. Thank you!", category="success")
                db.session.commit()

                allReviews = Reviews.query.filter_by(business_id=businessId).order_by(Reviews.id.desc()).all() 
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

@views.route('/my-reviews', methods=["GET", "POST"])
@login_required
def myReviews():
    if request.method == "POST":
        if 'oldest' in request.form:
            oldestReviews = Reviews.query.filter_by(user_id=current_user.id).all()
            lastSort = "oldest"
            return render_template("my-reviews.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), allReviews=oldestReviews, lastSort=lastSort)
        if 'newest' in request.form:
            lastSort = "newest"
            newestReviews = Reviews.query.filter_by(user_id=current_user.id).order_by(Reviews.id.desc()).all()
            return render_template("my-reviews.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), allReviews=newestReviews, lastSort=lastSort)
        if 'delete' in request.form:
            reviewId = request.form.get('reviewId')
            lastSort = request.form.get('lastSort')
            queryReview = Reviews.query.filter_by(id=reviewId).first()
            db.session.delete(queryReview)
            db.session.commit()
            if(lastSort == "oldest"):
                lastSort = "oldest"
                oldestReviews = Reviews.query.filter_by(user_id=current_user.id).all()
                flash("Review deleted successfully!", category="success")
                return render_template("my-reviews.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), allReviews=oldestReviews, lastSort=lastSort)
            elif(lastSort == "newest"):
                lastSort = "newest"
                newestReviews = Reviews.query.filter_by(user_id=current_user.id).order_by(Reviews.id.desc()).all()
                flash("Review deleted successfully!", category="success")
                return render_template("my-reviews.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), allReviews=newestReviews, lastSort=lastSort)
        if 'edit-review' in request.form:
            reviewText = request.form.get('review')                                                                     
            dateVisited = request.form.get('date-visited')
            rating = request.form.get('rating')
            reviewId = request.form.get('reviewId')
            lastSort = request.form.get('lastSort')
            queryReview = Reviews.query.filter_by(id=reviewId).first()
            if not (queryReview):
                flash("An error has occured or the review doesn't exist anymore.", category="error")
            elif len(reviewText) > 120:
                flash('Review cannot be more than 120 characters long!', category='error')
            elif len(reviewText) < 4:
                flash('Review cannot be less than 4 characters long!', category='error')
            else:
                queryReview.text = reviewText
                queryReview.date_visited = dateVisited
                queryReview.rating = rating
                db.session.commit()
                if(lastSort == "oldest"):
                    lastSort = "oldest"
                    oldestReviews = Reviews.query.filter_by(user_id=current_user.id).all()
                    flash("Review updated successfully!", category="success")
                    return render_template("my-reviews.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), allReviews=oldestReviews, lastSort=lastSort)
                elif(lastSort == "newest"):
                    lastSort = "newest"
                    newestReviews = Reviews.query.filter_by(user_id=current_user.id).order_by(Reviews.id.desc()).all()
                    flash("Review updated successfully!", category="success")
                    return render_template("my-reviews.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), allReviews=newestReviews, lastSort=lastSort)
            

    newestReviews = Reviews.query.filter_by(user_id=current_user.id).order_by(Reviews.id.desc()).all()
    return render_template("my-reviews.html", user=current_user, userImageURL=get_img_url_with_blob_sas_token(current_user.userImage), allReviews=newestReviews)



