from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

login_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>EcoFinds Login</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      margin: 0;
      font-family: Arial, sans-serif;
      background-color: #f5f7fa;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    .container {
      display: flex;
      width: 800px;
      height: 500px;
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      overflow: hidden;
      background: white;
    }
    .left {
      flex: 1;
      background: white;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      padding: 40px;
    }
    .left img {
      width: 120px;
      margin-bottom: 20px;
    }
    .left h2 {
      color: #2e7d32;
      margin-bottom: 10px;
    }
    .left p {
      color: #555;
    }
    .right {
      flex: 1.2;
      background: #a5d6a7;
      padding: 40px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
    .right h3 {
      color: #333;
      margin-bottom: 20px;
      text-align: center;
    }
    form {
      display: flex;
      flex-direction: column;
    }
    label {
      margin-bottom: 5px;
      font-weight: bold;
      font-size: 14px;
    }
    input {
      margin-bottom: 15px;
      padding: 12px;
      border: none;
      border-radius: 8px;
      font-size: 14px;
    }
    .options {
      display: flex;
      justify-content: flex-end;
      margin-bottom: 15px;
    }
    .options a {
      font-size: 14px;
      color: #1b5e20;
      text-decoration: none;
    }
    .btn {
      padding: 12px;
      background: #1b5e20;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 16px;
      margin-bottom: 10px;
    }
    .btn:hover {
      background: #124d16;
    }
    .signup {
      margin-top: 15px;
      text-align: center;
      font-size: 14px;
    }
    .signup a {
      color: #1b5e20;
      text-decoration: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="left">
      <img src="{{ url_for('static', filename='img1.jpg') }}" alt="EcoFinds Logo">
      <h2>EcoFinds</h2>
      <p>Shop Smart. Live Green</p>
    </div>
    <div class="right">
      <h3>Welcome Back</h3>
      <form method="POST">
        <label for="email">Username or Email</label>
        <input type="email" id="email" name="email" placeholder="you@example.com" required>
        <label for="password">Password</label>
        <input type="password" id="password" name="password" placeholder="••••••••" required>
        <div class="options">
          <a href="#">Forgot password?</a>
        </div>
        <button type="submit" class="btn">Sign In</button>
      </form>
      <div class="signup">
        New to EcoFinds? <a href="#">Create Account</a>
      </div>
    </div>
  </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # TODO: add authentication logic
        return redirect(url_for('dashboard'))
    return render_template_string(login_html)

@app.route('/dashboard')
def dashboard():
    return "<h1>Welcome to EcoFinds Dashboard!</h1>"

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="ECO_FINDS"
)
cursor = db.cursor()

# Create tables if not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    category VARCHAR(100),
    description TEXT,
    price DECIMAL(10,2),
    quantity INT,
    condition VARCHAR(50),
    image VARCHAR(255),
    seller_id INT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS purchases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    user_id INT,
    quantity INT,
    total DECIMAL(10,2)
)
""")
db.commit()

# ----------------------- Routes -----------------------

@app.route('/')
def landingpage():
    cursor.execute("SELECT * FROM products ORDER BY id DESC LIMIT 6")
    products = cursor.fetchall()
    return render_template('landingpage.html', products=products)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('userdash'))
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cursor.execute("INSERT INTO users (username,email,password) VALUES (%s,%s,%s)", (username,email,password))
        db.commit()
        flash("Signup successful! Login now.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/userdash')
def userdash():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM products WHERE seller_id=%s", (session['user_id'],))
    my_products = cursor.fetchall()
    return render_template('userdash.html', products=my_products)

@app.route('/listing')
def listing():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('listing.html', products=products)

@app.route('/addproduct', methods=['GET','POST'])
def addproduct():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        description = request.form['description']
        price = request.form['price']
        quantity = request.form['quantity']
        condition = request.form['condition']
        image_file = request.files['product-image']
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor.execute("""
            INSERT INTO products (title,category,description,price,quantity,condition,image,seller_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """,(title,category,description,price,quantity,condition,filename,session['user_id']))
        db.commit()
        flash("Product added successfully!", "success")
        return redirect(url_for('userdash'))
    return render_template('addproduct.html')

@app.route('/productdetails/<int:product_id>')
def productdetails(product_id):
    cursor.execute("SELECT * FROM products WHERE id=%s", (product_id,))
    product = cursor.fetchone()
    return render_template('productdetails.html', product=product)

@app.route('/cart')
def cart():
    # Placeholder: Fetch cart items for logged in user
    return render_template('cart.html')

@app.route('/purchase/<int:product_id>', methods=['POST'])
def purchase(product_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    quantity = int(request.form['quantity'])
    cursor.execute("SELECT price FROM products WHERE id=%s", (product_id,))
    price = cursor.fetchone()[0]
    total = price * quantity
    cursor.execute("INSERT INTO purchases (product_id,user_id,quantity,total) VALUES (%s,%s,%s,%s)",
                   (product_id, session['user_id'], quantity, total))
    db.commit()
    flash("Purchase successful!", "success")
    return redirect(url_for('userdash'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landingpage'))

# ----------------------- Run App -----------------------
if __name__ == "__main__":
    app.run(debug=True)
