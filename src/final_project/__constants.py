import re

# ---------------------------------------------------------------------------
# Secrets and configuration
# ---------------------------------------------------------------------------

SECRET_ENV_FILE = ".secret.env"
"""The name of the file that contains secrets (like the database connection string) in development."""

# NOTE: This is NOT the the connection string itself. Rather, it is the name of the environment variable.
CONNECTION_STRING_VARIABLE = "AZURE_SQL_CONNECTIONSTRING"
""" The name of the environment variable that holds the database connection string."""

# ---------------------------------------------------------------------------
# Account rules
# ---------------------------------------------------------------------------

MAX_USERNAME_LENGTH = 20
MIN_PASSWORD_LENGTH = 8

# These match the patterns in auth.js. We check on the server too, because
# anyone can skip our JavaScript and send a request straight to /register
# (try it with Postman!). Client-side validation is a convenience for the user.
# Server-side validation is the one that actually protects you.
USERNAME_PATTERN = re.compile(rf"[A-Za-z0-9]{{1,{MAX_USERNAME_LENGTH}}}")
# \x21-\x7E is the range of printable ASCII characters from ! to ~ (no spaces).
PASSWORD_PATTERN = re.compile(rf"[\x21-\x7E]{{{MIN_PASSWORD_LENGTH},}}")

# Login uses the same message for "no such user" and "wrong password".
BAD_LOGIN_MESSAGE = "Incorrect username or password"

# ---------------------------------------------------------------------------
# Sessions (added in Part 3)
# ---------------------------------------------------------------------------

# The name of the environment variable that holds the key we sign cookies with.
APP_SECRET_VARIABLE = "APP_SECRET"

# The name of the cookie that holds the signed session ID.
SESSION_COOKIE_NAME = "sessionID"

# How long a session lasts, in seconds. Used for both the database row and the cookie.
SESSION_LIFETIME_SECONDS = 60 * 60 * 24 * 7  # one week