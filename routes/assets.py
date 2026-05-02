import secrets
import string

from flask import Blueprint, render_template, request, redirect, url_for, flash, request, session, jsonify
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

@assets_bp.route('/<tag>')
def detail(tag):
    asset = Asset.query.filter_by(asset_tag=tag).first_or_404()
    all_bins = Bin.query.order_by(Bin.name).all()
    return render_template('asset_detail.html', asset=asset, all_bins=all_bins)

@assets_bp.route('/generate-tag')
def generate_tag():
    prefix = None
    bin_id = request.args.get('bin_id')
    if bin_id:
        bin_ = db.session.get(Bin, int(bin_id))
        if bin_ and '-' in bin_.tag:
            prefix = bin_.tag.split('-')[0]
    return jsonify(tag=_unique_asset_tag(prefix))


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
            )
            db.session.add(asset)
            db.session.commit()
            return redirect(url_for('assets.detail', tag=asset.asset_tag))
    return render_template('asset_new.html', all_bins=all_bins)


@assets_bp.route('/<tag>/move', methods=['POST'])
def move(tag):
    asset = Asset.query.filter_by(asset_tag=tag).first_or_404()
    asset.bin_id = request.form.get('bin_id') or None
    db.session.commit()
    return redirect(url_for('assets.detail', tag=tag))


@assets_bp.route('/<tag>/delete', methods=['POST'])
def delete(tag):
    asset = Asset.query.filter_by(asset_tag=tag).first_or_404()
    db.session.delete(asset)
    db.session.commit()
    return redirect(url_for('assets.list_assets'))