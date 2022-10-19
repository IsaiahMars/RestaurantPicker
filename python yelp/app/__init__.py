from flask import Flask
from flask_googlemaps import GoogleMaps

map = GoogleMaps()

def createApp():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "yelptesting"   

    
    app.config['GOOGLEMAPS_KEY'] = "AIzaSyDHUuntBzFTY0Wm3RjPGGLtauZwZRfG9c8"
    map.init_app(app)

    from .views import views

    app.register_blueprint(views, url_prefix="/")

    return app