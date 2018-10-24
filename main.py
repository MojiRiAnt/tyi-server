from flask      import Flask, request 
from flask_cors import CORS
import json
from datetime   import datetime
from functools  import wraps

app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI' : "sqlite:///resources/private/database.db",
    'SQLALCHEMY_TRACK_MODIFICATIONS' : False,
    'FLASK_ENV' : "development",
})

CORS(app)

import database as db
db.db.init_app(app)


def dumpResponse(response, msg_short, msg, data=None):
    return json.dumps({
        "status":
        {
            "response" : response,
            "message-short" : msg_short,
            "message" : msg,
        },
        "data" : data,
    }, indent=4)

def checkArgs(expected_args):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not all(arg in request.args for arg in expected_args):
                return dumpResponse(400, "NA", "Missing necessary arguments!")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def checkEmployee(permission):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            emp = db.Employee.query.filter_by(login=request.args['login']).first()
            if emp is None:
                return dumpResponse(404, "NF", "No employee found!")
            if emp.token != request.args['token']:
                return dumpResponse(401, "NA", "Incorrect token!")
            if (permission & emp.permission) != permission:
                return dumpResponse(403, "NA", "Permission denied!")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/mng/cafe/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Manager'])
def mng_cafe_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"        : cafe.id,
                    "name"      : cafe.name,
                    "address"   : cafe.address,
                }
                for cafe in db.Cafe.query.all()
            ])

@app.route('/mng/cafe/add')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_cafe_add():
    data = json.loads(request.args['data'])

    with app.app_context():
        db.db.session.add(db.Cafe(name=data['name'],
                                address=data['address']))
        db.db.session.commit()

    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/cafe/edit')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_cafe_edit():
    data = json.loads(request.args['data'])

    with app.app_context():
        cafe = db.Cafe.query.filter_by(id=data['id']).first()
        cafe.name=data['name']
        cafe.address=data['address']

        db.db.session.commit()

    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/shipper/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Manager'])
def mng_shipper_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"                : shipper.id,
                    "name"              : shipper.name,
                    "contract_number"   : shipper.contract_number,
                    "contract_file"     : shipper.contract_file,
                    "phone"             : shipper.phone,
                }
                for shipper in db.Shipper.query.all()
            ])

@app.route('/mng/shipper/add')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_shipper_add():
    data = json.loads(request.args['data'])

    with app.app_context():
        db.db.session.add(db.Shipper(name=data['name'],
                                    contract_number=data['contract_number'],
                                    contract_file=data['contract_file'],
                                    phone=data['phone']))
        db.db.session.commit()

    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/invoice/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Manager'])
def mng_invoice_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "number"        : invoice.number,
                    "shipper_id"    : invoice.shipper_id,
                    "shipper_name"  : invoice.shipper.name,
                    "cafe_id"       : invoice.cafe_id,
                    "cafe_name"     : invoice.cafe.name,
                    "date"          : invoice.date,
                    "supplies"      :
                    [
                        {
                            "id"                : supply.id,
                            "code"              : supply.foodstuff_code,
                            "name"              : supply.foodstuff.name,
                            "amount"            : supply.amount,
                            "measurement_unit"  : supply.foodstuff.measurement_unit,
                            "expiry"            : supply.expiry,
                        }
                        for supply in invoice.supplies
                    ],
                }
                for invoice in db.Invoice.query.all()
            ])

@app.route('/mng/invoice/add')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_invoice_add():
    data = json.loads(request.args['data'])

    with app.app_context():
        invoice = db.Invoice(number=data['number'],
                cafe_id=data['cafe_id'],
                shipper_id=data['shipper_id'])

        for supply in data['supplies']:
            invoice.supplies.append(db.Supply(expiry=supply['expiry'],
                                            amount=supply['amount'],
                                            foodstuff_code=supply['code'],
                                            cafe_id=data['cafe_id']
                                            ))
        db.db.session.add(invoice)
        db.db.session.commit()

    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/supply/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Manager'])
def mng_supply_list():
    supplies = db.Supply.query

    if 'cafe_id' in request.args:
        supplies = supplies.filter_by(cafe_id=request.args['cafe_id'])

    if 'date_start' in request.args:
        supplies = supplies.filter(db.Supply.invoice.has(db.Invoice.date >= request.args['date_start']))
    
    if 'date_finish' in request.args:
        supplies = supplies.filter(db.Supply.invoice.has(db.Invoice.date <= request.args['date_finish']))

    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"                : supply.id,
                    "expiry"            : supply.expiry,
                    "amount"            : supply.amount,
                    "cafe_id"           : supply.cafe_id,
                    "cafe_name"         : supply.cafe.name,
                    "invoice_id"        : supply.invoice_id,
                    "invoice_date"      : supply.invoice.date,
                    "invoice_number"    : supply.invoice.number,
                    "invoice_shipper_id": supply.invoice.shipper_id,
                    "invoice_shipper_name":supply.invoice.shipper.name,
                    "name"              : supply.foodstuff.name,
                    "measurement_unit"  : supply.foodstuff.measurement_unit,
                    "code"              : supply.foodstuff.code,
                }
                for supply in supplies.all()
            ])

