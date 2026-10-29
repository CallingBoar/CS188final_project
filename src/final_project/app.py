import datetime

from dotenv import find_dotenv, load_dotenv
from flask import Flask, abort, render_template

# from final_project import auth, db, sessions
# from final_project._constants import SECRET_ENV_FILE
# from final_project.sessions import login_required


def create_app():
    # load_dotenv(find_dotenv(SECRET_ENV_FILE))
    app = Flask(__name__)
    # db.setup_for_app(app)
    # sessions.setup_sessions(app)
    # auth.setup_auth(app)
    setup_routes(app)
    return app

def hello():
    return render_template("hello.html")

def setup_routes(app):
    app.route("/")(hello)

def run_app(debug: bool = True) -> None:
    app = create_app()
    app.run(debug=debug)

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
