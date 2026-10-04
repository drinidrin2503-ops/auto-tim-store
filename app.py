import json
import hmac
import os
import secrets
import sqlite3
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "autotim.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            brand TEXT NOT NULL,
            price INTEGER NOT NULL,
            old_price INTEGER,
            stock INTEGER NOT NULL DEFAULT 0,
            rating REAL DEFAULT 0,
            review_count INTEGER DEFAULT 0,
            description TEXT,
            short_description TEXT,
            specifications TEXT,
            image_url TEXT,
            gallery TEXT,
            featured INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            customer_phone TEXT,
            customer_email TEXT,
            delivery_address TEXT,
            comment TEXT,
            total INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price INTEGER,
            FOREIGN KEY(order_id) REFERENCES orders(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
        """
    )

    conn.execute("UPDATE products SET image_url = '', gallery = '[]' WHERE image_url LIKE 'http%' OR gallery LIKE 'http%' OR image_url IS NULL")

    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
        products = [
            {
                "name": "Фильтр масляный Mann W914/2",
                "slug": "filtr-maslyanyj-mann-w914-2",
                "category": "Масла и жидкости",
                "brand": "MANN",
                "price": 450,
                "old_price": 520,
                "stock": 25,
                "rating": 4.8,
                "review_count": 124,
                "description": "Высокий класс фильтрации масла для современных бензиновых и дизельных двигателей.",
                "short_description": "Масляный фильтр для надежной защиты мотора",
                "specifications": json.dumps(
                    {
                        "Материал": "Синтетический фильтрующий элемент",
                        "Размер": "93 мм",
                        "Производство": "Германия",
                        "Совместимость": "Audi, BMW, Mercedes, VW"
                    },
                    ensure_ascii=False,
                ),
                "image_url": "",
                "gallery": json.dumps([], ensure_ascii=False),
                "featured": 1,
            },
            {
                "name": "Тормозные колодки Brembo P 85 020",
                "slug": "tormoznye-kolodki-brembo-p-85-020",
                "category": "Тормозные колодки",
                "brand": "Brembo",
                "price": 2450,
                "old_price": 3000,
                "stock": 15,
                "rating": 5.0,
                "review_count": 89,
                "description": "Дисковые тормозные колодки премиум-класса с высокой устойчивостью к нагреву.",
                "short_description": "Премиальные тормозные колодки для безопасной езды",
                "specifications": json.dumps(
                    {
                        "Тип": "Дисковые",
                        "Материал": "Керамика",
                        "Серия": "P 85 020",
                        "Артикул": "Brembo 1200"
                    },
                    ensure_ascii=False,
                ),
                "image_url": "",
                "gallery": json.dumps([], ensure_ascii=False),
                "featured": 1,
            },
            {
                "name": "Свечи зажигания NGK BKR6EIX",
                "slug": "svechi-zazhiganiya-ngk-bkr6eix",
                "category": "Автозапчасти",
                "brand": "NGK",
                "price": 320,
                "old_price": 380,
                "stock": 42,
                "rating": 4.7,
                "review_count": 156,
                "description": "Высокотемпературные свечи с улучшенной искрой и стабильной работой двигателя.",
                "short_description": "Свечи зажигания для стабильной работы двигателя",
                "specifications": json.dumps(
                    {
                        "Тип": "Платиновая",
                        "Диаметр": "14 мм",
                        "Калильное число": "6",
                        "Страна": "Япония"
                    },
                    ensure_ascii=False,
                ),
                "image_url": "",
                "gallery": json.dumps([], ensure_ascii=False),
                "featured": 0,
            },
            {
                "name": "Аккумулятор Bosch S5 60 Ah",
                "slug": "akkumulyator-bosch-s5-60-ah",
                "category": "Аккумуляторы",
                "brand": "Bosch",
                "price": 5200,
                "old_price": 6800,
                "stock": 8,
                "rating": 4.9,
                "review_count": 61,
                "description": "Надежный аккумулятор для городских и трассовых поездок с хорошей отдачей старта.",
                "short_description": "Мощный аккумулятор для стабильного запуска",
                "specifications": json.dumps(
                    {
                        "Емкость": "60 Ah",
                        "Пусковой ток": "540 A",
                        "Гарантия": "24 месяца",
                        "Тип": "Кальциевая технология"
                    },
                    ensure_ascii=False,
                ),
                "image_url": "",
                "gallery": json.dumps([], ensure_ascii=False),
                "featured": 1,
            },
            {
                "name": "Моторное масло Shell Helix Ultra",
                "slug": "motornoe-maslo-shell-helix-ultra",
                "category": "Масла и жидкости",
                "brand": "Shell",
                "price": 1800,
                "old_price": 2100,
                "stock": 31,
                "rating": 4.8,
                "review_count": 188,
                "description": "Полностью синтетическое масло с повышенной защитой двигателя в условиях высокой нагрузки.",
                "short_description": "Синтетическое масло для современных моторов",
                "specifications": json.dumps(
                    {
                        "Объем": "5 л",
                        "Класс": "API SN",
                        "Вязкость": "5W-40",
                        "Тип": "Полностью синтетическое"
                    },
                    ensure_ascii=False,
                ),
                "image_url": "",
                "gallery": json.dumps([], ensure_ascii=False),
                "featured": 0,
            },
            {
                "name": "Фильтр салонный Cabin Air Filter",
                "slug": "filtr-salonnij-cabin-air-filter",
                "category": "Шины и диски",
                "brand": "MAF",
                "price": 890,
                "old_price": 1100,
                "stock": 54,
                "rating": 4.5,
                "review_count": 72,
                "description": "Эффективная очистка воздуха в салоне и защита системы кондиционирования.",
                "short_description": "Фильтр салона для чистого воздуха в кабине",
                "specifications": json.dumps(
                    {
                        "Форма": "Плоский",
                        "Материал": "Активированный уголь",
                        "Применение": "Легковые автомобили",
                        "Производство": "Европа"
                    },
                    ensure_ascii=False,
                ),
                "image_url": "",
                "gallery": json.dumps([], ensure_ascii=False),
                "featured": 0,
            },
            {
                "name": "Масляный фильтр Bosch 0986AF",
                "slug": "maslyanyj-filtr-bosch-0986af",
                "category": "Масла и жидкости",
                "brand": "Bosch",
                "price": 610,
                "old_price": 760,
                "stock": 19,
                "rating": 4.6,
                "review_count": 93,
                "description": "Надежный масляный фильтр для современной техники с повышенной нагрузкой.",
                "short_description": "Фильтр для надежной защиты двигателя",
                "specifications": json.dumps(
                    {
                        "Размер": "95 мм",
                        "Материал": "Синтетика",
                        "Гарантия": "12 месяцев",
                        "Подходит": "Дизель и бензин"
                    },
                    ensure_ascii=False,
                ),
                "image_url": "",
                "gallery": json.dumps([], ensure_ascii=False),
                "featured": 0,
            },
            {
                "name": "Диски колесные R18 Alloy Max",
                "slug": "diski-kolesnye-r18-alloy-max",
                "category": "Шины и диски",
                "brand": "Alloy Max",
                "price": 7600,
                "old_price": 9200,
                "stock": 12,
                "rating": 4.7,
                "review_count": 48,
                "description": "Легкосплавные диски для уверенного управления и эстетичного внешнего вида автомобиля.",
                "short_description": "Легкосплавный диск для городских и дорожных условий",
                "specifications": json.dumps(
                    {
                        "Диаметр": "18\"",
                        "Ширина": "7.5J",
                        "Паз": "5x114.3",
                        "Материал": "Легкий сплав"
                    },
                    ensure_ascii=False,
                ),
                "image_url": "",
                "gallery": json.dumps([], ensure_ascii=False),
                "featured": 1,
            },
        ]

        for product in products:
            conn.execute(
                """
                INSERT INTO products (
                    name, slug, category, brand, price, old_price, stock,
                    rating, review_count, description, short_description,
                    specifications, image_url, gallery, featured
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product["name"],
                    product["slug"],
                    product["category"],
                    product["brand"],
                    product["price"],
                    product["old_price"],
                    product["stock"],
                    product["rating"],
                    product["review_count"],
                    product["description"],
                    product["short_description"],
                    product["specifications"],
                    product["image_url"],
                    product["gallery"],
                    product["featured"],
                ),
            )

    conn.commit()
    conn.close()


