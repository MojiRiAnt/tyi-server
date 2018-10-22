from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

_NAME_SIZE = 32
_NUMBER_SIZE = 16
_CODE_SIZE = 16
_TEXT_SIZE = 128

#================[FOOD MANAGEMENT]===============

class Shipper(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(_NAME_SIZE), nullable=False)
    contract_number = db.Column(db.String(_NUMBER_SIZE), nullable=False)
    #supplies <- Supply

class Invoice(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    number          = db.Column(db.String(_NUMBER_SIZE), nullable=False)
    #supplies <- Supply
    shipper_id      = db.Column(db.Integer, db.ForeignKey('shipper.id'), default=-1)
    shipper         = db.relationship('Shipper', backref=db.backref('invoices'), lazy=True)
    cafe_id         = db.Column(db.Integer, db.ForeignKey('cafe.id'), default=-1)
    cafe            = db.relationship('Cafe', backref=db.backref('invoices', lazy=True))

class Supply(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    #expiry
    #amount
    foodstuff_code  = db.Column(db.String(_CODE_SIZE), db.ForeignKey('foodstuff.code'), default=-1)
    foodstuff       = db.relationship('Foodstuff', backref=db.backref('supplies'), lazy=True)
    cafe_id         = db.Column(db.Integer, db.ForeignKey('cafe.id'), default=-1)
    cafe            = db.relationship('Cafe', backref=db.backref('supplies'), lazy=True)
    invoice_id      = db.Column(db.Integer, db.ForeignKey('invoice.id'), default=-1)
    invoice         = db.relationship('Invoice', backref=db.backref('supplies'), lazy=True)

class Foodstuff(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    code            = db.Column(db.String(_CODE_SIZE), nullable=False)
    name            = db.Column(db.String(_NAME_SIZE), nullable=False)
    #measurement
    description     = db.Column(db.String(_TEXT_SIZE), nullable=False)
    #supplies <- Supply

#======================[GLOBAL]=======================

class Cafe(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    #coords
    name            = db.Column(db.String(_NAME_SIZE), nullable=False)
    #invoices <- Invoice
    #supplies <- Supply

