# =============================================================================
# app/config.py  -  CONFIGURATION + DATABASE BOOTSTRAP
# -----------------------------------------------------------------------------
# Responsibilities of this file:
#   1. Read settings (DB host/user/password/name) from a .env file so secrets
#      stay OUT of the source code.
#   2. Expose a Config class that Flask loads (app.config.from_object(Config)).
#   3. Provide ensure_database_exists(): create the MySQL database the first
#      time the app runs, because MySQL will not create it automatically.
# =============================================================================

import os
import mysql.connector                  # low-level MySQL driver (to create the DB)
from dotenv import load_dotenv          # loads key=value pairs from .env

# Find this project's root folder (the "todo" folder, one level above /app)
# and load the .env that sits there. Using an absolute path means the app works
# no matter which directory you launch it from.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- Raw connection settings, read once from the environment -----------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "todo_db")


def _build_uri():
    """Assemble the SQLAlchemy connection URL from the parts above.

    Format:  dialect+driver://user:password@host:port/database
    Keeping this in one helper means there is a SINGLE place to change how we
    connect to the database.
    """
    return (
        "mysql+mysqlconnector://"
        f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


def ensure_database_exists():
    """Create the target database if it does not already exist.

    We connect to the MySQL *server* WITHOUT naming a database, then run
    `CREATE DATABASE IF NOT EXISTS ...`. This is safe to call every startup:
    if the database is already there, MySQL does nothing.
    """
    connection = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD
    )
    cursor = connection.cursor()
    # Backticks let the name be used safely; charset keeps text (e.g. emojis) safe.
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.close()
    connection.close()


class Config:
    """All Flask/SQLAlchemy settings live here as class attributes.

    Flask reads them via app.config.from_object(Config) in the app factory.
    """
    # WHERE the database is. Built from the .env values above.
    SQLALCHEMY_DATABASE_URI = _build_uri()
    # Turn off a noisy event-tracking feature we don't use (saves memory).
    SQLALCHEMY_TRACK_MODIFICATIONS = False
