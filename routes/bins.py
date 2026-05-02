import secrets
import string

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from models import db, Bin, Asset


def _unique_bin_tag(prefix=None):
    d, l = string.digits, string.ascii_uppercase

    while True:
        p = prefix or (secrets.choice(d) + secrets.choice(l))
        suffix = ''.join(secrets.choice(d) for _ in range(5)) + secrets.choice(l)
        tag = f'{p}-{suffix}'
        if not Bin.query.filter_by(tag = tag).first():
            return tag

bins_bp = Blueprint('bins', __name__, url_prefix='/bins')

@bins_bp.route('/')
def list_bins():
    bins = Bin.query.filter_by(parent_id=None).order_by(Bin.name).all()
    return render_template('bin_list.html', bins=bins)

@bins_bp.route('/new', methods=['GET', 'POST'])
def new():
    all_bins  = Bin.query.order_by(Bin.name).all()
    if request.method == 'POST':
        tag = request.form.get('tag', '').strip()
        name = request.form.get('name', '').strip()
        parent_id = request.form.get('parent_id') or None
        if not tag or not name:
            flash('Tag and name are required.', 'danger')
        else:
            bin_ = Bin(tag=tag, name=name, parent_id=parent_id)
            db.session.add(bin_)
            db.session.commit()
            return redirect(url_for('bins.detail', bin_id=bin_.id))
    return render_template('bin_new.html', all_bins=all_bins)
