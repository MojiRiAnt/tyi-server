from flask import Flask 

#======[APP CONFIG]====== » READY TO GO

app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI' : "sqlite:///database.db",
    'SQLALCHEMY_TRACK_MODIFICATIONS' : False,
    'FLASK_ENV' : "development",
})


#======[DATABASE STUFF]====== » READY TO GO

import database as db

db.db.init_app(app)

#======[HANDLING ROUTES]====== » IN DEVELOPMENT

@app.route('/dbg')
def dbg():
    return "<h1>This is a debug page</h1>"


#======[RUN & DEBUG]====== » READY TO GO

if __name__ == '__main__':

    with app.app_context(): # PERFORM YOUR OWN DEBUGGING HERE
        db.db.drop_all()
        db.db.create_all()
        db.db.session.add(db.Cafe(name='testcafe'))
        db.db.session.commit()

    app.run(host='0.0.0.0', port='5000', debug=True) # WARNING: debug=True

