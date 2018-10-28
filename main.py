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

def checkDriver():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            drv = db.Driver.query.filter_by(login=request.args['login']).first()
            if drv is None:
                return dumpResponse(404, "NF", "No driver found!")
            if drv.token != request.args['token']:
                return dumpResponse(401, "NA", "Incorrect token!")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def checkClient():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cli = db.Client.query.filter_by(phone=request.args['phone']).first()
            if cli is None:
                return dumpResponse(404, "NF", "No client found!")
            if cli.secret != request.args['secret']:
                return dumpResponse(401, "NA", "Incorrect secret!")
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
    db.db.session.add(db.Cafe(name=data['name'],
                            address=data['address']))
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/cafe/edit')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_cafe_edit():
    data = json.loads(request.args['data'])
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
                    "photo"             : shipper.photo,
                }
                for shipper in db.Shipper.query.all()
            ])

@app.route('/mng/shipper/add')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_shipper_add():
    data = json.loads(request.args['data'])
    db.db.session.add(db.Shipper(name=data['name'],
                                contract_number=data['contract_number'],
                                contract_file=data['contract_file'],
                                phone=data['phone']))
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/shipper/edit')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_shipper_edit():
    data = json.loads(request.args['data'])
    shipper = db.Shipper.query.filter_by(id=data['id']).first()
    shipper.name = data['name']
    shipper.contract_number = data['contract_number']
    shipper.contract_file = data['contract_file']
    shipper.phone = data['phone']
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/invoice/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Manager'])
def mng_invoice_list():
    invoices  = db.Invoice.query
    if 'cafe_id' in request.args:
        invoices = invoices.filter_by(cafe_id=request.args['cafe_id'])
    if 'date_start' in request.args:
        invoices = invoices.filter(db.Invoice.date >= request.args['date_start'])
    if 'date_finish' in request.args:
        invoices = invoices.filter(db.Invoice.date <= request.args['date_finish'])
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
                            "photo"             : supply.foodstuff.photo,
                        }
                        for supply in invoice.supplies
                    ],
                }
                for invoice in invoices
            ])

@app.route('/mng/invoice/add')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_invoice_add():
    data = json.loads(request.args['data'])
    invoice = db.Invoice(number=data['number'],
            cafe_id=data['cafe_id'],
            shipper_id=data['shipper_id'])
    for supply in data['supplies']:
        invoice.supplies.append(db.Supply(expiry=supply['expiry'],
                                        amount=supply['amount'],
                                        foodstuff_code=supply['code'],
                                        cafe_id=data['cafe_id']))
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
                    "photo"             : supply.foodstuff.photo,
                }
                for supply in supplies.all()
            ])

@app.route('/mng/supply/setamount')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_supply_remove():
    data = json.loads(request.args['data'])
    supply = db.Supply.query.filter_by(id=data['id']).first()
    supply.amount = data['amount']
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/foodstuff/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Manager'])
def mng_foodstuff_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"                : foodstuff.id,
                    "code"              : foodstuff.code,
                    "name"              : foodstuff.name,
                    "measurement_unit"  : foodstuff.measurement_unit,
                    "photo"             : foodstuff.photo,
                }
                for foodstuff in db.Foodstuff.query.all()
            ])

@app.route('/mng/foodstuff/add')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_foodstuff_add():
    data = json.loads(request.args['data'])
    db.db.session.add(db.Foodstuff(code=data["code"],
                                    name=data["name"],
                                    measurement_unit=data["measurement_unit"]))
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/foodstuff/edit')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_foodstuff_edit():
    data = json.loads(request.args['data'])
    foodstuff = db.Foodstuff.query.filter_by(id=data["id"]).first()
    foodstuff.code=data["code"]
    foodstuff.name=data["name"]
    foodstuff.measurement_unit=data["measurement_unit"]
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/foodstuff/info')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_foodstuff_info():
    data = json.loads(request.args['data'])
    foodstuff = db.Foodstuff.query.filter_by(code=data['code']).first()
    if foodstuff is None:
        return dumpResponse(200, "OK", "Success!",
                {
                    "found" : False,    
                })
    return dumpResponse(200, "OK", "Success!",
                {
                    "found"             : True,
                    "name"              : foodstuff.name,
                    "photo"             : foodstuff.photo,
                    "measurement_unit"  : foodstuff.measurement_unit,
                })

