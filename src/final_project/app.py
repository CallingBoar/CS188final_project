#import datetime
#from functools import wraps

from dotenv import find_dotenv, load_dotenv
from flask import Flask, render_template#, g, json, request, Response, abort
#from flask_restful import Resource, reqparse
#from cs188_a3.__constants import PROJECT_ROOT
#import os
#from final_project.db import Database
#from flask_bcrypt import Bcrypt
#import datetime #for storing timestamps of messages and fronts
from final_project.db import setup_for_app
from final_project.__constants import SECRET_ENV_FILE
from final_project.auth import setup_auth
from final_project.sessions import login_required, setup_sessions


def create_app():
    load_dotenv(find_dotenv(SECRET_ENV_FILE))
    app = Flask(__name__)
    setup_for_app(app)
    setup_sessions(app)
    setup_auth(app)
    setup_routes(app)
    return app

@login_required
def account():
    return render_template("account.html")

def setup_routes(app):
    app.route("/")(index)
    app.route("/hello")(hello)
    app.route("/account")(account)

def run_app(debug: bool = True) -> None:
    app = create_app()
    app.run(debug=debug)

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

def index():
    return render_template("index.html")

def hello():
    return render_template("hello.html")