def product_record(row):
    if not row:
        return None
    item = dict(row)
    item["specifications"] = json.loads(item["specifications"]) if item.get("specifications") else {}
    item["gallery"] = json.loads(item["gallery"]) if item.get("gallery") else []
    return item


def get_products(limit=None, category=None, min_price=0, max_price=100000, search="", brand="all"):
    query = "SELECT * FROM products WHERE active = 1"
    params = []

    if category and category != "all":
        query += " AND category = ?"
        params.append(category)
    if brand and brand != "all":
        query += " AND brand = ?"
        params.append(brand)
    if search:
        query += " AND (name LIKE ? OR description LIKE ? OR short_description LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
    if min_price:
        query += " AND price >= ?"
        params.append(min_price)
    if max_price:
        query += " AND price <= ?"
        params.append(max_price)

    query += " ORDER BY featured DESC, price ASC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [product_record(row) for row in rows]


def get_product_by_id(product_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return product_record(row)


def get_product_by_slug(slug):
    conn = get_db()
    row = conn.execute("SELECT * FROM products WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    return product_record(row)


def get_cart_items():
    cart = session.get("cart", {})
    if not cart:
        return []
    products = []
    for product_id, quantity in cart.items():
        product = get_product_by_id(int(product_id))
        if product:
            products.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "image_url": product["image_url"],
                "qty": quantity,
                "total": product["price"] * quantity,
            })
    return products


