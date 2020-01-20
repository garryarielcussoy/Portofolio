# Import
from blueprints import db
from flask_restful import fields
from datetime import datetime
from blueprints.users.model import Users

# Create Model
class Books(db.Model):
    __tablename__ = 'books'
    id_buku = db.Column(db.Integer, primary_key = True, autoincrement = True)
    id_penjual = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    judul_buku = db.Column(db.String(255), nullable = False)
    pengarang = db.Column(db.String(255), nullable = False)
    penerbit = db.Column(db.String(255), nullable = False)
    nomor_isbn = db.Column(db.String(255), nullable = True)
    deskripsi_buku = db.Column(db.String(255), nullable = True)
    kategori = db.Column(db.String(255), nullable = False)
    foto_buku = db.Column(db.String(255), nullable = False)
    harga_satuan = db.Column(db.Integer, nullable = False)
    stok = db.Column(db.Integer, nullable = False)
    tanggal_unggah = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.String(8), default = None)

    books_fields = {
        'id_buku': fields.Integer,
        'id_penjual': fields.Integer,
        'judul_buku': fields.String,
        'pengarang': fields.String,
        'penerbit': fields.String,
        'nomor_isbn': fields.String,
        'deskripsi_buku': fields.String,
        'kategori': fields.String,
        'foto_buku': fields.String,
        'harga_satuan': fields.Integer,
        'stok': fields.Integer,
        'tanggal_unggah': fields.DateTime,
        'status': fields.String
    }

    def __init__(self, id_penjual, judul_buku, pengarang, penerbit, deskripsi_buku, kategori, foto_buku, harga_satuan, stok, nomor_isbn = None):
        self.id_penjual = id_penjual
        self.judul_buku = judul_buku
        self.pengarang = pengarang
        self.penerbit = penerbit
        self.nomor_isbn = nomor_isbn
        self.deskripsi_buku = deskripsi_buku
        self.kategori = kategori
        self.foto_buku = foto_buku
        self.harga_satuan = harga_satuan
        self.stok = stok
        self.tanggal_unggah = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = None