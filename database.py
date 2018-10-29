from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from string import ascii_letters, digits
import random

db = SQLAlchemy()

def randStr(length, charset):
    return ''.join(random.choice(charset) for _ in range(length))

_NAME_SIZE = 32
_NUMBER_SIZE = 16
_ORDERNUMBER_SIZE = 8
_CODE_SIZE = 16
_TEXT_SIZE = 128
_ADDRESS_SIZE = 32
_FILEPATH_SIZE = 16
_MEAS_SIZE = 4
_PHONE_SIZE = 16
_EMAIL_SIZE = 16
_TOKEN_SIZE = 16
_DATE_SIZE = 16
_SECRET_SIZE = 4
_DISHESLIST_SIZE = 256
#_PASSWORD_SIZE = 32

Role = {'Cook' : (1<<0), 'Operator' : (1<<1), 'Manager' : (1<<2), 'Admin' : (1<<3)}

#================[ORDERS MANAGEMENT]==============

class Maybeorder(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    number          = db.Column(db.String(_ORDERNUMBER_SIZE), nullable=False)
    address         = db.Column(db.String(_ADDRESS_SIZE), nullable=False)
    client_id       = db.Column(db.Integer, db.ForeignKey('client.id'), default=-1)
    client          = db.relationship('Client', backref=db.backref('maybeorders'), lazy=True)
    dishes          = db.Column(db.String(_DISHESLIST_SIZE), nullable=False)
    #number          = db.Column(db.String(_))

class Order(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    number          = db.Column(db.String(_ORDERNUMBER_SIZE), nullable=False)
    address         = db.Column(db.String(_ADDRESS_SIZE), nullable=False)
    client_id       = db.Column(db.Integer, db.ForeignKey('client.id'), default=-1)
    client          = db.relationship('Client', backref=db.backref('orders'), lazy=True)
    dishes          = db.Column(db.String(_DISHESLIST_SIZE), nullable=False)
    cafe_id         = db.Column(db.Integer, db.ForeignKey('cafe.id'), default=-1)
    cafe            = db.relationship('Cafe', backref=db.backref('orders'), lazy=True)

    @classmethod
    def newNumber(cls):
        res = randStr(_NUMBER_SIZE, digits)
        while Maybeorder.query.filter_by(number=res).first() is not None and Order.query.filter_by(number=res).first() is not None and Delivery.query.filter_by(number=res).first() is not None:
            res = randStr(_NUMBER_SIZE, digits)
        return res

class Delivery(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    number          = db.Column(db.String(_ORDERNUMBER_SIZE), nullable=False)
    address         = db.Column(db.String(_ADDRESS_SIZE), nullable=False)
    client_id       = db.Column(db.Integer, db.ForeignKey('client.id'), default=-1)
    client          = db.relationship('Client', backref=db.backref('deliveries'), lazy=True)
    dishes          = db.Column(db.String(_DISHESLIST_SIZE), nullable=False)
    cafe_id         = db.Column(db.Integer, db.ForeignKey('cafe.id'), default=-1)
    cafe            = db.relationship('Cafe', backref=db.backref('deliveries'), lazy=True)
    driver_id       = db.Column(db.Integer, db.ForeignKey('driver.id'), default=-1)
    driver          = db.relationship('Driver', backref=db.backref('deliveries'), lazy=True)

class Archivedorder(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    address         = db.Column(db.String(_ADDRESS_SIZE), nullable=False)
    client_id       = db.Column(db.Integer, db.ForeignKey('client.id'), default=-1)
    client          = db.relationship('Client', backref=db.backref('archivedorders'), lazy=True)
    dish_id         = db.Column(db.Integer, db.ForeignKey('dish.id'), default=-1)
    dish            = db.relationship('Dish', backref=db.backref('archivedorders'), lazy=True)
    money           = db.Column(db.Integer, nullable=False)

#================[USERS MANAGEMENT]===============

class Emptyclient(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    phone           = db.Column(db.String(_PHONE_SIZE), nullable=False, unique=True)
    secret          = db.Column(db.String(_SECRET_SIZE), nullable=False)
    registered_date = db.Column(db.String(_DATE_SIZE), default=datetime.now().strftime('%Y-%m-%d'))
    
class Client(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    phone           = db.Column(db.String(_PHONE_SIZE), nullable=False, unique=True)
    secret          = db.Column(db.String(_SECRET_SIZE), nullable=False)
    name            = db.Column(db.String(_NAME_SIZE), nullable=False)
    email           = db.Column(db.String(_EMAIL_SIZE), nullable=False, default="")
    registered_date = db.Column(db.String(_DATE_SIZE))
    #maybeorders <- Maybeorder
    #orders <- Order
    #deliveries <- Delivery

    @classmethod
    def randSecret(cls):
        return "2705"#randStr(_SECRET_SIZE, digits)

    @classmethod
    def isValidPhone(cls, phone):
        if phone == "":
            return False
        if phone[0] != ' ':
            return False
        return True

    @classmethod
    def isValidName(cls, name):
        if name == "":
            return False
        else:
            return True

    @classmethod
    def isValidEmail(cls, email):
        if email == "":
            return False
        else:
            return True

class Employee(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    login           = db.Column(db.String(_NAME_SIZE), nullable=False)
    #password        = db.Column(db.String(_PASSWORD_SIZE), nullable=False)
    token           = db.Column(db.String(_TOKEN_SIZE), nullable=False)
    phone           = db.Column(db.String(_PHONE_SIZE), nullable=False)
    email           = db.Column(db.String(_EMAIL_SIZE), nullable=False)
    permission      = db.Column(db.Integer, nullable=False)
    registered_date = db.Column(db.String(_DATE_SIZE), default=datetime.now().strftime('%Y-%m-%d'))
    cafe_id         = db.Column(db.Integer, db.ForeignKey('cafe.id'), default=-1)
    cafe            = db.relationship('Cafe', backref=db.backref('employees'), lazy=True)

    @classmethod
    def randToken(cls):
        return randStr(_TOKEN_SIZE, ascii_letters+digits)

class Driver(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    login           = db.Column(db.String(_NAME_SIZE), nullable=False)
    #password        = db.Column(db.String(_PASSWORD_SIZE), nullable=False)
    token           = db.Column(db.String(_TOKEN_SIZE), nullable=False)
    phone           = db.Column(db.String(_PHONE_SIZE), nullable=False)
    email           = db.Column(db.String(_EMAIL_SIZE), nullable=False)
    registered_date = db.Column(db.String(_DATE_SIZE), default=datetime.now().strftime('%Y-%m-%d'))
    #deliveries <- Delivery

#================[FOOD MANAGEMENT]===============

class Shipper(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(_NAME_SIZE), nullable=False)
    contract_number = db.Column(db.String(_NUMBER_SIZE), nullable=False)
    contract_file   = db.Column(db.String(_FILEPATH_SIZE), nullable=False)
    photo           = db.Column(db.String(_FILEPATH_SIZE), nullable=False, default='https://openclipart.org/image/800px/svg_to_png/197967/mono-metacontact-unknown.png')
    phone           = db.Column(db.String(_PHONE_SIZE), nullable=False)
    registered_date = db.Column(db.String(_DATE_SIZE), default=datetime.now().strftime('%Y-%m-%d'))
    #supplies <- Supply

class Invoice(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    number          = db.Column(db.String(_NUMBER_SIZE), nullable=False)
    date            = db.Column(db.String(_DATE_SIZE), default=datetime.now().strftime('%Y-%m-%d'))
    #supplies <- Supply
    shipper_id      = db.Column(db.Integer, db.ForeignKey('shipper.id'), default=-1)
    shipper         = db.relationship('Shipper', backref=db.backref('invoices'), lazy=True)
    cafe_id         = db.Column(db.Integer, db.ForeignKey('cafe.id'), default=-1)
    cafe            = db.relationship('Cafe', backref=db.backref('invoices', lazy=True))

class Supply(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    expiry          = db.Column(db.String, nullable=False)
    amount          = db.Column(db.Integer, nullable=False)
    foodstuff_code  = db.Column(db.String(_CODE_SIZE), db.ForeignKey('foodstuff.code'), default="")
    foodstuff       = db.relationship('Foodstuff', backref=db.backref('supplies'), lazy=True)
    cafe_id         = db.Column(db.Integer, db.ForeignKey('cafe.id'), default=-1)
    cafe            = db.relationship('Cafe', backref=db.backref('supplies'), lazy=True)
    invoice_id      = db.Column(db.Integer, db.ForeignKey('invoice.id'), default=-1)
    invoice         = db.relationship('Invoice', backref=db.backref('supplies'), lazy=True)

class Archivedsupply(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    removal         = db.Column(db.String(_DATE_SIZE), default=datetime.now().strftime('%Y-%m-%d'))
    invoice_number  = db.Column(db.String(_NUMBER_SIZE), nullable=False)
    cafe_name       = db.Column(db.String(_NAME_SIZE), nullable=False)
    foodstuff_code  = db.Column(db.String(_CODE_SIZE), nullable=False)

class Foodstuff(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    code            = db.Column(db.String(_CODE_SIZE), nullable=False)
    name            = db.Column(db.String(_NAME_SIZE), nullable=False)
    photo           = db.Column(db.String(_FILEPATH_SIZE), nullable=False, default='https://s8.hostingkartinok.com/uploads/images/2018/10/fa1c62a1b83af9429b6f567ac818496c.png')
    #supplies <- Supply
    #linkdishes <- Linkdishfoodstuff <- Dish
    measurement_unit= db.Column(db.String(_MEAS_SIZE), db.ForeignKey('measurement.unit'), default="")
    measurement     = db.relationship('Measurement', backref=db.backref('foodstuffs'), lazy=True)

class Linkdishfoodstuff(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    dish_id         = db.Column(db.Integer, db.ForeignKey('dish.id'), default=-1)
    dish            = db.relationship('Dish', backref=db.backref('linkfoodstuffs'), lazy=True)
    foodstuff_code  = db.Column(db.String(_CODE_SIZE), db.ForeignKey('foodstuff.code'), default="")
    foodstuff       = db.relationship('Foodstuff', backref=db.backref('linkdishes'), lazy=True)
    amount          = db.Column(db.Integer, nullable=False)

class Dish(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(_NAME_SIZE), nullable=False)
    description     = db.Column(db.String(_TEXT_SIZE), nullable=False)
    price           = db.Column(db.Integer, nullable=False)
    amount          = db.Column(db.Integer, nullable=False)
    cooking_time    = db.Column(db.Integer, nullable=False)
    photo           = db.Column(db.String(_FILEPATH_SIZE), nullable=False, default='https://s8.hostingkartinok.com/uploads/images/2018/10/fa1c62a1b83af9429b6f567ac818496c.png')
    #linkfoodstuffs <- Linkdishfoodstuff <- Foodstuff
    measurement_unit= db.Column(db.String(_MEAS_SIZE), db.ForeignKey('measurement.unit'), default="")
    measurement     = db.relationship('Measurement', backref=db.backref('dishes'), lazy=True)
    category_name   = db.Column(db.String(_NAME_SIZE), db.ForeignKey('dishcategory.name'), default="")
    category        = db.relationship('Dishcategory', backref=db.backref('dishes'), lazy=True)

class Dishcategory(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(_NAME_SIZE), nullable=False, unique=True)
    #dishes <- Dish

#======================[GLOBAL]=======================

class Measurement(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    unit            = db.Column(db.String(_MEAS_SIZE), nullable=False)
    #foodstuffs <- Foodstuff
    #dishes <- Dish

class Cafe(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    #coords
    name            = db.Column(db.String(_NAME_SIZE), nullable=False)
    address         = db.Column(db.String(_ADDRESS_SIZE), nullable=False)
    #invoices <- Invoice
    #supplies <- Supply
    #employees <- Employee

