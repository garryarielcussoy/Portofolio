# Import
import pytest, json, logging
from flask import Flask, request

from blueprints import app, db
from blueprints.users.model import Users
from blueprints.books.model import Books
from blueprints.transaction.model import Transaction
from blueprints.transaction_detail.model import TransactionDetail
from app import cache
from datetime import datetime

# Password Encription
from password_strength import PasswordPolicy
import hashlib

# Creating dummy DB for testing purpose
def db_reset():
    db.drop_all()
    db.create_all()

    # ----- Creating 4 Users -----
    # Creating password
    password_1 = hashlib.md5("Garryac1".encode()).hexdigest()
    password_2 = hashlib.md5("budisetiawan".encode()).hexdigest()
    password_3 = hashlib.md5("nurhadialdo".encode()).hexdigest()
    password_4 = hashlib.md5("sandycheeks".encode()).hexdigest()

    # Creating users
    user_1 = Users(email = 'garryarielcussoy@gmail.com', username = 'garrycussoy', password = password_1, nama_lengkap = 'Garry Ariel', foto_profil = 'Kosong', alamat = 'Jl. Madrasah no. 44B, Bintaro, Jakarta Selatan', nomor_hp = '089514845202')
    db.session.add(user_1)
    db.session.commit()
    user_2 = Users(email = 'budisetiawan@gmail.com', username = 'budisetiawan', password = password_2, nama_lengkap = 'Budi Setiawan', foto_profil = 'Kosong', alamat = 'Jl. Maju Mundur no. 22, Kemajuan, Jakarta Selatan', nomor_hp = '085712344335')
    db.session.add(user_2)
    db.session.commit()
    user_3 = Users(email = 'nurhadialdo@gmail.com', username = 'nurhadialdo', password = password_3, nama_lengkap = 'Nurhadi Aldo', foto_profil = 'Kosong', alamat = 'Jl. ABC, Kebayoran, Jakarta Utara', nomor_hp = '085699998888')
    db.session.add(user_3)
    db.session.commit()
    user_4 = Users(email = 'sandycheeks@gmail.com', username = 'sandycheeks', password = password_4, nama_lengkap = 'Sandy Cheeks', foto_profil = 'Kosong', alamat = 'Jl. In Aja Dulu, Kebayoran, Jakarta Utara', nomor_hp = '085699997213')
    db.session.add(user_4)
    db.session.commit()

    # ----- Creating 3 Books -----
    book_1 = Books(id_penjual = 1, judul_buku = 'Materi dan Simulasi Olimpiade Sains Matematika', pengarang = 'Garry Ariel, Willy Sumarno', penerbit = 'PT. Jakarta Sains Media', nomor_isbn = '978-623-90766-1-0', deskripsi_buku = 'Buku ini berisi kumpulan materi dan soal latihan dalam rangka menyiapkan olimpiade sains bidang matematika', kategori = 'non-fiksi', foto_buku = 'Kosong', harga_satuan = 100000, stok = 30)
    db.session.add(book_1)
    db.session.commit()
    book_2 = Books(id_penjual = 1, judul_buku = 'Math is Fun', pengarang = 'Albert Einstein', penerbit = 'PT. Grameaku', nomor_isbn = '448-623-90751-3-2', deskripsi_buku = 'Matematika itu menyenangkan', kategori = 'non-fiksi', foto_buku = 'Kosong', harga_satuan = 77000, stok = 20)
    db.session.add(book_2)
    db.session.commit()
    book_3 = Books(id_penjual = 2, judul_buku = 'Trading Binomo', pengarang = 'Budi Setiawan', penerbit = 'PT. Suka-Suka', nomor_isbn = '123-321-90112-2-3', deskripsi_buku = 'Kiat-kiat sukses trading Binomo', kategori = 'fiksi', foto_buku = 'Kosong', harga_satuan = 40000, stok = 50)
    db.session.add(book_3)
    db.session.commit()
    book_4 = Books(id_penjual = 2, judul_buku = 'Buku Habis', pengarang = 'Budi Setiawan', penerbit = 'PT. Suka-Suka', nomor_isbn = '123-321-90112-2-4', deskripsi_buku = 'Buku kosong yang tidak ada isinya', kategori = 'fiksi', foto_buku = 'Kosong', harga_satuan = 10000, stok = 0)
    book_4.status = 'terhapus'
    db.session.add(book_4)
    db.session.commit()

    # ----- Creating Transactions -----
    # Add to cart only and not sent yet
    transaction_1 = Transaction(id_pembeli = 3, id_penjual = 1)
    db.session.add(transaction_1)
    db.session.commit()

    # The transaction has been sent, but has not been confirmed yet by the seller
    transaction_2 = Transaction(id_pembeli = 3, id_penjual = 1)
    transaction_2.waktu_pembelian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.session.add(transaction_2)
    db.session.commit()

    # The transaction has been accepted by seller
    transaction_3 = Transaction(id_pembeli = 3, id_penjual = 1)
    transaction_3.waktu_pembelian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction_3.waktu_konfirmasi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction_3.status = 'terima'
    db.session.add(transaction_3)
    db.session.commit()

    # The transaction has been rejected by seller
    transaction_4 = Transaction(id_pembeli = 3, id_penjual = 1)
    transaction_4.waktu_pembelian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction_4.waktu_konfirmasi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction_4.status = 'tolak'
    db.session.add(transaction_4)
    db.session.commit()

    # The transaction has been rejected by seller and there is a book which has 0 stock
    transaction_5 = Transaction(id_pembeli = 3, id_penjual = 2)
    transaction_5.waktu_pembelian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction_5.waktu_konfirmasi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaction_5.status = 'tolak'
    db.session.add(transaction_5)
    db.session.commit()

    # The transaction has not been sent and if sent, will make an item out of stock
    transaction_6 = Transaction(id_pembeli = 4, id_penjual = 1)
    db.session.add(transaction_6)
    db.session.commit()

    # ----- Creating Transactions Detail -----
    # Transaction 1
    detail_1 = TransactionDetail(id_transaksi = 1, id_buku = 1, jumlah_pembelian = 2, total_harga = 200000)
    db.session.add(detail_1)
    db.session.commit()
    detail_2 = TransactionDetail(id_transaksi = 1, id_buku = 2, jumlah_pembelian = 1, total_harga = 77000)
    db.session.add(detail_2)
    db.session.commit()

    # Transaction 2
    detail_3 = TransactionDetail(id_transaksi = 2, id_buku = 1, jumlah_pembelian = 2, total_harga = 200000)
    db.session.add(detail_3)
    db.session.commit()
    detail_4 = TransactionDetail(id_transaksi = 2, id_buku = 2, jumlah_pembelian = 1, total_harga = 77000)
    db.session.add(detail_4)
    db.session.commit()

    # Transaction 3
    detail_5 = TransactionDetail(id_transaksi = 3, id_buku = 1, jumlah_pembelian = 2, total_harga = 200000)
    db.session.add(detail_5)
    db.session.commit()
    detail_6 = TransactionDetail(id_transaksi = 3, id_buku = 2, jumlah_pembelian = 1, total_harga = 77000)
    db.session.add(detail_6)
    db.session.commit()

    # Transaction 4
    detail_7 = TransactionDetail(id_transaksi = 4, id_buku = 1, jumlah_pembelian = 2, total_harga = 200000)
    db.session.add(detail_7)
    db.session.commit()
    detail_8 = TransactionDetail(id_transaksi = 4, id_buku = 2, jumlah_pembelian = 1, total_harga = 77000)
    db.session.add(detail_8)
    db.session.commit()

    # Transaction 5
    detail_9 = TransactionDetail(id_transaksi = 5, id_buku = 4, jumlah_pembelian = 5, total_harga = 5000)
    db.session.add(detail_9)
    db.session.commit()

    # Transaction 6
    detail_10 = TransactionDetail(id_transaksi = 6, id_buku = 1, jumlah_pembelian = 30, total_harga = 3000000)
    db.session.add(detail_10)
    db.session.commit()