@app.route('/mng/measurement/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Manager'])
def mng_measurement_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"    : measurement.id,
                    "unit"  : measurement.unit,
                }
                for measurement in db.Measurement.query.all()
            ])

@app.route('/mng/dish/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Manager'])
def mng_dish_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"                : dish.id,
                    "name"              : dish.name,
                    "description"       : dish.description,
                    "price"             : dish.price,
                    "amount"            : dish.amount,
                    "cooking_time"      : dish.cooking_time,
                    "photo"             : dish.photo,
                    "measurement_unit"  : dish.measurement_unit,
                    "category_name"     : dish.category_name,
                    "ingredients" :
                    [
                        {
                            "amount" : link.amount,
                            "foodstuff_code" : link.foodstuff_code,
                            "foodstuff_name" : link.foodstuff.name,
                            "foodstuff_photo": link.foodstuff.photo,
                            "foodstuff_measurement_unit" : link.foodstuff.measurement_unit,
                        }
                        for link in dish.linkfoodstuffs
                    ]
                }
                for dish in db.Dish.query.all()
            ])

@app.route('/mng/dish/add')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_dish_add():
    data = json.loads(request.args['data'])
    dish = db.Dish(name=data['name'],
                description=data['description'],
                price=data['price'],
                amount=data['amount'],
                cooking_time=data['cooking_time'],
                measurement_unit=data['measurement_unit'],
                category_name=data['category_name'])
    for ing in data['ingredients']:
        dish.linkfoodstuffs.append(db.Linkdishfoodstuff(amount = ing['amount'],
                                        foodstuff_code = ing['code']))
    db.db.session.add(dish)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/dish/edit')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_dish_edit():
    data = json.loads(request.args['data'])
    dish = db.Dish.query.filter_by(id=data['id']).first()
    dish.name = data['name']
    dish.description = data['description']
    dish.price = data['price']
    dish.amount = data['amount']
    dish.cooking_time = data['cooking_time']
    dish.measurement_unit = data['measurement_unit']
    dish.category_name = data['category_name']
    dish.linkfoodstuffs = [db.Linkdishfoodstuff(amount = ing['amount'],
                                                    foodstuff_code = ing['foodstuff_code'])
                                for ing in data['ingredients']]
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")


@app.route('/mng/dish/delete')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_dish_delete():
    data = json.loads(request.args['data'])
    dish = db.Dish.query.filter_by(id=data['id']).first()
    maybeorder = db.Maybeorder.query.filter((str(dish.id)+':') in db.Maybeorder.dishes).first()
    order = db.Order.query.filter((str(dish.id)+':') in db.Order.dishes).first()
    if maybeorder is not None or order is not None:
        return dumpResponse(403, "FB", "There are orders w/ this dish!")
    for link in dish.linkdishfoodstuffs:
        db.db.session.delete(link)
    db.db.session.delete(dish)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/dishcategory/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Manager'])
def mng_dishcategory_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id" : cat.id,
                    "name" : cat.name,
                }
                for cat in db.Dishcategory.query.all()
            ])

@app.route('/mng/dishcategory/add')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_dishcategory_add():
    data = json.loads(request.args['data'])
    db.db.session.add(db.Dishcategory(name=data['name']))
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success")

@app.route('/mng/dishcategory/edit')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_dishcategory_edit():
    data = json.loads(request.args['data'])
    cat = db.Dishcategory.query.filter_by(id=data['id']).first()
    cat.name = data['name']
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/dishcategory/delete')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Manager'])
def mng_dishcategory_delete():
    data = json.loads(request.args['data'])
    cat = db.Dishcategory.query.filter_by(id=data['id']).first()
    if cat.dishes != []:
        return dumpResponse(403, "FB", "There're dishes in this category!")
    db.db.session.delete(cat)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")


@app.route('/adm/emptyclient/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Admin'])
def adm_emptyclient_list():
    return dumpResponse(200, "OK", "Success!",
                [
                    {
                        "phone"             : cli.phone,
                        "secret"            : cli.secret,
                        "registered_date"   : cli.registered_date,
                    }
                    for cli in db.Emptyclient.query.all()
                ])

