# Import
from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc
from .model import Users
from blueprints import db, app
from blueprints.books.model import Books
from blueprints.transaction.model import Transaction
from blueprints.transaction_detail.model import TransactionDetail
from datetime import datetime
import json

# Import Authentication
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import internal_required, user_required

# Password Encription
from password_strength import PasswordPolicy
import hashlib

# Creating blueprint
bp_users = Blueprint('users', __name__)
api = Api(bp_users)

class UsersProfile(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200
    
    # Get the profile of a user, his/her books, notifications, and shopping history
    @jwt_required
    @user_required
    def get(self):
        # Define dictionary to store the data
        user_profile = {}

        # Searching for the user
        claims = get_jwt_claims()
        target_user = Users.query.filter_by(username = claims['username']).first()
        target_user = marshal(target_user, Users.users_fields)

        # Searching for his/her books
        user_books_raw = Books.query.filter_by(id_penjual = target_user['user_id'])
        user_books = []

        # Filter book with status none or stock zero
        for user_book in user_books_raw:
            if user_book.stok == 0 or user_book.status == None:
                user_books.append(user_book)

        user_books_marshalled = []
        for book in user_books:
            book = marshal(book, Books.books_fields)
            user_books_marshalled.append(book)
        
        # Searching for active order transactions
        active_order_transactions = []
        all_seller_transactions = Transaction.query.filter_by(id_penjual = target_user['user_id'])
        for seller_transaction in all_seller_transactions:
            if seller_transaction.waktu_pembelian != None and seller_transaction.waktu_konfirmasi == None:
                # Searching for buyer
                buyer = Users.query.filter_by(user_id = seller_transaction.id_pembeli).first()
                buyer = marshal(buyer, Users.users_fields)

                active_order_transactions.append({
                    "waktu_masuk_pesanan": seller_transaction.waktu_pembelian.strftime("%Y-%m-%d %H:%M:%S"),
                    "id_transaksi": seller_transaction.id_transaksi,
                    "data_pembeli": buyer
                })
        
        # Searching every related transactions detail
        all_order_lists = []
        for order in active_order_transactions:
            all_related_transactions_detail = TransactionDetail.query.filter_by(id_transaksi = order['id_transaksi'])
            detail_transaction_dict = {
                    "waktu_masuk_pesanan": order["waktu_masuk_pesanan"],
                    "data_pembeli": order["data_pembeli"],
                    "id_transaksi": order["id_transaksi"],
                    "detail_transaksi": [],
                    "jumlah_pembelian": 0,
                    "total_harga": 0
            }
            
            jumlah_pembelian_transaksi = 0
            total_harga_transaksi = 0

            for related_transaction_detail in all_related_transactions_detail:
                # Searching related book
                targeted_book = Books.query.filter_by(id_buku = related_transaction_detail.id_buku).first()

                related_transaction_detail = marshal(related_transaction_detail, TransactionDetail.transaction_detail_fields)
                related_transaction_detail['judul_buku'] = targeted_book.judul_buku
                detail_transaction_dict['detail_transaksi'].append(related_transaction_detail)
                jumlah_pembelian_transaksi += related_transaction_detail['jumlah_pembelian']
                total_harga_transaksi += related_transaction_detail['total_harga']
            
            detail_transaction_dict['jumlah_pembelian'] = jumlah_pembelian_transaksi
            detail_transaction_dict['total_harga'] = total_harga_transaksi

            all_order_lists.append(detail_transaction_dict)

        # Searching for shopping history
        all_buyer_transactions = Transaction.query.filter_by(id_pembeli = target_user['user_id'])
        buyer_transactions_sent = []
        for buyer_transaction in all_buyer_transactions:
            if buyer_transaction.waktu_pembelian != None:
                buyer_transactions_sent.append(buyer_transaction)

        # Search all related transactions detail
        transaction_data = []
        for buyer_transaction in buyer_transactions_sent:
            # Searching for buyer name
            targeted_seller = Users.query.filter_by(user_id = buyer_transaction.id_penjual).first()
            targeted_seller_name = targeted_seller.username

            transaction_data.append({
                "waktu_pembelian": buyer_transaction.waktu_pembelian.strftime("%Y-%m-%d %H:%M:%S"),
                "id_transaksi": buyer_transaction.id_transaksi,
                "id_penjual": buyer_transaction.id_penjual,
                "nama_penjual": targeted_seller_name,
                "status": buyer_transaction.status
            })
        
        # Create the history
        history_lists = []
        for data in transaction_data:
            all_related_transactions_detail = TransactionDetail.query.filter_by(id_transaksi = data['id_transaksi'])

            detail_transaction_dict = {
                    "waktu_pembelian": data["waktu_pembelian"],
                    "id_penjual": data["id_penjual"],
                    "nama_penjual": data["nama_penjual"],
                    "id_transaksi": data["id_transaksi"],
                    "detail_transaksi": [],
                    "jumlah_pembelian": 0,
                    "total_harga": 0,
                    "status": data['status']
            }
            
            jumlah_pembelian_transaksi = 0
            total_harga_transaksi = 0

            for related_transaction_detail in all_related_transactions_detail:
                # Searching for the books
                targeted_book_title = Books.query.filter_by(id_buku = related_transaction_detail.id_buku).first().judul_buku
                
                related_transaction_detail = marshal(related_transaction_detail, TransactionDetail.transaction_detail_fields)
                related_transaction_detail['judul_buku'] = targeted_book_title
                detail_transaction_dict['detail_transaksi'].append(related_transaction_detail)
                jumlah_pembelian_transaksi += related_transaction_detail['jumlah_pembelian']
                total_harga_transaksi += related_transaction_detail['total_harga']
            
            detail_transaction_dict['jumlah_pembelian'] = jumlah_pembelian_transaksi
            detail_transaction_dict['total_harga'] = total_harga_transaksi

            history_lists.append(detail_transaction_dict)

        # Storing user data, his/her books, his/her history of shopping, and notifications in dictionary mentioned before
        user_profile['user_data'] = target_user
        user_profile['new_order'] = all_order_lists
        user_profile['books'] = user_books_marshalled
        user_profile['history_belanja'] = history_lists

        return user_profile, 200

    # Accept or reject order
    @jwt_required
    @user_required
    def post(self):
        # Take user input
        parser = reqparse.RequestParser()
        parser.add_argument('transaction_id', location = 'json', required = True)
        parser.add_argument('status', location = 'json', required = True)
        args = parser.parse_args()

        # Confirm an order
        transaction_target = Transaction.query.filter_by(id_transaksi = args['transaction_id']).first()
        transaction_target.waktu_konfirmasi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()

        # Accept order
        if args['status'] == 'terima':
            transaction_target.status = "terima"
            db.session.commit()
            return {"message": "Pesanan kamu terima. Silahkan melakukan komunikasi dengan pembeli untuk pembayaran dan pengiriman"}
        
        # Reject order
        elif args['status'] == 'tolak':
            transaction_target.status = "tolak"
            db.session.commit()

        # Searching for all related transactions detail
        related_detail_transactions = TransactionDetail.query.filter_by(id_transaksi = args['transaction_id'])

        # Get book information for each detail_transaction
        for detail_transaction in related_detail_transactions:
            # Find the book
            book_id = detail_transaction.id_buku
            target_book = Books.query.filter_by(id_buku = book_id).first()
            
            # Update the book
            if target_book.stok == 0:
                target_book.status = None
                db.session.commit()
            
            target_book.stok += detail_transaction.jumlah_pembelian
            db.session.commit()
        
        return {"message": "Pesanan ditolak. Silahkan hubungi pembeli agar pembelimu tidak kecewa"}, 200

class UsersProfileAddBook(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200
    
    # Add book from user
    @jwt_required    
    @user_required
    def post(self):
        # Get the user ID
        claims = get_jwt_claims()
        target_user = Users.query.filter_by(username = claims['username']).first()
        target_user = marshal(target_user, Users.users_fields)
        id_penjual = target_user['user_id']

        # Take input from user
        parser = reqparse.RequestParser()
        parser.add_argument('judul_buku', location = 'json', required = True)
        parser.add_argument('pengarang', location = 'json', required = True)
        parser.add_argument('penerbit', location = 'json', required = True)
        parser.add_argument('nomor_isbn', location = 'json', required = False)
        parser.add_argument('deskripsi_buku', location = 'json', required = True)
        parser.add_argument('kategori', location = 'json', required = True)
        parser.add_argument('foto_buku', location = 'json', required = True)
        parser.add_argument('harga_satuan', location = 'json', required = True)
        parser.add_argument('stok', location = 'json', required = True)
        args = parser.parse_args()

        # Check for duplication
        duplication_status = False
        user_books = Books.query.filter_by(id_penjual = id_penjual)
        for book in user_books:
            book = marshal(book, Books.books_fields)
            if (book['judul_buku'] == args['judul_buku'] and book['pengarang'] == args['pengarang'] and book['penerbit'] == args['penerbit'] and book['status'] == None):
                duplication_status = True
                return {'message': 'Buku ini sudah ada dalam daftar buku yang kamu jual saat ini'}, 409

        # Creating the object and store it to database
        new_book = Books(id_penjual = id_penjual, judul_buku = args['judul_buku'], pengarang = args['pengarang'], penerbit = args['penerbit'], nomor_isbn = args['nomor_isbn'], deskripsi_buku = args['deskripsi_buku'], kategori = args['kategori'], foto_buku = args['foto_buku'], harga_satuan = args['harga_satuan'], stok = args['stok'])
        db.session.add(new_book)
        db.session.commit()

        return {'message': 'Success'}, 200

class UsersProfileEditBook(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200

    # Get book data to be shown in placeholder
    @jwt_required
    @user_required
    def get(self, id):
        # Get user ID
        claims = get_jwt_claims()
        target_user = Users.query.filter_by(username = claims['username']).first()
        user_id = target_user.user_id

        # Searching for the book
        target_book = Books.query.filter_by(id_penjual = user_id).filter_by(id_buku = id).first()
        
        # Checking whether the book exists or not
        if target_book is None:
            return {'message': 'Buku yang kamu cari tidak ditemukan'}, 404

        target_book = marshal(target_book, Books.books_fields)
        return target_book, 200
    
    # Delete a book
    @jwt_required
    @user_required
    def delete(self, id):
        # Searching for the book
        target_book = Books.query.filter_by(id_buku = id).first()

        # Change the status and commit
        target_book.status = 'terhapus'
        db.session.commit()

        return {'message': 'Success'}, 200

    # Edit a book
    @jwt_required
    @user_required
    def put(self, id):
        # Take the input from user
        parser = reqparse.RequestParser()
        parser.add_argument('judul_buku', location = 'json', required = True)
        parser.add_argument('pengarang', location = 'json', required = True)
        parser.add_argument('penerbit', location = 'json', required = True)
        parser.add_argument('nomor_isbn', location = 'json', required = False)
        parser.add_argument('deskripsi_buku', location = 'json', required = True)
        parser.add_argument('kategori', location = 'json', required = True)
        parser.add_argument('foto_buku', location = 'json', required = True)
        parser.add_argument('harga_satuan', location = 'json', required = True)
        parser.add_argument('stok', location = 'json', required = True)
        args = parser.parse_args()

        # Searching for the book
        target_book = Books.query.filter_by(id_buku = id).first()
        
        # Edit the book
        target_book.judul_buku = args['judul_buku']
        target_book.pengarang = args['pengarang']
        target_book.penerbit = args['penerbit']
        target_book.nomor_isbn = args['nomor_isbn']
        target_book.deskripsi_buku = args['deskripsi_buku']
        target_book.kategori = args['kategori']
        target_book.foto_buku = args['foto_buku']
        target_book.harga_satuan = args['harga_satuan']
        target_book.stok = args['stok']
        target_book.status = None

        # Update the book
        db.session.commit()

        return {'message': 'Success'}, 200

api.add_resource(UsersProfile, '')
api.add_resource(UsersProfileAddBook, '/tambah')
api.add_resource(UsersProfileEditBook, '/edit-buku/<id>')