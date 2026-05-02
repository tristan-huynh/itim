import secrets
import string

from flask import Blueprint, render_template, request, redirect, url_for, flash, request, session
from models import db, Bin, Asset


def _unique_asset_tag(prefix=None):
    d, l = string.digits, string.ascii_uppercase

    while True:
        p = prefix or (secrets.choice(d) + secrets.choice(l))
        suffix = ''.join(secrets.choice(d) for _ in range(5)) + secrets.choice(l)
        tag = f'{p}-{suffix}'
        if not Asset.query.filter_by(asset_tag = tag).first():
            return tag
        
assets_bp = Blueprint('assets', __name__, url_prefix='/assets')


@assets_bp.route('/')
def list_assets():
    assets = Asset.query.order_by(Asset.name).all()
    return render_template('asset_list.html', assets=assets)


@assets_bp.route('/new', methods=['GET', 'POST'])
def new():
    all_bins = Bin.query.order_by(Bin.name).all()
    if request.method == 'POST':
        asset_tag = request.form.get('asset_tag', '').strip()
        name = request.form.get('name', '').strip()
        barcode = request.form.get('barcode', '').strip() or None
        bin_id = request.form.get('bin_id') or None
        if not asset_tag or not name:
            flash('Asset tag and name are required.', 'danger')
        elif Asset.query.filter_by(asset_tag=asset_tag).first():
            flash('An asset with that tag already exists.', 'danger')
        elif barcode and Asset.query.filter_by(barcode=barcode).first():
            flash('An asset with that barcode already exists.', 'danger')
        else:
            asset = Asset(
                asset_tag=asset_tag, name=name, barcode=barcode, bin_id=bin_id,
                created_by=session['user']['name'],
            )
            db.session.add(asset)
            db.session.commit()
            return redirect(url_for('assets.detail', asset_id=asset.id))
    return render_template('asset_new.html', all_bins=all_bins)
