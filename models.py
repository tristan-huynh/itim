from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Crate(db.Model):
    __tablename__ = 'crate'

    id =        db.Column(db.Integer, primary_key=True)
    name =      db.Column(db.String(128), nullable=False)
    latitude =  db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    bins = db.relationship('Bin', backref='crate', lazy='select', order_by='Bin.name')

class Bin(db.Model):
    __tablename__ = 'bin'

    id =        db.Column(db.Integer, primary_key=True)
    tag =       db.Column(db.String(64), unique=True, nullable=False)
    name =      db.Column(db.String(128), nullable=False)
    crate_id =  db.Column(db.Integer, db.ForeignKey('crate.id'), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('bin.id'), nullable=True)
    last_scan = db.Column(db.DateTime, nullable=True)

    children = db.relationship('Bin', backref=db.backref('parent', remote_side=[id]), lazy='select', order_by='Bin.name')
    assets = db.relationship('Asset', backref='bin', lazy='select', order_by='Asset.name')

    def ancestors(self):
        path, node = [], self
        while node:
            path.append(node)
            node = node.parent
        return list(reversed(path))
    
    def breadcrumb(self):
        return self.ancestors() + [self]
    
class Asset(db.Model):
    __tablename__ = 'asset'

    id =        db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(64), unique=True, nullable=False)
    barcode =   db.Column(db.String(64), unique=True, nullable=True)
    serial_number = db.Column(db.String(128), nullable=True)
    name =      db.Column(db.String(128), nullable=False)
    bin_id =    db.Column(db.Integer, db.ForeignKey('bin.id'), nullable=True)
    last_scan = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.String(256), nullable=True)