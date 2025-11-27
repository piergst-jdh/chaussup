from flask import Flask
from models import db
import os
from routes import init_routes


def get_secret_or_env(secret_name, env_name=None, default=None):
    """Read from Docker secret first, then env var, then default"""
    secret_path = f"/run/secrets/{secret_name}"
    if os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()
    # Fallback to env var (for local dev)
    if env_name:
        return os.environ.get(env_name, default)
    return default


def create_app():
    app = Flask(__name__)

    # Read secret key
    app.config["SECRET_KEY"] = get_secret_or_env(
        "secret_key", "SECRET_KEY", "dev-secret-key"
    )

    # Read database credentials
    db_user = get_secret_or_env("db_user", "DB_USER", "admin")
    db_password = get_secret_or_env("db_password", "DB_PASSWORD", "password")
    db_host = os.environ.get("DB_HOST", "localhost")
    db_name = os.environ.get("DB_NAME", "chaussup")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}?sslmode=require"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    init_routes(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
