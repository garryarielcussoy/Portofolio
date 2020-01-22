# Import
from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc
from blueprints import db, app
from blueprints.users.model import Users
from blueprints.books.model import Books
from blueprints.transaction.model import Transaction
from blueprints.transaction_detail.model import TransactionDetail
from datetime import datetime
import json

# Import Authentication
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import internal_required

# Create blueprint
bp_admin = Blueprint('admin', __name__)
api = Api(bp_admin)

class AdminUsers(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @jwt_required
    @internal_required
    def get(self):
        users_list = []
        users = Users.query
        for user in users:
            user = marshal(user, Users.users_fields)
            users_list.append(user)
        return users_list, 200
    
    @jwt_required
    @internal_required
    def delete(self):
        # Take input from admin
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', location = 'json', required = True)
        args = parser.parse_args()

        # Searching for the user
        target_user = Users.query.filter_by(user_id = args['user_id']).first()
        target_user.status = "terhapus"
        db.session.commit()

        # Delete all his/her books
        target_books = Books.query.filter_by(id_penjual = args['user_id'])
        for book in target_books:
            book.status = "terhapus"
        db.session.commit()

        return {"message": "Deleted"}, 200

class AdminTransaksi(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200

    # Show all transactions list
    @jwt_required
    @internal_required
    def get(self):
        all_transactions_data_to_show = []

        # Get all transactions
        all_transactions = Transaction.query
        
        # Get all transaction detail
        for transaction in all_transactions:
            transaction = marshal(transaction, Transaction.transaction_fields)
            transaction["detail_transaksi"] = []
            transactions_detail = TransactionDetail.query.filter_by(id_transaksi = transaction["id_transaksi"])

            for transaction_detail in transactions_detail:
                # Search for book
                target_book_title = Books.query.filter_by(id_buku = transaction_detail.id_buku).first().judul_buku
                
                transaction_detail = marshal(transaction_detail, TransactionDetail.transaction_detail_fields)
                transaction_detail["judul_buku"] = target_book_title
                transaction["detail_transaksi"].append(transaction_detail)
            
            all_transactions_data_to_show.append(transaction)
        
        return all_transactions_data_to_show, 200

api.add_resource(AdminUsers, '/users')
api.add_resource(AdminTransaksi, '/transaksi')