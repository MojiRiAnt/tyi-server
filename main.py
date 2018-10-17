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


@app.route('/cli/getmenu')
def cli_getmenu():
    
    return json.dumps({
        "status" :
        {
            "response" : 200,
            "message-short" : "OK",
            "message" : "Success!",
        },
        "data" :
        [
            {
                "name" : dish.name,
                "category" : dish.category,
                "price" : dish.price,
                "amount" : dish.amount,
                "measurement" : dish.measurement_unit,
            }
            for dish in db.Dish.query.all()
        ],
    })

@app.route('/cli/dishinfo')
def cli_dishinfo():

    expected_args = ['name']
    if not all(x in request.args for x in expected_args):
        return json.dumps({
            "status" :
            {
                "response" : 401,
                "message-short" : "NA",
                "message" : "Missing query arguments!",
            },
        })

    dish = db.Dish.query.filter_by(name=request.args['name']).first()

    if dish is None:
        return json.dumps({
            "status" :
            {
                "response" : 404,
                "message-short" : "NF",
                "message" : "Dish not found!",
            },
        })

    return json.dumps({
        "status" :
        {
            "response" : 200,
            "message-short" : "OK",
            "message" : "Success!",
        },
        "data" :
        {
            "description" : dish.description,
            "ingredients" : dish.ingredients,
        },
    })


if __name__ == '__main__':

    with app.app_context():
        db.db.drop_all()
        db.db.create_all()

        with open('resources/misc/menu.json') as f:
            menu = json.load(f)

        for dish in menu:
            db.db.session.add(db.Dish(name=dish["name"],
                                    category=dish["category"],
                                    price=dish["price"],
                                    amount=dish["amount"],
                                    measurement_unit=dish["measurement"],
                                    ingredients=dish["ingredients"],
                                    description=dish["description"]))
        db.db.session.commit()

    app.run(host='0.0.0.0', port='5000', debug=True) # WARNING: debug=True

