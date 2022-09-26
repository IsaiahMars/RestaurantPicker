from flask import Flask

def createApp():
    app = Flask(__name__)
    app.config['SECRET KEY'] = "restPicker123"


    return app


# __init__.py is used to define the function createApp. In this
# function, we specify which modules to be exported (views.py, auth.py, etc).
