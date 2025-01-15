from os import read
from flask import Flask, render_template, request, redirect, url_for, flash

import json

app = Flask(__name__)

# Sample data structure to hold inventory items
inventory = []

INVENTORY_FILE_PATH = "db/inventory.json"
ORDERS_FILE_PATH = "db/orders.json"
USERS_FILE_PATH = "db/users.json"


def read_inventory():
    try:
        with open(INVENTORY_FILE_PATH, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_inventory(inventory):
    with open(INVENTORY_FILE_PATH, "w") as file:
        json.dump(inventory, file, indent=4)


def read_users():
    try:
        with open(USERS_FILE_PATH, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_users(users):
    with open(USERS_FILE_PATH, "w") as file:
        json.dump(users, file, indent=4)


def get_inventory_info():
    return (
        request.form["name"],
        int(request.form["quantity"]),
        round(float(request.form["price"]), 2),
    )


def get_order_info():
    return (
        request.form["name"],
        [tuple(request.form["products"])],
        request.form["date"],
    )


@app.route("/", method=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = read_users()
        user = next(
            (
                user
                for user in users
                if user["username"] == username and user["password"] == password
            ),
            None,
        )

    if user:
        flash("Sign-in successful!", "success")
        return redirect(url_for("signin"))  # Redirect to a dashboard or homepage
    else:
        flash("Invalid username or password!", "error")
        return redirect(url_for("signin"))

    return render_template("signin.html")


@app.route("/add-inv", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        (name, quantity, price) = get_inventory_info()

        inventory = read_inventory()
        inventory.append({"name": name, "quantity": quantity, "price": price})
        save_inventory(inventory)

        return redirect(url_for("admin/index"))
    return render_template("admin/add-item.html")


@app.route("/update-inv/<int:item_id>", methods=["GET", "POST"])
def update_item(item_id):
    inventory = read_inventory()

    if request.method == "POST":
        (name, quantity, price) = get_inventory_info()

        inventory[item_id] = {"name": name, "quantity": quantity, "price": price}

        save_inventory(inventory)

        return redirect(url_for("admin/index"))

    item = inventory[item_id]
    return render_template("admin/update-item.html", item=item, item_id=item_id)


@app.route("/delete-inv/<int:item_id>")
def delete_item(item_id):
    inventory = read_inventory()
    inventory.pop(item_id)
    save_inventory(inventory)

    return redirect(url_for("admin/index"))


@app.route("/logout")
def logout():
    return redirect(url_for("signin"))


if __name__ == "__main__":
    app.run(debug=True)
