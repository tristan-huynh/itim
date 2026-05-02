from flask import Blueprint, redirect, render_template, session, url_for

from auth import oauth

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login')
def login_page():
    if session.get('user'):
        return redirect(url_for('scan.index'))
    return render_template('login.html')


@auth_bp.route('/login/oidc')
def login():
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.oidc.authorize_redirect(redirect_uri)


@auth_bp.route('/callback')
def callback():
    token = oauth.oidc.authorize_access_token()
    userinfo = token['userinfo']
    session['user'] = {
        'sub': userinfo['sub'],
        'email': userinfo.get('email', ''),
        'name': userinfo.get('name') or userinfo.get('email', 'Unknown'),
        'preferred_username': userinfo.get('preferred_username') or userinfo.get('email', 'Unknown'),
    }
    return redirect(url_for('scan.index'))


@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('scan.index'))
