"""Login sessions, stored in the Sessions table and identified by a signed cookie.

How it fits together:
  1. When a user logs in, Login asks the database for a new session, and
     set_session_cookie() tells the browser to store that session's ID in a cookie.
  2. The browser automatically sends that cookie back with every request to our site.
  3. Before every request, load_current_user() reads the cookie, looks up the
     session, and stores the logged-in user (or None) in g.current_user.
  4. Logging out deletes the session row and the cookie.
"""

import functools
import hashlib
import hmac
import os

from flask import Flask, Response, g, redirect, request, url_for

from final_project.__constants import APP_SECRET_VARIABLE, SESSION_COOKIE_NAME, SESSION_LIFETIME_SECONDS
from final_project.db import get_db


def get_app_secret() -> bytes:
    """Read the app secret from the environment, the same way db.py reads the connection string."""

    return os.environ[APP_SECRET_VARIABLE].encode()


def running_on_azure() -> bool:
    """Azure sets the WEBSITE_HOSTNAME environment variable on every web app."""
    return "WEBSITE_HOSTNAME" in os.environ


def compute_signature(session_id: str) -> str:
    """Compute an HMAC signature for a session ID.

    Only someone who knows the app secret can compute this, so a valid
    signature proves that our server created the cookie.
    """
    return hmac.new(get_app_secret(), session_id.encode(), hashlib.sha256).hexdigest()


def sign_session_id(session_id: str) -> str:
    """Build the cookie value: "<session id>:<signature>"."""
    return f"{session_id}:{compute_signature(session_id)}"


def verify_session_cookie(cookie: str | None) -> str | None:
    """Return the session ID if the cookie's signature is valid, otherwise None."""
    if not cookie:
        return None
    session_id, _, signature = cookie.partition(":")
    # compare_digest takes the same amount of time no matter where the first
    # wrong character is. A normal == stops at the first difference, and an
    # attacker could time that to guess the signature one character at a time.
    if hmac.compare_digest(signature.encode(), compute_signature(session_id).encode()):
        return session_id
    return None


def set_session_cookie(response: Response, session_id: str) -> None:
    """Tell the browser to store the signed session ID in a cookie."""
    response.set_cookie(
        SESSION_COOKIE_NAME,
        value=sign_session_id(session_id),
        # How long the browser keeps the cookie. Matches the expiry in the database.
        max_age=SESSION_LIFETIME_SECONDS,
        # JavaScript on the page can't read this cookie (document.cookie won't show it).
        httponly=True,
        # Don't send the cookie with requests that other websites start, except
        # when the user clicks a plain link to our site.
        samesite="Lax",
        # Only send the cookie over HTTPS. Azure uses HTTPS; your laptop doesn't.
        secure=running_on_azure(),
    )


def clear_session_cookie(response: Response) -> None:
    """Tell the browser to delete the session cookie."""
    response.delete_cookie(SESSION_COOKIE_NAME, httponly=True, samesite="Lax", secure=running_on_azure())


def load_current_user() -> None:
    """Look up the logged-in user before every request and store it in g.current_user.

    g.current_user is a row with the user's info, or None if nobody is logged in.
    """
    g.current_user = None

    # Static files (CSS, JavaScript, images) don't care who you are, so skip
    # the trip to the database for them.
    if request.endpoint == "static":
        return

    session_id = verify_session_cookie(request.cookies.get(SESSION_COOKIE_NAME))
    if session_id is None:
        return

    # This is None if the session isn't in the table anymore (for example,
    # because the user logged out somewhere else).
    g.current_user = get_db().get_session_user(session_id)


def inject_current_user() -> dict:
    """Make `current_user` available in every template."""
    return {"current_user": g.get("current_user")}


def login_required(view):
    """Decorator for routes that only logged-in users may see.

    Anyone else gets sent back to the home page.
    """

    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if g.current_user is None:
            return redirect(url_for("index"))
        return view(*args, **kwargs)

    return wrapper


def setup_sessions(app: Flask) -> None:
    """Hook sessions into the app. Call this from create_app()."""
    app.before_request(load_current_user)
    app.context_processor(inject_current_user)

