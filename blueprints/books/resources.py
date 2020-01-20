# Import
from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc
from .model import Books
from blueprints import db, app
from blueprints.users.model import Users
from blueprints.transaction.model import Transaction
from blueprints.transaction_detail.model import TransactionDetail
from datetime import datetime
import json

# Import Authentication
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import internal_required, user_required

# Creating blueprint
bp_books = Blueprint('books', __name__)
api = Api(bp_books)

class BooksResource(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200

    # Get list of all books (can use filter)
    @jwt_required
    @user_required
    def get(self):
        # Take the parameter from user
        parser = reqparse.RequestParser()
        parser.add_argument('id_buku', location = 'args', required = False)
        parser.add_argument('judul_buku', location = 'args', required = False)
        parser.add_argument('username_penjual', location = 'args', required = False)
        parser.add_argument('penerbit', location = 'args', required = False)
        parser.add_argument('pengarang', location = 'args', required = False)
        parser.add_argument('nomor_isbn', location = 'args', required = False)
        parser.add_argument('kategori', location = 'args', required = False)
        args = parser.parse_args()

        # Get all books
        all_books = Books.query.filter_by(status = None)

        # Filter Proccess
        # By Book ID
        if args['id_buku'] != None:
            all_books = all_books.filter_by(id_buku = args['id_buku'])

        # By Book title
        if args['judul_buku'] != None:
            all_books = all_books.filter(Books.judul_buku.like("%" + args['judul_buku'] + "%"))

        # By Author
        if args['pengarang'] != None:
            all_books = all_books.filter(Books.pengarang.like("%" + args['pengarang'] + "%"))

        # By Publisher
        if args['penerbit'] != None:
            all_books = all_books.filter(Books.penerbit.like("%" + args['penerbit'] + "%"))

        # By ISBN number
        if args['nomor_isbn'] != None:
            all_books = all_books.filter_by(nomor_isbn = args['nomor_isbn'])

        # By seller username
        if args['username_penjual'] != None:
            target_user = Users.query.filter_by(username = args['username_penjual']).first()
            if target_user:
                user_id = target_user.user_id
                all_books = all_books.filter_by(id_penjual = user_id)
            else:
                return [], 200

        # By Category
        if args['kategori'] != None:
            all_books = all_books.filter_by(kategori = args['kategori'])

        # Showing the result
        filtered_books = []
        for book in all_books:
            book = marshal(book, Books.books_fields)

            # Searching for seller username
            user_id = book['id_penjual']
            seller = Users.query.filter_by(user_id = user_id).first()
            seller_username = seller.username
            book['username_penjual'] = seller_username

            filtered_books.append(book)
        return filtered_books[::-1], 200

class BooksResourceByID(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200
        
    # Detail Books Page
    @jwt_required
    @user_required
    def get(self, id):
        # Searching for the book
        book = Books.query.filter_by(id_buku = id).filter_by(status = None).first()

        # Checking whether the book exists or not
        if book is None:
            return {"message": "Buku yang kamu cari tidak ditemukan"}, 404

        book = marshal(book, Books.books_fields)

        # Searching for the seller
        seller_id = book["id_penjual"]
        seller = Users.query.filter_by(user_id = seller_id).first()
        seller = marshal(seller, Users.users_fields)

        # Result format to be shown
        book_detail = {
            "data_buku": book,
            "data_penjual": seller,
            "can_add": False,
            "placeholder_start": 0
        }

        # Check whether this book can be added to cart or not
        # Find buyer ID
        claims = get_jwt_claims()
        buyer = Users.query.filter_by(username = claims['username']).first()
        buyer_id = buyer.user_id

        # Searching for the transaction of related buyer
        buyer_transactions = Transaction.query.filter_by(id_pembeli = buyer_id)

        # Checking for active transaction
        active_transaction = buyer_transactions.filter_by(waktu_pembelian = None).first()
        if active_transaction is None:
            book_detail["can_add"] = True
        else:
            active_transaction_seller_id = active_transaction.id_penjual
            if active_transaction_seller_id == seller_id:
                book_detail["can_add"] = True

        # Check for related detail transactions
        if active_transaction is not None:
            active_transaction_id = active_transaction.id_transaksi
            related_detail_transactions = TransactionDetail.query.filter_by(id_transaksi = active_transaction_id).filter_by(id_buku = id).first()
            if related_detail_transactions is not None:
                book_detail['placeholder_start'] = related_detail_transactions.jumlah_pembelian

        # Check whether the owner of the book is the user himself/herself
        book_seller_id = book['id_penjual']
        if book_seller_id == buyer_id:
            book_detail['can_add'] = False

        return book_detail, 200

    # Add a book to cart
    @jwt_required
    @user_required
    def patch(self, id):
        # Take input from user
        parser = reqparse.RequestParser()
        parser.add_argument('jumlah_pembelian', location = 'json', required = True)
        args = parser.parse_args()
        jumlah_pembelian = args['jumlah_pembelian']

        # Check the input
        target_book = Books.query.filter_by(id_buku = id).first()
        if int(jumlah_pembelian) > target_book.stok:
            return {'message': 'Jumlah buku yang kamu inginkan melebihi stok yang tersedia'}, 422
        elif int(jumlah_pembelian) < 0:
            return {'message': 'Angka yang kamu masukkan haruslah berupa bilangan bulat non-negatif'}, 422
        
        # Find buyer ID
        claims = get_jwt_claims()
        buyer = Users.query.filter_by(username = claims['username']).first()
        buyer_id = buyer.user_id

        # Find seller ID
        seller_id = target_book.id_penjual

        # Searching for the transaction of related buyer
        buyer_transactions = Transaction.query.filter_by(id_pembeli = buyer_id)

        # Make a new active cart or continue using an active cart
        active_transaction = buyer_transactions.filter_by(waktu_pembelian = None).first()
        if active_transaction is None:
            # Make a new one
            active_transaction = Transaction(id_pembeli = buyer_id, id_penjual = seller_id)
            db.session.add(active_transaction)
            db.session.commit()
        transaction_id = active_transaction.id_transaksi
        
        # Searching for the related transaction detail
        transaction_detail_related = TransactionDetail.query.filter_by(id_transaksi = transaction_id)
        if transaction_detail_related.first() is None:
            # Must be greater than zero
            if int(jumlah_pembelian) == 0:
                return {"message": "Untuk memasukkan ke keranjang, kamu setidaknya harus membeli 1 buku"}, 200

            # Make a new transaction detail
            total_harga = target_book.harga_satuan * int(jumlah_pembelian)
            new_transaction_detail = TransactionDetail(id_transaksi = transaction_id, id_buku = id, jumlah_pembelian = jumlah_pembelian, total_harga = total_harga)
            db.session.add(new_transaction_detail)
            db.session.commit()
            return {"message": "Sukses menambahkan buku ke keranjang"}, 200
        else:
            # Make sure whether the book is already in cart or not
            book_transaction_related_status = False
            for detail_transaction in transaction_detail_related:
                if detail_transaction.id_buku == int(id):
                    book_transaction_related_status = True
                    detail_transaction_id = detail_transaction.detail_id
                    break

            if book_transaction_related_status == False:
                # Must be greater than zero
                if int(jumlah_pembelian) == 0:
                    return {"message": "Untuk memasukkan ke keranjang, kamu setidaknya harus membeli 1 buku"}, 200

                # Make a new one
                total_harga = target_book.harga_satuan * int(jumlah_pembelian)
                new_transaction_detail = TransactionDetail(id_transaksi = transaction_id, id_buku = id, jumlah_pembelian = jumlah_pembelian, total_harga = total_harga)
                db.session.add(new_transaction_detail)
                db.session.commit()
            
            else:
                # Update the related detail transaction
                active_detail_transaction = transaction_detail_related.filter_by(detail_id = detail_transaction_id).first()
                if int(jumlah_pembelian) != 0:
                    total_harga = target_book.harga_satuan * int(jumlah_pembelian)
                    active_detail_transaction.jumlah_pembelian = jumlah_pembelian
                    active_detail_transaction.total_harga = total_harga
                    db.session.commit()
                else:
                    # Delete the detail transaction
                    db.session.delete(active_detail_transaction)
                    db.session.commit()

                    # Checking whether the active transaction doesn't have transaction detail or not
                    filtered_detail_transaction = TransactionDetail.query.filter_by(id_transaksi = transaction_id).first()
                    if filtered_detail_transaction is None:
                        db.session.delete(active_transaction)
                        db.session.commit()

                    return {'message': 'Sukses menghapus buku dari keranjang'}, 200
            return {'message': 'Sukses menambahkan buku ke keranjang'}, 200

api.add_resource(BooksResource, '')
api.add_resource(BooksResourceByID, '/<id>')