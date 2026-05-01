from flask import Flask

from flask_migrate import Migrate
from models import db


def create_app():

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itim.db'
    
    db.init_app(app)
    Migrate(app, db)
    
    return app

app = create_app()