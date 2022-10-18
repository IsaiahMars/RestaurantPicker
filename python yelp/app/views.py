from flask import Blueprint, render_template, request
import requests
import json

views = Blueprint('views', __name__)


@views.route('/', methods=["POST", "GET"])
def home():
    if request.method == "POST":
        location = request.form.get("location")
        PARAMETERS = {'location':location,
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

        PARAMETERS = {'location':location,
              'radius':2500,
              'limit': 50,
              'term':'restaurant'
            }
        response = requests.get(url=BUSINESS_SEARCH, 
                                params=PARAMETERS, 
                                headers=HEADERS)
        parsed = json.loads(response.text)
        allBusinesses = parsed["businesses"]

        return render_template("home.html", trendingBusinesses=trendingBusinesses, allBusinesses=allBusinesses, location=location)

    return render_template("home.html", trendingBusinesses=[], allBusinesses=[])

@views.route('/restaurant/<businessId>', methods=["POST", "GET"])   
def restaurant(businessId):
    if request.method == 'GET':
        PARAMETERS = {}
        response = requests.get(url=BUSINESS_DETAILS + businessId, 
                                params=PARAMETERS, 
                                headers=HEADERS)
        parsed = json.loads(response.text)
        print("parsed data ---------------- ", flush=True)
        print(parsed, flush=True)
        return render_template("restaurant.html", id=businessId, business=parsed) 




# link to tutorial: https://www.youtube.com/watch?v=oggMBtza80E
# link to code source: https://github.com/areed1192/sigma_coding_youtube/blob/master/python/python-api/yelp-api/Yelp%20API%20-%20Other%20Search%20%26%20Categories.py
# link to parsing example: https://python.gotrained.com/yelp-fusion-api-tutorial/

# Define API Key, Search Type, and header
MY_API_KEY = 'YOUR_API_KEY_HERE'
BUSINESS_SEARCH = 'https://api.yelp.com/v3/businesses/search'
BUSINESS_DETAILS = 'https://api.yelp.com/v3/businesses/'
HEADERS = {'Authorization': 'bearer %s' % MY_API_KEY}



