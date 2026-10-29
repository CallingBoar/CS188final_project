#import datetime
#from functools import wraps

#from dotenv import find_dotenv, load_dotenv
from flask import Flask, render_template#, g, json, request, Response, abort
#from flask_restful import Resource, reqparse
#from cs188_a3.__constants import PROJECT_ROOT
#import os
#from final_project.db import Database
#from flask_bcrypt import Bcrypt
#import datetime #for storing timestamps of messages and fronts
from final_project.auth import setup_auth


def create_app():
    app = Flask(__name__)
    setup_auth(app)
    setup_routes(app)
    return app


def setup_routes(app):
    app.route("/")(index)
    app.route("/hello")(hello)

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