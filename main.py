from flask import Flask 
import json

#======[APP CONFIG]====== » READY TO GO

global app
app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI' : "sqlite:///resources/private/database.db",
    'SQLALCHEMY_TRACK_MODIFICATIONS' : False,
    'FLASK_ENV' : "development",
})

#======[DATABASE STUFF]====== » READY TO GO

import database as db

db.db.init_app(app)

#======[HANDLING ROUTES]====== » IN DEVELOPMENT

@app.route('/cli/getmenu')
def cli_getmenu():
    
    return json.dumps({
        "status" :
        {
            "response" : 200,
            "message-short" : "OK",
            "message" : "OK",
        },
        "data" :
        [
            {
                "name" : dish.name,
                "category" : dish.category,
                "ingredients" : dish.ingredients,
            }
            for dish in db.Dish.query.all()
        ],
    })

#======[RUN & DEBUG]====== » READY TO GO

if __name__ == '__main__':

    with app.app_context(): # PERFORM YOUR OWN DEBUGGING HERE

        db.db.drop_all()
        db.db.create_all()

        with open('resources/misc/menu.json') as f:
            menu = json.load(f)

        for dish in menu:
            db.db.session.add(db.Dish(name=dish["name"],
                                    category=dish["category"],
                                    ingredients=dish["ingredients"]))

        db.db.session.commit()

    app.run(host='0.0.0.0', port='5000', debug=True) # WARNING: debug=True

