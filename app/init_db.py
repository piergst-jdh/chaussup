from models import db, User, Product
from sqlalchemy.exc import IntegrityError, ProgrammingError
from flask import current_app


def initialize_database(username, password):
    """Drop and recreate all tables with demo data"""
    try:
        current_app.logger.debug("Attempting to drop all tables...")
        db.drop_all()
    except Exception as e:
        current_app.logger.debug(f"Note: {e}")

    try:
        current_app.logger.debug("Creating database tables...")
        db.create_all()
    except (IntegrityError, ProgrammingError) as e:
        current_app.logger.debug(f"Tables might already exist: {e}")
        db.session.rollback()

    try:
        current_app.logger.debug(f"Creating admin user: {username}")
        admin = User(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
    except IntegrityError:
        current_app.logger.debug("Admin user already exists")
        db.session.rollback()

    try:
        if Product.query.count() == 0:
            current_app.logger.debug("Creating demo products...")
            products = [
                Product(
                    name="Duo Asymetrique Foret",
                    description="Une chaussette verte sapin, une marron ecorce. L'economie circulaire commence dans votre tiroir !",
                    price=12.90,
                    image_url="/static/images/duo_forest.png",
                ),
                Product(
                    name="Pack Rebelle Arc-en-ciel",
                    description="7 couleurs, 0 paires identiques. Parce que la conformite c'est ringard.",
                    price=24.90,
                    image_url="/static/images/rebel_pack.jpg",
                ),
                Product(
                    name="Edition Limitee Ocean",
                    description="Bleu marine + turquoise recycle. Sauvez les mers, un pied a la fois.",
                    price=15.90,
                    image_url="/static/images/ocean_limited.jpg",
                ),
                Product(
                    name="Classics Depareilles Noir & Blanc",
                    description="L'intemporel revisite. Elegance asymetrique garantie.",
                    price=11.90,
                    image_url="/static/images/black_white.jpg",
                ),
            ]
            
            for product in products:
                db.session.add(product)
            
            db.session.commit()
            current_app.logger.debug(f"Added {len(products)} demo products")
        else:
            current_app.logger.debug("Products already exist, skipping...")
    except Exception as e:
        current_app.logger.debug(f"Error creating products: {e}")
        db.session.rollback()

    current_app.logger.info("Database initialization complete!")