# Import
from blueprints import db
from flask_restful import fields
from datetime import datetime

# Create Model
class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    email = db.Column(db.String(150), nullable = False, unique = True)
    username = db.Column(db.String(150), nullable = False, unique = True)
    password = db.Column(db.String(255), nullable = False)
    nama_lengkap = db.Column(db.String(255), nullable = False)
    foto_profil = db.Column(db.String(255), nullable = True)
    alamat = db.Column(db.String(255), nullable = False)
    nomor_hp = db.Column(db.String(15), nullable = False)
    tanggal_bergabung = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.String(8), default = None)

    users_fields = {
        'user_id': fields.Integer,
        'email': fields.String,
        'username': fields.String,
        'password': fields.String,
        'nama_lengkap': fields.String,
        'foto_profil': fields.String,
        'alamat': fields.String,
        'nomor_hp': fields.String,
        'tanggal_bergabung': fields.DateTime,
        'status': fields.String
    }

    jwt_claim_fields = {
        'username': fields.String,
        'password': fields.String
    }

    def __init__(self, email, username, password, nama_lengkap, foto_profil, alamat, nomor_hp):
        self.email = email
        self.username = username
        self.password = password
        self.nama_lengkap = nama_lengkap
        self.foto_profil = foto_profil
        self.alamat = alamat
        self.nomor_hp = nomor_hp
        self.tanggal_bergabung = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = None