from flask import Flask
from models import db
import os
from routes import init_routes
from init_db import initialize_database


def get_secret_or_env(secret_name, env_name=None):
    """Read from Docker secret first, then env var, then default"""
    secret_path = f"/run/secrets/{secret_name}"
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()
    # Fallback to env var (for local dev)
    if env_name:
        return os.environ.get(env_name)
    return ""


def create_app():
    app = Flask(__name__)

    # Read secret key
    app.config["SECRET_KEY"] = get_secret_or_env("secret_key", "SECRET_KEY")

    # Read database credentials
    db_user = get_secret_or_env("db_user", "DB_USER")
    db_password = get_secret_or_env("db_password", "DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")
    web_admin_user = get_secret_or_env("web_admin_user", "DB_USER")
    web_admin_password = get_secret_or_env("web_admin_password", "DB_USER")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}?sslmode=require"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        initialize_database(web_admin_user, web_admin_password)

    init_routes(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
