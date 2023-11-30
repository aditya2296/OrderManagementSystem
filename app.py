from flask import Flask, render_template, request, flash, redirect, url_for
from validators import generate_secret_key
import pandas as pd
from models import Customer, db

app = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customer.db'  # Use your actual database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = generate_secret_key()
valid_credentials = {'pmadmin': 'pass123'}
test_credentials = {'pmtest': 'pass123'}
item_detail = []
customer_detail = []
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    login_id = request.form.get('loginId')
    password = request.form.get('password')
    if login_id in valid_credentials and password == valid_credentials[login_id]:
        return redirect(url_for('dashboard'))
    elif login_id in test_credentials and password == test_credentials[login_id]:
        return redirect(url_for('order_booking'))
    else:
        flash('Invalid username or password.', 'error')
        return render_template('login.html', error='Invalid username or password.')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/item_details')
def item_details():
    return render_template('item_details.html', item_details=item_detail)

@app.route('/customer_details')
def customer_details():
    customers = Customer.query.all()
    return render_template('customer_details.html', customer_details=customers)

@app.route('/new_item')
def new_item():
    return render_template('new_item.html')

@app.route('/save_new_item', methods=['POST'])
def save_new_item():
    newItemDate = request.form.get('newItemDate')
    newItemName = request.form.get('newItemName')
    newItemCompany = request.form.get('newItemCompany')
    newItemQuantity = request.form.get('newItemQuantity')
    newItemPrice = request.form.get('newItemPrice')
    newItemDiscount = request.form.get('newItemDiscount')

    new_item = {
        'Date of Purchase': newItemDate,
        'Item Name': newItemName,
        'Company Name': newItemCompany,
        'Quantity': int(newItemQuantity),
        'Price': int(newItemPrice),
        'Discount': int(newItemDiscount)
    }
    item_detail.append(new_item)

    return 'OK', 200
@app.route('/insert_excel_page')
def insert_excel_page():
    return render_template('insert_excel_page.html')

@app.route('/insert_from_excel', methods=['POST'])
def insert_from_excel():
    try:
        if 'file' not in request.files:
            return 'No file part', 400

        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        if not file.filename.endswith('.xlsx'):
            return 'Invalid file format. Please upload an Excel file (.xlsx)', 400
        df = pd.read_excel(file)
        new_items = df.iloc[:, :].to_dict(orient='records')
        item_detail.extend(new_items)
        file.close
        return render_template('item_details.html', item_details=item_detail)

    except Exception as e:
        return str(e), 500
    
@app.route('/new_customer')
def new_customer():
    return render_template('new_customer.html')

@app.route('/save_new_customer', methods=['POST'])
def save_new_customer():
    newCustomerName = request.form.get('newCustomerName')
    newCustomerLocation = request.form.get('newCustomerLocation')
    newPhoneNumber = request.form.get('newPhoneNumber')
    newCustomerEmail = request.form.get('newCustomerEmail')
    customerBillingType = request.form.get('CustomerBillingType')
    customerDeliveryType = request.form.get('CustomerDeliveryType')
    customerRoute = request.form.get('Route')

    new_customer = Customer(customer_name=newCustomerName, customer_location = newCustomerLocation, customer_phone_number = newPhoneNumber, customer_email=newCustomerEmail, customer_billing_type = customerBillingType, customer_delivery_type = customerDeliveryType, customer_route = customerRoute)
    db.session.add(new_customer)
    db.session.commit()

    return 'OK', 200

@app.route('/insert_customer_page')
def insert_customer_page():
    return render_template('insert_customer_page.html')

@app.route('/insert_from_excel_customer', methods=['POST'])
def insert_from_excel_customer():
        try:
            if 'file' not in request.files:
                return 'No file part', 400

            file = request.files['file']
            df = pd.read_excel(file)

            for index, row in df.iterrows():
                new_customer = Customer(
                    customer_name=row['Customer_Name'],
                    customer_location=row['Location'],
                    customer_phone_number=row['Mobile_Number'],
                    customer_email=row['Email'],
                    customer_billing_type=row['Billing_Type'],
                    customer_delivery_type=row['Delivery_Type'],
                    customer_route=row['Route']
                )
                db.session.add(new_customer)
            db.session.commit()
            file.close
            return redirect(url_for('customer_details'))
        except Exception as e:
            return str(e), 500

@app.route('/order_booking')
def order_booking():
    return render_template('order_booking.html')

@app.route('/new_order')
def new_order():
    return render_template('new_order.html')

@app.route('/edit_customer/<string:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    original_id = customer_id
    if request.method == 'POST':
        customer.customer_name = request.form.get('newCustomerName')
        customer.customer_location = request.form.get('newCustomerLocation')
        customer.customer_phone_number = request.form.get('newPhoneNumber')
        customer.customer_email = request.form.get('newCustomerEmail')
        customer.customer_billing_type = request.form.get('CustomerBillingType')
        customer.customer_delivery_type = request.form.get('CustomerDeliveryType')
        customer.customer_route = request.form.get('Route')
        customer.id = original_id
        db.session.commit()
        return redirect(url_for('customer_details'))

        ## update_customer_in_database(customer_id, customer_name, customer_location, customer_phone, customer_email, customer_billing_type, customer_delivery_type, customer_route)
        ## return redirect(url_for('customer_details'))
    return render_template('edit_customer.html', customer=customer)

@app.route('/delete_customer/<string:customer_id>', methods=['GET', 'POST'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for('customer_details'))

if __name__ == '__main__':
    app.run(debug=True)