@app.route('/mng/supply/remove')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_supply_remove():
    data = json.loads(request.args['data'])
    
    supply = db.Supply.query.filter_by(id=data['id']).first()

    if supply is None:
        return dumpResponse(404, "NF", "Supply not found!")

    db.db.session.delete(supply)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/cli/dish/list')
def cli_dish_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "name"              : dish.name,
                    "price"             : dish.price,
                    "amount"            : dish.amount,
                    "measurement_unit"  : dish.measurement_unit,
                    "category_name"     : dish.category_name,
                }
                for dish in db.Dish.query.all()
            ])

@app.route('/cli/dish/info')
@checkArgs(['data'])
def cli_dish_info():
    data = json.loads(request.args['data'])

    return dumpResponse(200, "OK", "Success!",
            {
                "description" : db.Dish.query.filter_by(id=data['id']).first().description,
            })

#@app.route('/cli/order')


if __name__ == '__main__':

    with app.app_context():
        db.db.drop_all()
        db.db.create_all()
       
       #LOAD Shipper
        with open('resources/misc/shippers.json') as f:
            models = json.load(f)

        for shipper in models:
            db.db.session.add(db.Shipper(name=shipper["name"],
                                        contract_number=shipper["contract_number"],
                                        contract_file=shipper["contract_file"],
                                        phone=shipper["phone"]))

       #LOAD Invoice, Supply
        with open('resources/misc/invoices.json') as f:
            models = json.load(f)

        for data in models:
            invoice = db.Invoice(number=data['number'],
                                cafe_id=data['cafe_id'],
                                shipper_id=data['shipper_id'])
            for supply in data['supplies']:
                invoice.supplies.append(db.Supply(amount=supply['amount'],
                                            foodstuff_code=supply['foodstuff_code'],
                                            expiry=supply['expiry'],
                                            cafe_id=data['cafe_id']))
            db.db.session.add(invoice)

       #LOAD Foodstuff
        with open('resources/misc/foodstuffs.json') as f:
            models = json.load(f)

        for foodstuff in models:
            measurement = db.Measurement.query.filter_by(unit=foodstuff['measurement']).first()
            if measurement is None:
                db.db.session.add(db.Measurement(unit=foodstuff['measurement']))
            
            db.db.session.add(db.Foodstuff(code=foodstuff['code'],
                                            name=foodstuff['name'],
                                            description=foodstuff['description'],
                                            measurement_unit=foodstuff['measurement']))

       #LOAD Dish, Dishcategory, Linkdishfoodstuff
        with open('resources/misc/dishes.json') as f:
            models = json.load(f)

        for data in models:
            category = db.Dishcategory(name=data["name"])
            for dish in data["dishes"]:
                measurement = db.Measurement.query.filter_by(unit=dish['measurement']).first()
                if measurement is None:
                    db.db.session.add(db.Measurement(unit=dish['measurement']))

                new_dish = db.Dish(name=dish["name"],
                                    description=dish["description"],
                                    price=dish["price"],
                                    amount=dish["amount"],
                                    measurement_unit=dish["measurement"],
                                    category_name=category.name)
                db.db.session.add(new_dish)
                new_dish = db.Dish.query.filter_by(name=dish["name"]).first()

                for foodstuff in dish['ingredients']:
                    db.db.session.add(db.Linkdishfoodstuff(amount=foodstuff['amount'],
                                                        foodstuff_code=foodstuff['code'],
                                                        dish_id=new_dish.id))

            db.db.session.add(category)

       #LOAD Cafe, Employee
        with open('resources/misc/employees.json') as f:
            models = json.load(f)

        for data in models:
            cafe = db.Cafe(name=data["name"],
                        address=data["address"])
            for emp in data["staff"]:
                perm = sum(db.Role[x] for x in emp["permission"])
                cafe.employees.append(db.Employee(login=emp["login"],
                                                token=emp["token"],
                                                phone=emp["phone"],
                                                email=emp["email"],
                                                permission=perm))
            db.db.session.add(cafe)

        db.db.session.commit()
        
    app.run(host='0.0.0.0', port='5000', debug=True) # WARNING: debug=True

