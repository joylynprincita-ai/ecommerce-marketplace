from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Create Database
def create_database():
    conn = sqlite3.connect('database.db')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER,
        name TEXT,
        price REAL,
        description TEXT
    )
    ''')

    conn.commit()
    conn.close()

create_database()


# Home Page
@app.route('/')
def home():
    return render_template('home.html')


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        conn = sqlite3.connect('database.db')

        conn.execute(
            "INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
            (name, email, password, role)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            if user[4] == "Vendor":
                return redirect('/vendor-dashboard')

            elif user[4] == "Customer":
                return redirect('/customer-dashboard')

        else:
            return "Invalid Email or Password"

    return render_template('login.html')


# Vendor Dashboard
@app.route('/vendor-dashboard')
def vendor_dashboard():
    return render_template('vendor_dashboard.html')


# Add Product
@app.route('/add-product', methods=['GET', 'POST'])
def add_product():

    if request.method == 'POST':

        product_name = request.form['name']
        price = request.form['price']
        description = request.form['description']

        conn = sqlite3.connect('database.db')

        conn.execute(
            "INSERT INTO products(vendor_id,name,price,description) VALUES(?,?,?,?)",
            (1, product_name, price, description)
        )

        conn.commit()
        conn.close()

        return "Product Added Successfully!"

    return render_template('add_product.html')


# View Products
@app.route('/view-products')
def view_products():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template('view_products.html', products=products)


@app.route('/delete-product/<int:id>')
def delete_product(id):

    conn = sqlite3.connect('database.db')

    conn.execute(
        "DELETE FROM products WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/view-products')

@app.route('/customer-dashboard')
def customer_dashboard():
    return render_template('customer_dashboard.html')


@app.route('/customer-products')
def customer_products():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template(
        'customer_products.html',
        products=products
    )
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)