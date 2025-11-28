from models import db, User, Product
from sqlalchemy.exc import IntegrityError, ProgrammingError


def initialize_database(username, password):
    """Drop and recreate all tables with demo data"""
    try:
        print("Attempting to drop all tables...")
        db.drop_all()
    except Exception as e:
        print(f"Note: {e}")

    try:
        print("Creating database tables...")
        db.create_all()
    except (IntegrityError, ProgrammingError) as e:
        print(f"Tables might already exist: {e}")
        db.session.rollback()

    try:
        print(f"Creating admin user: {username}")
        admin = User(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
    except IntegrityError:
        print("Admin user already exists")
        db.session.rollback()

    try:
        if Product.query.count() == 0:
            print("Creating demo products...")
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
            print(f"Added {len(products)} demo products")
        else:
            print("Products already exist, skipping...")
    except Exception as e:
        print(f"Error creating products: {e}")
        db.session.rollback()

    print("Database initialization complete!")