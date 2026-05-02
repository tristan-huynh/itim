from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from models import db, Bin, Asset
from datetime import datetime, timezone

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/', methods=['GET', 'POST'])
def index():
    result = None
    result_type = None
    error = None

    if request.method == 'POST':
        tag = request.form.get('tag', '').strip()
        if tag:
            asset = Asset.query.filter(
                (Asset.asset_tag == tag) | (Asset.barcode == tag)
            ).first()
            user = session.get('user', {}).get('preferred_username')
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            if asset:
                asset.last_scan = now
                asset.last_scanned_by = user
                db.session.commit()
                result = asset
                result_type = 'asset'
            else:
                bin_ = Bin.query.filter_by(tag=tag).first()
                if bin_:
                    bin_.last_scan = now
                    bin_.last_scanned_by = user
                    db.session.commit()
                    result = bin_
                    result_type = 'bin'
                else:
                    error = f'No record found for tag: {tag}'

    return render_template('scan.html', result=result, result_type=result_type, error=error)
