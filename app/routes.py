from flask import render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from models import db, Product, User


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def init_routes(app):

    # Homepage with products
    @app.route("/")
    def index():
        products = Product.query.all()
        return render_template("index.html", products=products)

    # Cart API (client-side storage, but validation endpoint)
    @app.route("/api/cart/validate", methods=["POST"])
    def validate_cart():
        cart_items = request.json.get("items", [])
        product_ids = [item["id"] for item in cart_items]
        products = Product.query.filter(Product.id.in_(product_ids)).all()

        validated_items = []
        total = 0
        for item in cart_items:
            product = next((p for p in products if p.id == item["id"]), None)
            if product:
                quantity = int(item.get("quantity", 1))
                subtotal = float(product.price) * quantity
                validated_items.append(
                    {
                        "id": product.id,
                        "name": product.name,
                        "price": float(product.price),
                        "quantity": quantity,
                        "subtotal": subtotal,
                    }
                )
                total += subtotal

        return jsonify({"items": validated_items, "total": total})

    # Admin login
    @app.route("/admin/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session["admin_logged_in"] = True
                session["user_id"] = user.id
                return redirect(url_for("admin_dashboard"))

            return render_template("login.html", error="Identifiants invalides")

        return render_template("login.html")

    # Admin logout
    @app.route("/admin/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    # Admin dashboard
    @app.route("/admin")
    @login_required
    def admin_dashboard():
        products = Product.query.all()
        return render_template("admin.html", products=products)

    # Admin: Add product
    @app.route("/admin/product/add", methods=["POST"])
    @login_required
    def add_product():
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        image_url = request.form.get("image_url")

        product = Product(
            name=name, description=description, price=price, image_url=image_url
        )
        db.session.add(product)
        db.session.commit()

        return redirect(url_for("admin_dashboard"))

    # Admin: Delete product
    @app.route("/admin/product/delete/<int:product_id>", methods=["POST"])
    @login_required
    def delete_product(product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()

        return redirect(url_for("admin_dashboard"))

    # Admin: Edit product
    @app.route("/admin/product/edit/<int:product_id>", methods=["POST"])
    @login_required
    def edit_product(product_id):
        product = Product.query.get_or_404(product_id)

        product.name = request.form.get("name")
        product.description = request.form.get("description")
        product.price = request.form.get("price")
        product.image_url = request.form.get("image_url")

        db.session.commit()

        return redirect(url_for("admin_dashboard"))
