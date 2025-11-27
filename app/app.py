from flask import Flask
from models import db
import os
from routes import init_routes


def create_app():
    app = Flask(__name__)

    # Secret key for sessions
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-prod"
    )

    # Azure PostgreSQL configuration
    db_user = os.environ.get("DB_USER", "your_admin_user")
    db_password = os.environ.get("DB_PASSWORD", "your_password")
    db_host = os.environ.get("DB_HOST", "your-server.postgres.database.azure.com")
    db_name = os.environ.get("DB_NAME", "chaussup")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        # f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}?sslmode=require"
        f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}?sslmode=disable"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    db.init_app(app)

    with app.app_context():
        db.create_all()

    init_routes(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
