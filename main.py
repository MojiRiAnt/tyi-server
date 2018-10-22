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


    
if __name__ == '__main__':

    with app.app_context():
        db.db.drop_all()
        db.db.create_all()
        
        with open('resources/misc/shippers.json') as f:
            models = json.load(f)

        for shipper in models:
            db.db.session.add(db.Shipper(name=shipper["name"],
                                        contract_number=shipper["contract_number"]))

        db.db.session.commit()

    app.run(host='0.0.0.0', port='5000', debug=True) # WARNING: debug=True

