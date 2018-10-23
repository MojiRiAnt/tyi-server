from flask import Flask, request 
import json

app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI' : "sqlite:///resources/private/database.db",
    'SQLALCHEMY_TRACK_MODIFICATIONS' : False,
    'FLASK_ENV' : "development",
})

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


@app.route('/mng/cafe/list')
def mng_cafe_list():
    expected_args = ['login', 'token']

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
def mng_cafe_add():
    expected_args = ['login', 'token', 'data']

    data = json.loads(request.args['data'])

    with app.app_context():
        db.db.session.add(db.Cafe(name=data['name'],
                                address=data['address']))
        db.db.session.commit()

    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/cafe/edit')
def mng_cafe_edit():
    expected_args = ['login', 'token', 'data']
    
    data = json.loads(request.args['data'])

    with app.app_context():
        cafe = db.Cafe.query.filter_by(id=data['id']).first()
        cafe.name=data['name']
        cafe.address=data['address']

        db.db.session.commit()

    return dumpResponse(200, "OK", "Success!")


@app.route('/mng/shipper/list')
def mng_shipper_list():
    expected_args = ['login', 'token']

    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "id"                : shipper.id,
                    "name"              : shipper.name,
                    "contract_number"   : shipper.contract_number,
                }
                for shipper in db.Shipper.query.all()
            ])

@app.route('/mng/shipper/add')
def mng_shipper_add():
    expected_args = ['login', 'token', 'data']

    data = json.loads(request.args['data'])

    with app.app_context():
        db.db.session.add(db.Shipper(name=data['name'],
                                    contract_number=data['contract_number']))
        db.db.session.commit()

    return dumpResponse(200, "OK", "Success!")

@app.route('/mng/invoice/list')
def mng_invoice_list():
    expected_args = ['login', 'token']

    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "number"        : invoice.number,
                    "shipper_id"    : invoice.shipper_id,
                    "shipper_name"  : invoice.shipper.name,
                    "cafe_id"       : invoice.cafe_id,
                    "cafe_name"     : invoice.cafe.name,
                    "supplies"      :
                    [
                        {
                            "code" : supply.foodstuff_code,
                            "name" : supply.foodstuff.name,
                            #"amount" :
                            #"date" :
                            #"expiry" :
                        }
                        for supply in invoice.supplies
                    ],
                }
                for invoice in db.Invoice.query.all()
            ])

@app.route('/mng/invoice/add')
def mng_invoice_add():
    expected_args = ['login', 'token', 'data']

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

    
if __name__ == '__main__':

    with app.app_context():
        db.db.drop_all()
        db.db.create_all()
        
        with open('resources/misc/shippers.json') as f:
            models = json.load(f)

        for shipper in models:
            db.db.session.add(db.Shipper(name=shipper["name"],
                                        contract_number=shipper["contract_number"]))

        with open('resources/misc/invoices.json') as f:
            models = json.load(f)

        for invoice in models:
            pass

        with open('resources/misc/employees.json') as f:
            models = json.load(f)

        for cafe in models:
            db.db.session.add(db.Cafe(name=cafe["name"],
                                    address=cafe["address"]))

        db.db.session.commit()

    app.run(host='0.0.0.0', port='5000', debug=True) # WARNING: debug=True