@app.route('/adm/client/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Admin'])
def adm_client_list():
    return dumpResponse(200, "OK", "Success!",
                [
                    {
                        "phone"             : cli.phone,
                        "email"             : cli.email,
                        "secret"            : cli.secret,
                        "name"              : cli.name,
                        "registered_date"   : cli.registered_date,
                    }
                    for cli in db.Client.query.all()
                ])

@app.route('/adm/client/add')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Admin'])
def adm_client_add():
    data = json.loads(request.args['data'])
    cli = db.Client.query.filter_by(phone=data['phone']).first()
    if cli is not None:
        return dumpResponse(403, "AE", "Client already exists!")

    if not db.Client.isValidPhone(data['phone']) or not db.Client.isValidName(data['name']):
        return dumpResponse(403, "FB", "Invalid phone or name!")

    cli = db.Client(phone=data['phone'],
                    secret=db.Client.randSecret(),
                    name=data['name'],
                    reqistered_date=data['registered_date'])
    if 'email' in data and db.Client.isValidEmail(data['email']):
        cli.email = data['email']
    db.db.session.add(cli)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/adm/client/edit')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Admin'])
def adm_client_edit():
    data = json.loads(request.args['data'])
    cli = db.Client.query.filter_by(phone=data['phone']).first()
    if 'name' in data and db.Client.isValidName(data['name']):
        cli.name = data['name']
    if 'email' in data and db.Client.isValidEmail(data['email']):
        cli.email = data['email']
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/adm/client/delete')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Admin'])
def adm_client_delete():
    data = json.loads(request.args['data'])
    cli = db.Client.query.filter_by(phone=data['phone']).first()
    if cli.orders != [] or cli.maybeorders != [] or cli.deliveries != []:
        return dumpResponse(403, "FB", "Client has orders/deliveries!")
    db.db.session.delete(cli)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/adm/employee/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Admin'])
def adm_employee_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id" : emp.id,
                    "name" : emp.name,
                    "login" : emp.login,
                    "phone" : emp.phone,
                    "email" : emp.email,
                    "permission" : emp.permission,
                    "registered_date" : emp.registered_date,
                    "cafe_id" : emp.cafe_id,
                    "cafe_name" : emp.cafe.name,
                }
                for emp in db.Employee.query.all()
            ])

@app.route('/adm/employee/add')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Admin'])
def adm_employee_add():
    data = json.loads(request.args['data']) # WARNING : no validity checkers
    db.db.session.add(db.Employee(login=data['login'],
                                    phone=data['phone'],
                                    email=data['email'],
                                    permission=data['permission'],
                                    cafe_id=data['cafe_id']))
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/adm/employee/edit')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Admin'])
def adm_employee_edit():
    data = json.loads(request.args['data']) # WARNING : no validity checkers
    emp = db.Employee.query.filter_by(id=data['id']).first()
    emp.login = data['login']
    emp.name = data['name']
    emp.phone = data['phone']
    emp.email = data['email']
    emp.permission = data['permission']
    emp.cafe_id = data['cafe_id']
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")


@app.route('/cli/dish/list')
@checkArgs(['phone', 'secret'])
@checkClient()
def cli_dish_list():
    dishes = db.Dish.query
    if 'category' in request.args:
        dishes = dishes.filter_by(category_name=request.args['category'])
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"                : dish.id,
                    "name"              : dish.name,
                    "price"             : dish.price,
                    "amount"            : dish.amount,
                    "photo"             : dish.photo,
                    "measurement_unit"  : dish.measurement_unit,
                    "category_name"     : dish.category_name,
                    "cooking_time"      : dish.cooking_time,
                }
                for dish in dishes
            ])

@app.route('/cli/dish/info')
@checkArgs(['phone', 'secret', 'data'])
@checkClient()
def cli_dish_info():
    data = json.loads(request.args['data'])
    dish = db.Dish.query.filter_by(id=data['id']).first()
    if dish is None:
        return dumpResponse(404, "NF", "No dish found!")
    return dumpResponse(200, "OK", "Success!",
            {
                "description" : dish.description,
                "ingredients" :
                [
                    {
                        "amount"            : ing.amount,
                        "code"              : ing.foodstuff.code,
                        "name"              : ing.foodstuff.name,
                        "measurement_unit"  : ing.foodstuff.measurement_unit,
                    }
                    for ing in db.Linkdishfoodstuff.query.filter_by(dish_id=dish.id)
                ],
            })

