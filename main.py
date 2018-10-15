from flask import Flask

#======[APP CONFIG]====== » IN DEVELOPMENT

app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_DATABASE_URI' : "sqlite:///database.db",
    'SQLALCHEMY_TRACK_MODIFICATIONS' : False,
    'FLASK_ENV' : "development",
})


#======[DATABASE STUFF]====== » TO BE DONE



#======[HANDLING ROUTES]====== » IN DEVELOPMENT

@app.route('/test')
def test():
    return "<h1>This is a test page</h1>"


#======[RUN & DEBUG]====== » READY TO GO

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True) # WARNING: debug=True