def call_client(request):
    client = app.test_client()
    return client

@pytest.fixture
def client(request):
    return call_client(request)

# Creating token
def create_token(username):
    # Checking whether admin or user and prepare the data
    if username == 'ADMIN':
        cachename = "test-admin-token"
        data = {
            'username': 'ADMIN',
            'password': 'ADMIN1234'
        }
    elif username == 'garrycussoy':
        cachename = "test-garry-token"
        data = {
            'username': 'garrycussoy',
            'password': 'Garryac1'
        }
    elif username == 'budisetiawan':
        cachename = "test-budi-token"
        data = {
            'username': 'budisetiawan',
            'password': 'budisetiawan'
        }
    elif username == 'nurhadialdo':
        cachename = "test-nurhadi-token"
        data = {
            'username': 'nurhadialdo',
            'password': 'nurhadialdo'
        }
    elif username == 'sandycheeks':
        cachename = "test-sandy-token"
        data = {
            'username': 'sandycheeks',
            'password': 'sandycheeks'
        }

    token = cache.get(cachename)
    if token is None:
        # Do Request
        req = call_client(request)
        res = req.post('/login', json = data, content_type='application/json')

        # Store Response
        res_json = json.loads(res.data)
        logging.warning('RESULT : %s', res_json)

        # Assertion
        assert res.status_code == 200

        # Save token into cache
        cache.set(cachename, res_json['token'], timeout = 60)

        # Return, because it is useful for other test
        return res_json['token']
    else:
        return token