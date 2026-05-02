from flask import Flask

from flask_migrate import Migrate
from models import db


def create_app():

    app = Flask(__name__, static_folder='assets')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itim.db'
    
    db.init_app(app)
    Migrate(app, db)
    
    from routes.scan import scan_bp
    from routes.bins import bins_bp
    from routes.assets import assets_bp
    from routes.crates import crates_bp

    app.register_blueprint(scan_bp)
    app.register_blueprint(bins_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(crates_bp)
    
    return app

app = create_app()