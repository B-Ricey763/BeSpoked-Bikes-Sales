import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
 
 
db = SQLAlchemy()
csrf = CSRFProtect()
app = Flask(__name__)

import bespoked_bikes_sales.routes
import bespoked_bikes_sales.models

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sales.db"
app.config["SECRET_KEY"] = os.urandom(32)
app.config["WTF_CSRF_TIME_LIMIT"] = None
app.config["WTF_CSRF_SSL_STRICT"] = False
app.config["WTF_CSRF_ENABLED"] = False


db.init_app(app)
csrf.init_app(app)
 
 
# DEBUG 
 
def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True)