@app.route('/cli/dishcategory/list')
@checkArgs(['phone', 'secret'])
@checkClient()
def cli_dishcategory_list():
    return dumpResponse(200, "OK", "Success!",
            [cat.name for cat in db.Dishcategory.query.all()])

@app.route('/cli/maybeorder/list')
@checkArgs(['phone', 'secret'])
@checkClient()
def cli_maybeorder_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"        : maybeorder.id,
                    "address"   : maybeorder.address,
                    "dishes"    : maybeorder.dishes,
                }
                for maybeorder in db.Maybeorder.query.filter(db.Maybeorder.client.has(phone=request.args['phone'])).all()
            ])

@app.route('/cli/order/list')
@checkArgs(['phone', 'secret'])
@checkClient()
def cli_order_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"        : order.id,
                    "address"   : order.address,
                    "dishes"    : order.dishes,
                }
                for order in db.Order.query.filter(db.Order.client.has(phone=request.args['phone'])).all()
            ])

@app.route('/cli/delivery/list')
@checkArgs(['phone', 'secret'])
@checkClient()
def cli_delivery_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"        : delivery.id,
                    "address"   : delivery.address,
                    "dishes"    : delivery.dishes,
                }
                for delivery in db.Delivery.query.filter(db.Delivery.client.has(phone=request.args['phone'])).all()
            ])

@app.route('/cli/auth/add')
@checkArgs(['phone'])
def cli_auth_try():
    cli = db.Client.query.filter_by(phone=request.args['phone']).first()
    ecli = db.Emptyclient.query.filter_by(phone=request.args['phone']).first()
    if cli is None and ecli is None:
        db.db.session.add(db.Emptyclient(phone=request.args['phone'],
                                    secret=db.Client.randSecret()))
        db.db.session.commit()
        #WARNING : send SMS with secret here
        return dumpResponse(200, "OK", "Success!",
                {
                    "verified" : False, 
                })
    return dumpResponse(200, "OK", "Success!",
                {
                    "verified" : cli is not None,
                })

@app.route('/cli/auth/new')
@checkArgs(['phone', 'secret', 'name'])
def cli_auth_new():
    ecli = db.Emptyclient.query.filter_by(phone=request.args['phone']).first()
    if ecli is None:
        return dumpResponse(404, "NF", "Emptyclient not found!")
    if request.args['secret'] != ecli.secret:
        return dumpResponse(401, "NA", "Incorrect secret!")
    if not db.Client.isValidName(request.args['name']):
        return dumpResponse(403, "NA", "Forbidden info!")
    cli = db.Client(phone = ecli.phone,
                    secret = db.Client.randSecret(),
                    name = request.args['name'],
                    registered_date = ecli.registered_date)
    db.db.session.add(cli)
    db.db.session.delete(ecli)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!",
                {
                    "phone" : cli.phone,
                    "secret": cli.secret,
                    "name"  : cli.name,
                    "email" : cli.email,
                })

@app.route('/cli/auth/login')
@checkArgs(['phone', 'secret'])
@checkClient()
def cli_auth():
    cli = db.Client.query.filter_by(phone=request.args['phone']).first()
    return dumpResponse(200, "OK", "Success!",
                {
                    "phone" : cli.phone,
                    "name"  : cli.name,
                    "email" : cli.email,
                })

@app.route('/cli/update')
@checkArgs(['phone', 'secret'])
@checkClient()
def cli_update():
    cli = db.Client.query.filter_by(phone=request.args['phone']).first()
    updated = {'name':False, 'email':False}
    if 'name' in request.args and db.Client.isValidName(request.args['name']):
        cli.name = request.args['name']
        updated['name'] = True
    if 'email' in request.args and db.Client.isValidEmail(request.args['email']):
        cli.email = request.args['email']
        updated['email'] = True
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!", updated)

