from app import create_app
from models import db, User, Product


def init_database():
    app = create_app()

    with app.app_context():
        # Drop all tables and recreate them (use with caution in production)
        print("Creating database tables...")
        db.create_all()

        # Check if admin already exists
        existing_admin = User.query.filter_by(username="admin").first()
        if not existing_admin:
            # Create default admin user
            admin = User(username="admin")
            admin.set_password("Chauss2024!")  # Change this password in production
            db.session.add(admin)
            print("Admin user created (username: admin, password: Chauss2024!)")
        else:
            print("Admin user already exists")

        # Check if products already exist
        existing_products = Product.query.count()
        if existing_products == 0:
            # Create demo products
            products = [
                Product(
                    name="Duo Asymétrique Forêt",
                    description="Une chaussette verte sapin, une marron écorce. L'économie circulaire commence dans votre tiroir !",
                    price=12.90,
                    image_url="/static/images/duo_forest.png",
                ),
                Product(
                    name="Pack Rebelle Arc-en-ciel",
                    description="7 couleurs, 0 paires identiques. Parce que la conformité c'est ringard.",
                    price=24.90,
                    image_url="/static/images/rebel_pack.jpg",
 
                ),
                Product(
                    name="Edition Limitée Océan",
                    description="Bleu marine + turquoise recyclé. Sauvez les mers, un pied à la fois.",
                    price=15.90,
                    image_url="/static/images/ocean_limited.jpg",
                ),
                Product(
                    name="Classics Dépareillés Noir & Blanc",
                    description="L'intemporel revisité. Élégance asymétrique garantie.",
                    price=11.90,
                    image_url="/static/images/black_white.jpg",
 
                ),
            ]

            for product in products:
                db.session.add(product)

            print(f"Added {len(products)} demo products")
        else:
            print(f"{existing_products} products already exist in database")

        # Commit all changes
        db.session.commit()
        print("Database initialization complete!")


if __name__ == "__main__":
    init_database()
