# Import
from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from sqlalchemy import desc
from .model import Transaction
from blueprints import db, app
from blueprints.users.model import Users
from blueprints.books.model import Books
from blueprints.transaction_detail.model import TransactionDetail
from datetime import datetime
import json, os
import requests
from mailjet_rest import Client

# Import Authentication
from flask_jwt_extended import jwt_required, get_jwt_claims
from blueprints import internal_required, user_required

# Creating blueprint
bp_transaction = Blueprint('transaction', __name__)
api = Api(bp_transaction)

class KeranjangResource(Resource):
    # Enable CORS
    def options(self, id=None):
        return {'status': 'ok'}, 200

    # Show the active transaction
    @jwt_required
    @user_required
    def get(self):
        # Get buyer ID
        claims = get_jwt_claims()
        buyer = Users.query.filter_by(username = claims['username']).first()
        buyer_id = buyer.user_id

        # Search for active transaction
        active_transaction = Transaction.query.filter_by(id_pembeli = buyer_id).filter_by(waktu_pembelian = None).first()
        if active_transaction is None:
            return {"message": "Kamu belum menambahkan apapun ke keranjang", "data_transaksi": [], "can_send": False}, 200
        active_transaction_id = active_transaction.id_transaksi

        # Search for seller data
        seller_id = active_transaction.id_penjual
        seller = Users.query.filter_by(user_id = seller_id).first()
        seller = marshal(seller, Users.users_fields)

        # Search for all related detail transactions
        related_detail_transactions = TransactionDetail.query.filter_by(id_transaksi = active_transaction_id)

        # Get book information for each detail_transaction
        jumlah_pembelian = 0
        total_harga = 0
        transaction_data = []
        for detail_transaction in related_detail_transactions:
            jumlah_pembelian += detail_transaction.jumlah_pembelian
            total_harga += detail_transaction.total_harga
            detail_transaction = marshal(detail_transaction, TransactionDetail.transaction_detail_fields)
            
            # Find the book
            book_id = detail_transaction['id_buku']
            target_book = Books.query.filter_by(id_buku = book_id).first()
            target_book = marshal(target_book, Books.books_fields)

            # Append to transaction data
            transaction_data.append(
                {
                    'detail_transaksi': detail_transaction,
                    'informasi_buku': target_book
                }
            )

        # Define cart list to be shown
        cart_list = {
            "data_penjual": seller,
            "data_transaksi": transaction_data,
            "jumlah_pembelian": jumlah_pembelian,
            "total_harga": total_harga,
            "can_send": True
        }

        return cart_list, 200
    
    # Send the order to seller
    @jwt_required
    @user_required
    def put(self):
        # Get buyer ID
        claims = get_jwt_claims()
        buyer = Users.query.filter_by(username = claims['username']).first()
        buyer_id = buyer.user_id

        # Search for active transaction
        active_transaction = Transaction.query.filter_by(id_pembeli = buyer_id).filter_by(waktu_pembelian = None).first()
        if active_transaction is None:
            return {"message": "Tidak ada apapun dalam keranjang"}, 200
        active_transaction_id = active_transaction.id_transaksi

        # Search for all related detail transactions
        related_detail_transactions = TransactionDetail.query.filter_by(id_transaksi = active_transaction_id)
        
        # Checking whetehr the book is already out of stock or not
        for detail_transaction in related_detail_transactions:
            # Find the book
            book_id = detail_transaction.id_buku
            target_book = Books.query.filter_by(id_buku = book_id).first()
            if target_book.stok < detail_transaction.jumlah_pembelian:
                target_book = marshal(target_book, Books.books_fields)
                return {'message': 'Mohon maaf, buku dengan judul ' + target_book['judul_buku'] + ' yang kamu pesan melebihi stok yang tersedia saat ini.'}, 200

        # Update the transaction date
        active_transaction.waktu_pembelian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.commit()

        # Get book information for each detail_transaction
        for detail_transaction in related_detail_transactions:
            # Find the book
            book_id = detail_transaction.id_buku
            target_book = Books.query.filter_by(id_buku = book_id).first()
            
            # Update the book
            target_book.stok -= detail_transaction.jumlah_pembelian
            db.session.commit()
            if target_book.stok == 0:
                target_book.status = "terhapus"
                db.session.commit()
        
        # ---------- Send notification email to seller ----------
        # Searching for seller information
        seller_id = active_transaction.id_penjual
        seller = Users.query.filter_by(user_id = seller_id).first()
        
        # Prepare required data
        required_data = {
            "id_transaksi": str(active_transaction_id),
            "email_penjual": seller.email,
            "nama_penjual": seller.nama_lengkap,
            "nama_pembeli": buyer.nama_lengkap,
            "waktu_pembelian": active_transaction.waktu_pembelian.strftime("%Y-%m-%d %H:%M:%S")
        }

        # API configuration
        api_key = 'bb6a7959ba912ff930bfffac2036b568'
        api_secret = '0173c13cba0c2d75a2f1ac26e6adf2da'
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')

        # Preparing the body of the email
        first_greeting = "<h3>Halo " + required_data["nama_penjual"] + "</h3><br />Ada pesanan masuk nih dari <b>" + required_data["nama_pembeli"] + "</b>. Berikut ini detail pesanannya."
        main_content = "<h3>DETAIL PESANAN</h3>ID Transaksi : " + required_data["id_transaksi"] + "<br />Waktu Pembelian: " + required_data["waktu_pembelian"] + "<br />Pesanan:<br /><ul>"
        for detail_transaction in related_detail_transactions:
            book_id = detail_transaction.id_buku
            target_book = Books.query.filter_by(id_buku = book_id).first()
            main_content += "<li>" + target_book.judul_buku + " (Total Pembelian: " + str(detail_transaction.jumlah_pembelian) + ")</li>"
        main_content += "</ul>"
        final_greeting = "Segera konfirmasi ya supaya pembelimu tidak menunggu lama :D"

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
                "Email": required_data["email_penjual"],
                "Name": required_data["nama_penjual"]
                }
            ],
            "Subject": "Pesanan Masuk",
            "HTMLPart": first_greeting + main_content + final_greeting,
            "CustomID": "AppGettingStartedTest"
            }
        ]
        }
        
        # Send the email
        if 'FLASK_ENV' not in os.environ: os.environ['FLASK_ENV'] = 'development'
        if os.environ['FLASK_ENV'] == 'development': mailjet.send.create(data=data)
        
        return {"message": "Pesananmu sudah dikirim. Silahkan melakukan komunikasi dengan penjual. Terimakasih"}, 200

api.add_resource(KeranjangResource, '')