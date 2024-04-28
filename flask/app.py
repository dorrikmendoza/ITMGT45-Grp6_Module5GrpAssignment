from flask import Flask,redirect
from flask import render_template
from flask import request
from flask import session
from flask import flash
import database as db
import authentication
import logging
import ordermanagement as om

app = Flask(__name__)

# Set the secret key to some random bytes.
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/past_orders')
def past_orders():
    if 'user' not in session or 'id' not in session['user']:
        flash('You must be logged in to view this page.')
        return render_template('login.html')

    user_id = session['user']['id']
    orders = db.orders.find({'user_id': user_id})
    return render_template('past_orders.html', orders=list(orders))

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')
    is_successful, response = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if is_successful:
        session["user"] = response  # Assuming response here is the user object
        return redirect('/')
    else:
        error_message = "Invalid username or password. Please try again."
        return render_template('login.html', error=error_message)

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')


@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()
    # A click to add a product translates to a
    # quantity of 1 for now

    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/updatecart', methods=['POST'])
def update_cart():
    if 'cart' not in session or session['cart'] is None:
        flash('There are no items in your cart to update.', 'info')
        return redirect('/cart')

    try:
        for item_code in list(session['cart'].keys()):
            form_key = f"quantity-{item_code}"
            if form_key in request.form:
                new_qty = int(request.form[form_key])
                if new_qty > 0:
                    session['cart'][item_code]['qty'] = new_qty
                else:
                    del session['cart'][item_code]  # Remove item if quantity is 0 or negative
    except ValueError:
        flash('Invalid quantity provided. Please enter a valid number.', 'error')

    return redirect('/cart')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))
    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")
