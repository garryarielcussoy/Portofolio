# Import Flask Tools
from flask import Blueprint
from flask_restful import Api, Resource, reqparse, marshal
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims

# Import Password Encription Tools
from password_strength import PasswordPolicy
import hashlib

# Import blueprint
from blueprints import app, db
from blueprints.users.model import Users

# Import ReGex
import re, json, os

# Import Mailjet
from mailjet_rest import Client

# Create blueprint
bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)

# Resource
class CreateTokenResource(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200

    # Create token while login
    def post(self):
        # Take username and password input
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        args = parser.parse_args()

        # Admin
        if args['username'] == 'ADMIN' and args['password'] == 'ADMIN1234':
            token = create_access_token(identity = args['username'], user_claims = {'username': args['username']})
            return {'token': token}, 200

        # Users
        else:
            password_digest = hashlib.md5(args['password'].encode()).hexdigest()
            qry = Users.query.filter_by(username = args['username']).filter_by(password = password_digest).filter_by(status = None)
            user_data = qry.first()
            if user_data is not None:
                token = create_access_token(identity = args['username'], user_claims = {'username': args['username']})
                return {'token': token}, 200
            return {'status': 'BAD REQUEST', 'message': 'Username atau password yang kamu masukkan salah'}, 400

class RegisterResource(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def post(self):
        # Take the required data from user
        parser = reqparse.RequestParser()
        parser.add_argument('email', location = 'json', required = True)
        parser.add_argument('username', location = 'json', required = True)
        parser.add_argument('password', location = 'json', required = True)
        parser.add_argument('confirm_password', location = 'json', required = True)
        parser.add_argument('nama_lengkap', location = 'json', required = True)
        parser.add_argument('foto_profil', location = 'json', required = False)
        parser.add_argument('alamat', location = 'json', required = True)
        parser.add_argument('nomor_hp', location = 'json', required = True)
        args = parser.parse_args()

        # ---------- Checking Format ----------
        # Email Format
        email_pattern = "^[A-Za-z][A-Za-z0-9_]*@[A-Za-z]+[.][A-Za-z]+([.][A-Za-z]+)?$"
        if not re.match(email_pattern, args['email']):
            return {'message': 'Email yang kamu masukkan tidak valid'}, 200 #422

        # Password Format (consists of minimum 6 characters)
        if len(args['password']) < 6:
            return {'message': 'Password minimal terdiri atas 6 karakter'}, 200 #400

        # Phone Format
        phone_pattern = "^0[0-9]{9,}$"
        if not re.match(phone_pattern, args['nomor_hp']):
            return {'message': 'Nomor handphone yang kamu masukkan tidak valid'}, 200 #422

        # Check if email or username has already in database
        all_users = Users.query
        for user in all_users:
            if user.email == args['email']:
                return {'message': 'Maaf, email tersebut sudah digunakan'}, 200 #409
            if user.username == args['username'] or args['username'] == 'ADMIN':
                return {'message': 'Maaf, username tersebut sudah digunakan'}, 200 #409

        # Confirm password
        if args['password'] != args['confirm_password']:
            return {'message': 'Coba periksa kembali password kamu'}, 200 #400

        # Creating the object and insert it to database
        password_digest = hashlib.md5(args['password'].encode()).hexdigest()
        new_user = Users(email = args['email'], username = args['username'], password = password_digest, nama_lengkap = args['nama_lengkap'], foto_profil = args['foto_profil'], alamat = args['alamat'], nomor_hp = args['nomor_hp'])
        db.session.add(new_user)
        db.session.commit()

        # API configuration
        api_key = 'bb6a7959ba912ff930bfffac2036b568'
        api_secret = '0173c13cba0c2d75a2f1ac26e6adf2da'
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')

        # Prepare the email to be sent
        data = {
        'Messages': [
            {
            "From": {
                "Email": "serbabuku96@gmail.com",
                "Name": "SerbaBuku"
            },
            "To": [
                {
                "Email": args["email"],
                "Name": args["nama_lengkap"]
                }
            ],
            "Subject": "Selamat Datang",
            "HTMLPart": "<h3>HALO " + args['nama_lengkap'] + "</h3>Selamat datang di SerbaBuku, surganya para pecinta buku.<br />Silahkan cari buku-buku yang sesuai seleramu, dan bagikan juga buku-buku yang kamu anggap menarik :D",
            "CustomID": "AppGettingStartedTest"
            }
        ]
        }
        
        # Send the email
        if 'FLASK_ENV' not in os.environ: os.environ['FLASK_ENV'] = 'development'
        if os.environ['FLASK_ENV'] == 'development': mailjet.send.create(data=data)

        # Show success message
        return {'message': 'Selamat! Akunmu sudah terdaftar sekarang'}, 200

# Add Resource
api.add_resource(CreateTokenResource, '/login')
api.add_resource(RegisterResource, '/register')