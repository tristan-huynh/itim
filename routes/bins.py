import secrets
import string

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from models import db, Bin, Crate


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

@bins_bp.route('/<tag>')
def detail(tag):
    bin_ = Bin.query.filter_by(tag=tag).first_or_404()
    all_bins = Bin.query.order_by(Bin.name).all()
    all_crates = Crate.query.order_by(Crate.name).all()
    return render_template('bin_detail.html', bin=bin_, all_bins=all_bins, all_crates=all_crates)


@bins_bp.route('/generate-tag')
def generate_tag():
    prefix = None
    parent_id = request.args.get('parent_id')
    if parent_id:
        parent = db.session.get(Bin, int(parent_id))
        if parent and '-' in parent.tag:
            prefix = parent.tag.split('-')[0]
    return jsonify(tag=_unique_bin_tag(prefix))


@bins_bp.route('/new', methods=['GET', 'POST'])
def new():
    all_bins = Bin.query.order_by(Bin.name).all()
    all_crates = Crate.query.order_by(Crate.name).all() 
    if request.method == 'POST':
        tag = request.form.get('tag', '').strip()
        name = request.form.get('name', '').strip()
        parent_id = request.form.get('parent_id') or None
        crate_id = request.form.get('crate_id') or None
        if not tag or not name:
            flash('Tag and name are required.', 'danger')
        elif not crate_id:
            flash('A crate must be selected.', 'danger')
        elif Bin.query.filter_by(tag=tag).first():
            flash('A bin with that tag already exists.', 'danger')
        else:
            bin_ = Bin(tag=tag, name=name, parent_id=parent_id, crate_id=crate_id)
            db.session.add(bin_)
            db.session.commit()
            return redirect(url_for('bins.detail', tag=bin_.tag))
    return render_template('bin_new.html', all_bins=all_bins, all_crates=all_crates)

@bins_bp.route('/<tag>/move', methods=['POST'])
def move(tag):
    bin_ = Bin.query.filter_by(tag=tag).first_or_404()
    new_parent = request.form.get('parent_id') or None
    if new_parent and int(new_parent) == bin_.id:
        flash('A bin cannot be its own parent.', 'danger')
    else:
        bin_.parent_id = new_parent
        db.session.commit()
    return redirect(url_for('bins.detail', tag=tag))


@bins_bp.route('/<tag>/move-crate', methods=['POST'])
def move_crate(tag):
    bin_ = Bin.query.filter_by(tag=tag).first_or_404()
    crate_id = request.form.get('crate_id') or None
    bin_.crate_id = crate_id
    db.session.commit()
    return redirect(url_for('bins.detail', tag=tag))


@bins_bp.route('/<tag>/delete', methods=['POST'])
def delete(tag):
    bin_ = Bin.query.filter_by(tag=tag).first_or_404()
    if bin_.children or bin_.assets:
        flash('Cannot delete a bin that still contains bins or assets.', 'danger')
        return redirect(url_for('bins.detail', tag=tag))
    db.session.delete(bin_)
    db.session.commit()
    return redirect(url_for('bins.list_bins'))
