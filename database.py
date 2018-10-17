from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

_STRING_SIZE = 16 # WARNING : to be deprecated
_LOGIN_SIZE = 16
_NAME_SIZE = 16
_PASSWORD_SIZE = 16
_CATEGORY_SIZE = 16
_TEXT_SIZE = 512
_PATH_SIZE = 32
_MEAS_UNIT_SIZE = 8

Role = {"cook":(1<<0), "operator":(1<<1), "manager":(1<<2), "admin":(1<<3),}

class Foodstuff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(_NAME_SIZE), nullable=False)
    amount = db.Column(db.Integer, nullable=False, default=1)
    #measurement units
    expiry = db.Column(db.Date, nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouse.id'), default=-1)
    warehouse = db.relationship('Warehouse', backref=db.backref('foodstuffs', lazy=True))

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(_NAME_SIZE), nullable=False)
    category = db.Column(db.String(_CATEGORY_SIZE), nullable=False, default='Undefined')
    price = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    measurement_unit = db.Column(db.String(_MEAS_UNIT_SIZE), nullable=False)
    ingredients = db.Column(db.String(_TEXT_SIZE), nullable=False)
    description = db.Column(db.String(_TEXT_SIZE), nullable=False)
    #image = db.Column(db.String(_PATH_SIZE), nullable=False, default="resources/public/unknown-dish.png")

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ready = db.Column(db.Boolean, nullable=False, default=False)
    dish = db.Column(db.String(_NAME_SIZE), nullable=False)
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
    login = db.Column(db.String(_LOGIN_SIZE), nullable=False, unique=True)
    password = db.Column(db.String(_PASSWORD_SIZE), nullable=False)
    permission = db.Column(db.Integer, nullable=False, default=0)
    name = db.Column(db.String(_NAME_SIZE), nullable=False, default="NoName")
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafe.id'), default=-1)
    cafe = db.relationship('Cafe', backref=db.backref('employees', lazy=True))
    #orders <- Order

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(_LOGIN_SIZE), nullable=False, unique=True)
    password = db.Column(db.String(_PASSWORD_SIZE), nullable=False)
    name = db.Column(db.String(_NAME_SIZE), nullable=False, default="NoName")
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


