# this is used to render our routes (randomizer page, map page, etc...)
from flask import render_template, redirect, request, current_app, session, flash, url_for
from flask.ext.secuirty import LoginForm, current_user, login_required, login_ser
