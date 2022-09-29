from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def createApp():
    app = Flask(__name__)
    app.config['SECRET KEY'] = "restPicker123"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://'




    return app


# __init__.py is used to define the function createApp. In this
# function, we specify which modules to be exported (views.py, auth.py, etc).
