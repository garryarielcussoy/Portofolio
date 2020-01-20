# Import
from blueprints import db
from flask_restful import fields
from datetime import datetime
from blueprints.users.model import Users
from blueprints.books.model import Books
from blueprints.transaction.model import Transaction

# Create Model
class TransactionDetail(db.Model):
    __tablename__ = 'transaction_detail'
    detail_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    id_transaksi = db.Column(db.Integer, db.ForeignKey('transaction.id_transaksi'), nullable = False)
    id_buku = db.Column(db.Integer, db.ForeignKey('books.id_buku'), nullable = False)
    jumlah_pembelian = db.Column(db.Integer, nullable = False)
    total_harga = db.Column(db.Integer, nullable = False)

    transaction_detail_fields = {
        'detail_id': fields.Integer,
        'id_transaksi': fields.Integer,
        'id_buku': fields.Integer,
        'jumlah_pembelian': fields.Integer,
        'total_harga': fields.Integer
    }

    def __init__(self, id_transaksi, id_buku, jumlah_pembelian, total_harga):
        self.id_transaksi = id_transaksi
        self.id_buku = id_buku
        self.jumlah_pembelian = jumlah_pembelian
        self.total_harga = total_harga