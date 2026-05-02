import secrets, string

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from models import db, Bin, Crate, Asset

crates_bp = Blueprint('crates', __name__, url_prefix='/crates')

@crates_bp.route('/')
def list_crates():
    crates = Crate.query.order_by(Crate.name).all()
    return render_template('crate_list.html', crates=crates)

@crates_bp.route('/<int:crate_id>')
def detail(crate_id):
    crate = db.get_or_404(Crate, crate_id)
    return render_template('crate_detail.html', crate=crate)

@crates_bp.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        lat = request.form.get('latitude', '').strip() or None
        lng = request.form.get('longitude', '').strip() or None
        if not name:
            flash('Name is required.', 'danger')
        else:
            try:
                crate = Crate(
                    name=name,
                    latitude=float(lat) if lat is not None else None,
                    longitude=float(lng) if lng is not None else None,
                )
                db.session.add(crate)
                db.session.commit()
                return redirect(url_for('crates.detail', crate_id=crate.id))
            except ValueError:
                flash('Latitude and longitude must be valid numbers.', 'danger')
    return render_template('crate_new.html')

@crates_bp.route('/<int:crate_id>/edit', methods=['GET', 'POST'])
def edit(crate_id):
    crate = db.get_or_404(Crate, crate_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        lat = request.form.get('latitude', '').strip() or None
        lng = request.form.get('longitude', '').strip() or None
        if not name:
            flash('Name is required.', 'danger')
        else:
            try:
                crate.name = name
                crate.latitude = float(lat) if lat is not None else None
                crate.longitude = float(lng) if lng is not None else None
                db.session.commit()
                return redirect(url_for('crates.detail', crate_id=crate.id))
            except ValueError:
                flash('Latitude and longitude must be valid numbers.', 'danger')
    return render_template('crate_edit.html', crate=crate)

@crates_bp.route('/<int:crate_id>/delete', methods=['POST'])
def delete(crate_id):
    crate = db.get_or_404(Crate, crate_id)
    if crate.bins:
        flash('Cannot delete a crate that still contains bins.', 'danger')
        return redirect(url_for('crates.detail', crate_id=crate_id))
    db.session.delete(crate)
    db.session.commit()
    return redirect(url_for('crates.list_crates'))

