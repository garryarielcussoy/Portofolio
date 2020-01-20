# Import
from blueprints import db
from flask_restful import fields
from datetime import datetime
from blueprints.users.model import Users
from blueprints.books.model import Books

# Create Model
class Transaction(db.Model):
    __tablename__ = 'transaction'
    id_transaksi = db.Column(db.Integer, primary_key = True, autoincrement = True)
    id_pembeli = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    id_penjual = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    waktu_pembelian = db.Column(db.DateTime, default = None)
    waktu_konfirmasi = db.Column(db.DateTime, default = None)
    status = db.Column(db.String(8), default = None)

    transaction_fields = {
        'id_transaksi': fields.Integer,
        'id_pembeli': fields.Integer,
        'id_penjual': fields.Integer,
        'waktu_pembelian': fields.DateTime,
        'waktu_konfirmasi': fields.DateTime,
        'status': fields.String
    }

    def __init__(self, id_pembeli, id_penjual):
        self.id_pembeli = id_pembeli
        self.id_penjual = id_penjual
        self.waktu_pembelian = None
        self.waktu_konfirmasi = None
        self.status = None