from flask import Flask, render_template, request, redirect, url_for

import json

app = Flask(__name__)

# Sample data structure to hold inventory items
inventory = []

JSON_FILE_PATH="inventory.json"


def get_table_info():
    return (request.form["name"], int(request.form["quantity"]), round(float(request.form["price"]), 2))


def read_inventory():
    try:
        with open(JSON_FILE_PATH, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_inventory(inventory):
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(inventory, file, indent=4)



@app.route('/')
def index():
    inventory = read_inventory()
    return render_template('index.html', inventory=inventory)


@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        # item_name = request.form['name']
        # item_quantity = request.form['quantity']
        # item_price = request.form['price']

        (name, quantity, price) = get_table_info()

        inventory = read_inventory()
        inventory.append({'name': name, 'quantity': quantity, 'price': price})
        save_inventory(inventory)
        
        return redirect(url_for('index'))
    return render_template('add-item.html')


@app.route('/update/<int:item_id>', methods=['GET', 'POST'])
def update_item(item_id):
    inventory = read_inventory()

    if request.method == 'POST':
        # name = request.form['name']
        # quantity = int(request.form['quantity'])
        # price = float(request.form['price'])

        (name, quantity, price) = get_table_info()

        inventory[item_id] = {'name': name, 'quantity': quantity, 'price': price}

        save_inventory(inventory)

        return redirect(url_for('index'))

    item = inventory[item_id]
    return render_template('update-item.html', item=item, item_id=item_id)



@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    inventory = read_inventory()
    inventory.pop(item_id)
    save_inventory(inventory)

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
