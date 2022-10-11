# this will be used to render the pages used in our login system
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from azure.storage.blob import BlobServiceClient
from .models import User
from . import db
