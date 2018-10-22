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
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "name"      : cafe.name,
                    "address"   : cafe.address,
                }
                for cafe in db.Cafe.query.all()
            ])

@app.route('/mng/shippers/list')
def mng_shippers_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "name"              : shipper.name,
                    "contract_number"   : shipper.contract_number,
                }
                for shipper in db.Shipper.query.all()
            ])

@app.route('/mng/invoice/list')
def mng_invoice_list():
    return dumpResponse(200, "OK", "Success!",
            [
                {
                    "number"    : invoice.number,
                    "shipper"   : invoice.shipper.name,
                    "cafe"      : invoice.cafe.name,
                    "supplies"  :
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
    expected_args = ['data']

    data = json.loads(request.args['data'])

    with app.app_context():
        invoice = db.Invoice(number=data['number'],
                cafe_id=db.Cafe.query.filter_by(name=data['cafe_name']).first().id,
                shipper_id=db.Shipper.query.filter_by(name=data['shipper_name']).first().id)
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

        with open('resources/misc/employees.json') as f:
            models = json.load(f)

        for cafe in models:
            db.db.session.add(db.Cafe(name=cafe["name"]))

        db.db.session.commit()

    app.run(host='0.0.0.0', port='5000', debug=True) # WARNING: debug=True