@app.route('/cli/order')
@checkArgs(['phone', 'secret', 'address', 'data'])
@checkClient()
def cli_order():
    cli = db.Client.query.filter_by(phone=request.args['phone']).first()
    try:
        data = json.loads(request.args['data'])
    except Exception as e:
        return dumpResponse(400, "ER", "Invalid JSON!")
    dishes = ' '.join(str(dish["id"])+':'+str(dish["amount"]) for dish in data) # WARNING : No json validity checker
    cli = db.Client.query.filter_by(phone=request.args["phone"]).first()
    db.db.session.add(db.Maybeorder(address=request.args["address"],
                                    client_id=cli.id,
                                    dishes=dishes))
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")


@app.route('/opr/maybeorder/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Operator'])
def opr_maybeorder_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"            : maybeorder.id,
                    "address"       : maybeorder.address,
                    "client_id"     : maybeorder.client_id,
                    "client_phone"  : maybeorder.client.phone,
                    "dishes"        : maybeorder.dishes,
                }
                for maybeorder in db.Maybeorder.query.all()
            ])

@app.route('/opr/maybeorder/claim')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Operator'])
def opr_maybeorder_approve():
    operator = db.Employee.query.filter_by(login=request.args['login']).first()
    data = json.loads(request.args['data'])
    maybeorder = db.Maybeorder.query.filter_by(id=data["id"]).first()
    if maybeorder is None:
        return dumpResponse(404, "NF", "No maybeorder found!")
    db.db.session.add(db.Order(address = maybeorder.address,
                                dishes = maybeorder.dishes,
                                client_id = maybeorder.client_id,
                                cafe_id = operator.cafe_id))
    db.db.session.delete(maybeorder)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/opr/maybeorder/delete')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Operator'])
def opr_maybeorder_decline():
    data = json.loads(request.args['data'])
    maybeorder = db.Maybeorder.query.filter_by(id=data["id"]).first()
    if maybeorder is None:
        return dumpResponse(404, "NF", "No maybeorder found!")
    db.db.session.delete(maybeorder)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/opr/order/list')
@checkArgs(['login', 'token'])
@checkEmployee(db.Role['Operator'])
def opr_order_list():
    operator = db.Employee.query.filter_by(login=request.args['login']).first()
    return dumpResponse(200, "OK", "Success!",
                [
                    {
                        "id"            : order.id,
                        "address"       : order.address,
                        "client_id"     : order.client_id,
                        "client_phone"  : order.client.phone,
                        "dishes"        : order.dishes,
                    }
                    for order in db.Order.query.filter_by(cafe_id=operator.cafe_id).all()
                ])

@app.route('/opr/order/ready')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Operator'])
def opr_order_setcooked():
    operator = db.Employee.query.filter_by(login=request.args['login']).first()
    data = json.loads(request.args['data'])
    order = db.Order.query.filter_by(id=data["id"], cafe_id=operator.cafe_id).first()
    if order is None:
        return dumpResponse(404, "NF", "No order found!")
    db.db.session.add(db.Delivery(address=order.address,
                                    dishes=order.dishes,
                                    client_id=order.client_id,
                                    cafe_id=order.cafe_id))
    db.db.session.delete(order)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/opr/dish/info')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Operator'])
def opr_dish_info():
    data = json.loads(request.args['data'])
    dish = db.Dish.query.filter_by(id=data['id']).first()
    if dish is None:
        return dumpResponse(404, "NF", "No dish found!")
    return dumpResponse(200, "OK", "Success!",
            {
                "name" : dish.name,
                "cooking_time" : dish.cooking_time,
            })

@app.route('/opr/dish/list')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Operator'])
def opr_dish_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"                : dish.id,
                    "name"              : dish.name,
                    "description"       : dish.description,
                    "price"             : dish.price,
                    "amount"            : dish.amount,
                    "cooking_time"      : dish.cooking_time,
                    "photo"             : dish.photo,
                    "measurement_unit"  : dish.measurement_unit,
                    "category_name"     : dish.category_name,
                    "ingredients" :
                    [
                        {
                            "amount" : link.amount,
                            "foodstuff_code" : link.foodstuff_code,
                            "foodstuff_name" : link.foodstuff.name,
                        }
                        for link in dish.linkfoodstuffs
                    ]
                }
                for dish in db.Dish.query.all()
            ])

