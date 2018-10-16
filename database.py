from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


#======[MISC FUNCTIONS]====== # TO BE DONE



#======[DATABASE TABLES]====== # IN DEVELOPMENT

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)

class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)


