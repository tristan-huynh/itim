import os
from dotenv import load_dotenv

from flask import Flask, redirect, request, session, url_for

from flask_migrate import Migrate
from models import db
from auth import oauth

load_dotenv()

def create_app():

    app = Flask(__name__, static_folder='assets', static_url_path='/static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///itim.db'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 24 * 3600  # 1 day

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me')
    app.config['OIDC_CLIENT_ID'] = os.environ.get('OIDC_CLIENT_ID', '')
    app.config['OIDC_CLIENT_SECRET'] = os.environ.get('OIDC_CLIENT_SECRET', '')
    app.config['OIDC_DISCOVERY_URL'] = os.environ.get('OIDC_DISCOVERY_URL', '')

    db.init_app(app)
    Migrate(app, db)
    
    oauth.init_app(app)
    oauth.register(
        name='oidc',
        client_id=app.config['OIDC_CLIENT_ID'],
        client_secret=app.config['OIDC_CLIENT_SECRET'],
        server_metadata_url=app.config['OIDC_DISCOVERY_URL'],
        client_kwargs={'scope': 'openid email profile'},
    )


    from routes.scan import scan_bp
    from routes.bins import bins_bp
    from routes.assets import assets_bp
    from routes.crates import crates_bp
    from routes.auth import auth_bp

    app.register_blueprint(scan_bp)
    app.register_blueprint(bins_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(crates_bp)
    app.register_blueprint(auth_bp)

    @app.before_request
    def require_login():
        public = {'auth.login_page', 'auth.login', 'auth.callback', 'static'}
        if request.endpoint not in public and not session.get('user'):
            return redirect(url_for('auth.login_page'))

    @app.context_processor
    def inject_current_user():
        return {'current_user': session.get('user')}

    return app

app = create_app()