@app.route('/opr/client/register')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Operator'])
def opr_client_register():
    data = json.loads(request.args['data'])
    cli = db.Client.query.filter_by(phone=data['phone']).first()
    if cli is not None:
        return dumpResponse(403, "FB", "Client already exists!")
    cli = db.Client(phone = data['phone'],
                    secret = db.Client.randSecret(),
                    name = data['name'])
    if 'email' in data:
        cli.email = data['email']
    db.db.session.add(cli)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!",
                {
                    "phone" : cli.phone,
                    "secret": cli.secret,
                    "name"  : cli.name,
                    "email" : cli.email,
                })

@app.route('/opr/client/order')
@checkArgs(['login', 'token', 'data'])
@checkEmployee(db.Role['Operator'])
def opr_client_order():
    data = json.loads(request.args['data'])
    cli = db.Client.query.filter_by(phone=data["phone"]).first()
    if cli is None:
        return dumpResponse(403, "FB", "No client found!")
    dishes = ' '.join(str(dish["id"])+':'+str(dish["amount"]) for dish in data['dishes'])
    db.db.session.add(db.Maybeorder(address=data["address"],
                                    client_id=cli.id,
                                    dishes=dishes))
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")


@app.route('/drv/delivery/list')
@checkArgs(['login', 'token'])
@checkDriver()
def drv_delivery_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"            : delivery.id,
                    "address"       : delivery.address,
                    "client_id"     : delivery.client_id,
                    "client_name"   : delivery.client.name,
                    "dishes"        : delivery.dishes,
                    "cafe_id"       : delivery.cafe_id,
                    "cafe_name"     : delivery.cafe.name,
                }
                for delivery in db.Delivery.query.filter_by(driver_id=-1).all()
            ])

@app.route('/drv/delivery/claim')
@checkArgs(['login', 'token', 'data'])
@checkDriver()
def drv_delivery_claim():
    data = json.loads(request.args['data'])
    driver = db.Driver.query.filter_by(login=request.args['login']).first()
    delivery = db.Delivery.query.filter_by(id=data['id']).first()
    if delivery.driver_id != -1:
        return dumpResponse(403, "AT", "Delivery already taken!")
    delivery.driver_id = driver.id
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")

@app.route('/drv/claim/list')
@checkArgs(['login', 'token'])
@checkDriver()
def drv_claim_list():
    driver = db.Driver.query.filter_by(login=request.args['login']).first()
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"            : delivery.id,
                    "address"       : delivery.address,
                    "client_id"     : delivery.client_id,
                    "client_name"   : delivery.client.name,
                    "dishes"        : delivery.dishes,
                    "cafe_id"       : delivery.cafe_id,
                    "cafe_name"     : delivery.cafe.name,
                }
                for delivery in db.Delivery.query.filter_by(driver_id=driver.id).all()
            ])

@app.route('/drv/claim/confirm')
@checkArgs(['login', 'token', 'data'])
@checkDriver()
def drv_claim_confirm():
    data = json.loads(request.args['data'])
    delivery = db.Delivery.query.filter_by(id=data['id']).first()
    db.db.session.delete(delivery)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success")

@app.route('/drv/claim/decline')
@checkArgs(['login', 'token', 'data'])
@checkDriver()
def drv_claim_decline():
    data = json.loads(request.args['data'])
    delivery = db.Delivery.query.filter_by(id=data['id']).first()
    db.db.session.delete(delivery)
    db.db.session.commit()
    return dumpResponse(200, "OK", "Success!")


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
                                    cooking_time=dish["cooking_time"],
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
                employee = db.Employee(login=emp["login"],
                                token=db.Employee.randToken(),
                                phone=emp["phone"],
                                email=emp["email"],
                                permission=sum(db.Role[x] for x in emp["permission"]))
                if "token" in emp:
                    employee.token = emp["token"]
                cafe.employees.append(employee)
            db.db.session.add(cafe)

       #LOAD Driver
        with open('resources/misc/drivers.json') as f:
            drivers = json.load(f)

        for driver in drivers:
            drv = db.Driver(login=driver["login"],
                            phone=driver["phone"],
                            email=driver["email"],
                            token=db.Employee.randToken())
            if "token" in driver:
                drv.token = driver["token"]
            db.db.session.add(drv)

        db.db.session.commit()
        
    app.run(host='0.0.0.0', port='5000', debug=True) # WARNING: debug=True

