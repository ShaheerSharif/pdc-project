from flask import Flask, render_template, request, redirect, url_for, session, jsonify

import json

app = Flask(__name__)
app.secret_key = "supersecretkey"

inventory = []
orders = []
users = []
cart = []

INVENTORY_FILE_PATH = "db/inventory.json"
ORDERS_FILE_PATH = "db/orders.json"
USERS_FILE_PATH = "db/users.json"


@app.route("/admin")
def admin():
    if "user" not in session and not session.get("is_admin"):
        return jsonify({"message": "Log in first"}), 401

    return render_template("admin/index.html", inventory=inventory)


@app.route("/", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = get_users()

        user = next(
            (
                user
                for user in users
                if user["username"] == username and user["password"] == password
            ),
            None,
        )

        if user is None:
            return jsonify({"message": "Unknown username or password"}), 404

        elif user["username"] == "admin":
            session["user"] = user["username"]
            session["is_admin"] = True
            return redirect(url_for("admin"))

        else:
            session["user"] = user["username"]
            session["is_admin"] = False
            return redirect(url_for("shop"))

    return render_template("signin.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = get_users()

        # Check if user already exists
        if any(user["username"] == username for user in users):
            return jsonify({"message": "Pick another username"}), 402

        users.append({"username": username, "password": password})
        set_users(users)
        return redirect(url_for("signin"))

    return render_template("signup.html")


@app.route("/view-inv")
def view_item():
    if "user" not in session and not session.get("is_admin"):
        return jsonify({"message": "Log in first"}), 401

    inventory = get_inventory()
    return render_template("admin/items/view-item.html", inventory=inventory)


@app.route("/add-inv", methods=["GET", "POST"])
def add_item():
    if "user" not in session and not session.get("is_admin"):
        return jsonify({"message": "Log in first"}), 401

    if request.method == "POST":
        (name, quantity, price) = get_request_info()

        inventory = get_inventory()
        inventory.append({"name": name, "quantity": quantity, "price": price})
        set_inventory(inventory)

        return redirect(url_for("view_item"))
    return render_template("admin/items/add-item.html")


@app.route("/update-inv/<int:item_id>", methods=["GET", "POST"])
def update_item(item_id):
    if "user" not in session and not session.get("is_admin"):
        return jsonify({"message": "Log in first"}), 401

    inventory = get_inventory()

    if request.method == "POST":
        (name, quantity, price) = get_request_info()

        inventory[item_id] = {"name": name, "quantity": quantity, "price": price}

        set_inventory(inventory)

        return redirect(url_for("view_item"))

    item = inventory[item_id]
    return render_template("admin/items/update-item.html", item=item, item_id=item_id)


@app.route("/delete-inv/<int:item_id>")
def delete_item(item_id):
    if "user" not in session and not session.get("is_admin"):
        return jsonify({"message": "Log in first"}), 401

    inventory = get_inventory()
    inventory.pop(item_id)
    set_inventory(inventory)

    return redirect(url_for("view_item"))


@app.route("/shop")
def shop():
    inventory = get_inventory()
    return render_template("customer/shop.html", inventory=inventory)


@app.route("/add-to-cart", methods=["GET", "POST"])
def add_to_cart():
    if "user" not in session:
        return redirect(url_for("signin"))

    cart = get_session_cart()

    inventory = get_inventory()
    (item_names, _, _) = get_request_info()

    if item_names is None:
        return jsonify({"message": "Product not found"}), 404

    item = next((i for i in inventory if i["name"] == item_names), None)

    if item:
        if cart:
            cart_item = next((i for i in cart if i["name"] == item_names), None)
            if cart_item:
                cart_item["quantity"] += 1
            else:
                cart.append(
                    {"name": item["name"], "quantity": 1, "price": item["price"]}
                )

    set_session_cart(cart)

    return redirect(url_for("shop"))


@app.route("/cart")
def view_cart():
    if "user" not in session:
        return redirect(url_for("signin"))

    cart = get_session_cart()
    total = sum(item["price"] * item["quantity"] for item in cart) if cart else 0

    return render_template("customer/cart.html", cart=cart, total=total)


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user" not in session:
        return redirect(url_for("signin"))

    cart = get_session_cart()
    inventory = get_inventory()

    if cart:
        total = sum(item["price"] * item["quantity"] for item in cart)

        for cart_item in cart:
            inventory_item = next(
                (item for item in inventory if item["name"] == cart_item["name"]), None
            )

            if inventory_item:
                inventory_item["quantity"] -= cart_item["quantity"]

        set_inventory(inventory)

    session.pop("cart", None)
    return render_template("customer/checkout.html", cart=cart, total=total)


@app.route("/logout")
def logout():
    session["cart"] = []
    session["is_admin"] = False
    session.pop("user", None)
    return redirect(url_for("signin"))


def get_request_info():
    return (
        request.form["name"],
        int(request.form["quantity"]),
        round(float(request.form["price"]), 2),
    )


def get_inventory():
    try:
        with open(INVENTORY_FILE_PATH, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def set_inventory(inventory):
    with open(INVENTORY_FILE_PATH, "w") as file:
        json.dump(inventory, file, indent=4)


def get_users():
    try:
        with open(USERS_FILE_PATH, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def set_users(users):
    with open(USERS_FILE_PATH, "w") as file:
        json.dump(users, file, indent=4)


def get_session_cart():
    return session.get("cart", [])


def set_session_cart(cart):
    session["cart"] = cart


if __name__ == "__main__":
    app.run()
