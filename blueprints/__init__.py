# Import
import json, os
from flask import Flask, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims

# Import others
from datetime import timedelta
from functools import wraps

# Import CORS
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['APP_DEBUG'] = True

# JWT Setup
app.config['JWT_SECRET_KEY'] = 'iuahdLIXwaDOIXhodihowdoqd'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days = 1)
jwt = JWTManager(app)

# Admin Required
def internal_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['username'] != 'ADMIN':
            return {'status': 'FORBIDDEN', 'message': 'Admin Only'}, 403
        else:
            return fn(*args, **kwargs)
    return wrapper

def user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['username'] == 'ADMIN':
            return {'status': 'FORBIDDEN', 'message': 'User Only'}, 403
        else:
            return fn(*args, **kwargs)
    return wrapper

# DB Setup
env = os.environ.get('FLASK_ENV', 'development')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@0.0.0.0:3306/portofolio_test' if (env == 'testing') else 'mysql+pymysql://root:alta1234@portofolio.clrlyzuonr9k.ap-southeast-1.rds.amazonaws.com:3306/portofolio'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Form app.py
@app.after_request
def after_request(response):
    requestData = request.get_json()
    if response.status_code == 200:
        app.logger.info("REQUEST_LOG\t%s", json.dumps({
            'status_code': response.status_code,
            'method': request.method,
            'code': response.status,
            'url': request.full_path,
            'request': requestData,
            'response': json.loads(response.data.decode('utf-8'))
        }))
    else:
        app.logger.error("REQUEST_LOG\t%s", json.dumps({
            'status_code': response.status_code,
            'method': request.method,
            'code': response.status,
            'url': request.full_path,
            'request': requestData,
            'response': json.loads(response.data.decode('utf-8'))
        }))
    return response

# Routing
from blueprints.auth.__init__ import bp_auth
app.register_blueprint(bp_auth, url_prefix='')
from blueprints.users.resources import bp_users
app.register_blueprint(bp_users, url_prefix = '/users/profile')
from blueprints.books.resources import bp_books
app.register_blueprint(bp_books, url_prefix = '/users/buku')
from blueprints.public.__init__ import bp_public
app.register_blueprint(bp_public, url_prefix = '/public/buku')
from blueprints.admin.__init__ import bp_admin
app.register_blueprint(bp_admin, url_prefix = '/admin')
from blueprints.transaction.resources import bp_transaction
app.register_blueprint(bp_transaction, url_prefix = '/users/keranjang')

db.create_all()