def get_cart_total():
    return sum(item["total"] for item in get_cart_items())


def get_brands():
    conn = get_db()
    rows = conn.execute("SELECT DISTINCT brand FROM products WHERE active = 1 ORDER BY brand ASC").fetchall()
    conn.close()
    return [row[0] for row in rows]


def require_admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    return None


@app.context_processor
def inject_common():
    return {
        "categories": [
            "Автозапчасти",
            "Шины и диски",
            "Масла и жидкости",
            "Аккумуляторы",
            "Тормозные колодки",
        ],
        "cart_count": sum(item["qty"] for item in get_cart_items()),
        "cart_total": get_cart_total(),
    }


@app.route("/")
def index():
    featured = get_products(limit=8)
    popular_categories = [
        {
            "name": "Тормозная система",
            "count": 2345,
            "image": "/static/images/categories/brakes.jpg",
        },
        {
            "name": "Фильтры",
            "count": 1890,
            "image": "/static/images/categories/filters-photo.jpg",
        },
        {
            "name": "Подвеска",
            "count": 3120,
            "image": "/static/images/categories/suspension.jpg",
        },
        {
            "name": "Система зажигания",
            "count": 1260,
            "image": "/static/images/categories/spark-plug-single.jpg",
        },
        {
            "name": "Дворники",
            "count": 760,
            "image": "/static/images/categories/wipers.jpg",
        },
    ]
    return render_template("index.html", featured=featured, popular_categories=popular_categories)


@app.route("/catalog")
def catalog():
    category = request.args.get("category", "all")
    brand = request.args.get("brand", "all")
    min_price = request.args.get("min_price", 0, type=int)
    max_price = request.args.get("max_price", 50000, type=int)
    search = request.args.get("search", "")

    products = get_products(
        category=category,
        min_price=min_price,
        max_price=max_price,
        search=search,
        brand=brand,
    )
    brands = get_brands()
    return render_template(
        "catalog.html",
        products=products,
        brands=brands,
        selected_category=category,
        selected_brand=brand,
        search=search,
        min_price=min_price,
        max_price=max_price,
    )


@app.route("/product/<int:product_id>")
def product(product_id):
    product_data = get_product_by_id(product_id)
    related = get_products(limit=4)
    if not product_data:
        flash("Товар не найден")
        return redirect(url_for("catalog"))
    return render_template("product.html", product=product_data, related=related)


@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    quantity = int(request.form.get("quantity", 1))
    cart = session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    session["cart"] = cart
    flash("Товар добавлен в корзину")
    return redirect(request.referrer or url_for("catalog"))


