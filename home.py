from flask import Blueprint, render_template, abort, request, flash, jsonify
from jinja2 import TemplateNotFound
from forms import RegisterForm, LoginForm
from flask_login import login_required, current_user
import requests
import json

home_pages = Blueprint(
    'home',__name__,
    template_folder='home_templates'
)

@home_pages.route("/")
def home():
    login = LoginForm(request.form)
    register = RegisterForm(request.form)
    flash('gg')
    return render_template('home.html', login=login,register=register)



        