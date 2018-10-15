from flask import Flask

app = Flask(__name__)

app.config.update({
    'SQLALCHEMY_DATABASE_URI' : "sqlite:///database.db",
    'SQLALCHEMY_TRACK_MODIFICATIONS' : False,
    'FLASK_ENV' : "development",
})

@app.route('/test')
def test():
    return "<h1>This is a test page</h1>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True) # WARNING: debug=True