@app.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    flash("Товар удален из корзины")
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    items = get_cart_items()
    total = get_cart_total()
    delivery = 200 if total and total < 5000 else 0
    grand_total = total + delivery
    return render_template("cart.html", items=items, total=total, delivery=delivery, grand_total=grand_total)


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = get_cart_items()
    if request.method == "POST":
        if not items:
            flash("Корзина пуста")
            return redirect(url_for("cart"))

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (customer_name, customer_phone, customer_email, delivery_address, comment, total) VALUES (?, ?, ?, ?, ?, ?)",
            (
                request.form.get("name"),
                request.form.get("phone"),
                request.form.get("email"),
                request.form.get("address"),
                request.form.get("comment"),
                get_cart_total(),
            ),
        )
        order_id = cur.lastrowid

        for item in items:
            cur.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                (order_id, item["id"], item["qty"], item["price"]),
            )

        conn.commit()
        conn.close()

        session["cart"] = {}
        flash("Заказ оформлен успешно")
        return redirect(url_for("checkout_success", order_id=order_id))

    total = get_cart_total()
    delivery = 200 if total and total < 5000 else 0
    return render_template("checkout.html", items=items, total=total, delivery=delivery, grand_total=total + delivery)


@app.route("/checkout_success/<int:order_id>")
def checkout_success(order_id):
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    items = conn.execute(
        "SELECT oi.*, p.name, p.image_url FROM order_items oi JOIN products p ON p.id = oi.product_id WHERE oi.order_id = ?",
        (order_id,),
    ).fetchall()
    conn.close()
    return render_template("checkout_success.html", order=dict(order) if order else None, items=items)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        expected_username = os.environ.get("ADMIN_USERNAME")
        expected_password = os.environ.get("ADMIN_PASSWORD")
        if (
            expected_username
            and expected_password
            and username
            and password
            and hmac.compare_digest(username, expected_username)
            and hmac.compare_digest(password, expected_password)
        ):
            session["admin_logged_in"] = True
            flash("Успешный вход в админку")
            return redirect(url_for("admin_panel"))
        if not expected_username or not expected_password:
            flash("Вход в админку не настроен. Установите ADMIN_USERNAME и ADMIN_PASSWORD.")
        else:
            flash("Неверный логин или пароль")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Вы вышли из админки")
    return redirect(url_for("admin_login"))


@app.route("/admin")
def admin_panel():
    redirect_result = require_admin()
    if redirect_result:
        return redirect_result

    products = get_products()
    return render_template("admin.html", products=products)


@app.route("/admin/add_product", methods=["POST"])
def add_product():
    redirect_result = require_admin()
    if redirect_result:
        return redirect_result

    product_name = request.form.get("name").strip()
    slug = request.form.get("slug").strip() or product_name.lower().replace(" ", "-")
    category = request.form.get("category")
    brand = request.form.get("brand")
    price = int(request.form.get("price", 0))
    old_price = int(request.form.get("old_price") or price)
    stock = int(request.form.get("stock", 0))
    description = request.form.get("description", "")
    short_description = request.form.get("short_description") or description[:120]
    image_url = request.form.get("image_url") or ""
    specs = {
        "Производитель": brand,
        "Категория": category,
        "Гарантия": request.form.get("warranty", "12 месяцев"),
    }

    conn = get_db()
    conn.execute(
        """
        INSERT INTO products (
            name, slug, category, brand, price, old_price, stock,
            description, short_description, specifications, image_url, gallery,
            rating, review_count, featured
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product_name,
            slug,
            category,
            brand,
            price,
            old_price,
            stock,
            description,
            short_description,
            json.dumps(specs, ensure_ascii=False),
            image_url,
            json.dumps([image_url], ensure_ascii=False),
            4.7,
            0,
            0,
        ),
    )
    conn.commit()
    conn.close()

    flash("Товар добавлен")
    return redirect(url_for("admin_panel"))


@app.route("/admin/delete_product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    redirect_result = require_admin()
    if redirect_result:
        return redirect_result

    conn = get_db()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    flash("Товар удален")
    return redirect(url_for("admin_panel"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    init_db()
    app.run(
        debug=os.environ.get("FLASK_DEBUG") == "1",
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
    )
