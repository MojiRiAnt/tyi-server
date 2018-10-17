from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

_STRING_SIZE = 16


class Foodstuff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(_STRING_SIZE), nullable=False)
    amount = db.Column(db.Integer, nullable=False, default=1)
    #measurement units
    expiry = db.Column(db.Date, nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), default=-1)
    warehouse = db.relationship('Warehouse', backref=db.backref('foodstuffs', lazy=True))

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(_STRING_SIZE), nullable=False)
    category = db.Column(db.String(_STRING_SIZE), nullable=False, default='Undefined')
    ingredients = db.Column(db.String(_STRING_SIZE), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ready = db.Column(db.Boolean, nullable=False, default=False)
    dish = db.Column(db.String(_STRING_SIZE), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), default=-1)
    employee = db.relationship('Employee', backref=db.backref('orders', lazy=True))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), default=-1)
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    info = db.Column(db.String(_STRING_SIZE), nullable=False)
    #coords
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), default=-1)
    driver = db.relationship('Driver', backref=db.backref('deliveries', lazy=True))

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    info = db.Column(db.String(_STRING_SIZE), nullable=False)
    #coords
    #orders <- Order

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(_STRING_SIZE), nullable=False, unique=True)
    password = db.Column(db.String(_STRING_SIZE), nullable=False)
    permissions = db.Column(db.Integer, nullable=False, default=0)
    name = db.Column(db.String(_STRING_SIZE), nullable=False, default="NoName")
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafe.id'), default=-1)
    cafe = db.relationship('Cafe', backref=db.backref('employees', lazy=True))
    #orders <- Order

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(_STRING_SIZE), nullable=False, unique=True)
    password = db.Column(db.String(_STRING_SIZE), nullable=False)
    name = db.Column(db.String(_STRING_SIZE), nullable=False, default="NoName")
    #coords
    #deliveries <- Delivery

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #coords
    #employees <- Employee

class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #coords
    #foodstuffs <- Foodstuff


