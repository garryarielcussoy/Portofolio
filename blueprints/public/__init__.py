# Import
from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc
from blueprints import db, app
from blueprints.users.model import Users
from blueprints.books.model import Books
from datetime import datetime
import json

# Import Authentication
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import internal_required

# Creating blueprint
bp_public = Blueprint('public', __name__)
api = Api(bp_public)

class PublicResource(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200

    # Get list of all books (can use filter)
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

class PublicResourceByID(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200
    
    # Detail Books Page
    def get(self, id):
        # Searching for the book
        book = Books.query.filter_by(id_buku = id).filter_by(status = None).first()

        # Check whether the book exist or not
        if book is None:
            return {"message": "Buku yang kamu cari tidak ditemukan"}, 404

        book = marshal(book, Books.books_fields)

        # Searching for the seller
        seller_id = book["id_penjual"]
        seller = Users.query.filter_by(user_id = seller_id).first()
        seller = marshal(seller, Users.users_fields)

        # Show the result
        book_detail = {
            "data_buku": book,
            "data_penjual": seller
        }

        return book_detail, 200

api.add_resource(PublicResource, '')
api.add_resource(PublicResourceByID, '/<id>')