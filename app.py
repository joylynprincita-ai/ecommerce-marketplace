from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "ecommerce_secret_key"

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

            session['user_id'] = user[0]
            session['role'] = user[4]

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

    if 'user_id' not in session:
        return redirect('/login')

    return render_template('vendor_dashboard.html')


# Add Product
@app.route('/add-product', methods=['GET', 'POST'])
def add_product():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        product_name = request.form['name']
        price = request.form['price']
        description = request.form['description']

        conn = sqlite3.connect('database.db')

        conn.execute(
            "INSERT INTO products(vendor_id,name,price,description) VALUES(?,?,?,?)",
            (session['user_id'], product_name, price, description)
        )

        conn.commit()
        conn.close()

        return redirect('/view-products')

    return render_template('add_product.html')


# View Products
@app.route('/view-products')
def view_products():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    return render_template('view_products.html', products=products)


@app.route('/delete-product/<int:id>')
def delete_product(id):

    if 'user_id' not in session:
        return redirect('/login')

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

    if 'user_id' not in session:
        return redirect('/login')

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

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)