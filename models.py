# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String(255))
    customer_location = db.Column(db.String(255))
    customer_phone_number = db.Column(db.Integer)
    customer_email = db.Column(db.String(255))
    customer_billing_type = db.Column(db.String(255))
    customer_delivery_type = db.Column(db.String(255))
    customer_route = db.Column(db.String(255))

    def __repr__(self):
        return f"<Customer {self.id}: {self.name}>"

def init_db(app):
    # Initialize the database with the Flask app
    db.init_app(app)

    # Create tables
    with app.app_context():
        db.create_all()

# Other model definitions and configurations...
