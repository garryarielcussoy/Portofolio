import json
from . import app, client, cache, create_token, db_reset

class TestBooksResource():
    # Admin try to access user part
    def test_admin_access_user(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('ADMIN')

        res = client.get('/users/buku', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 403
    
    # Get list all of books
    def test_users_get_all_books_without_parameter(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        res = client.get('/users/buku', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Get list all of books using filter
    def test_users_get_all_books_with_parameter(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        # JSON Body
        data = {
            'id_buku': 1,
            'judul_buku': 'Matematika',
            'pengarang': 'Garry',
            'penerbit': 'PT',
            'nomor_isbn': '978-623-90766-1-0',
            'username_penjual': 'garrycussoy',
            'kategori': 'Non-Fiksi'
        }

        res = client.get('/users/buku', query_string = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Get list all of books using filter but nothing match
    def test_users_get_all_books_with_parameter_nothing_match(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        # JSON Body
        data = {
            'id_buku': 1,
            'judul_buku': 'Matematika',
            'pengarang': 'Garry',
            'penerbit': 'PT',
            'nomor_isbn': '978-623-90766-1-0',
            'username_penjual': 'garry',
            'kategori': 'Non-Fiksi'
        }

        res = client.get('/users/buku', query_string = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200

class TestBooksResourceByID():
    # Book Detail Page (Accesed by different user)
    def test_show_book_detail_different_user(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        res = client.get('/users/buku/3', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Book Detail Page (Did not match any book)
    def test_show_book_detail_not_match(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        res = client.get('/users/buku/47', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 404

    # Book Detail Page (There is already a book in cart with the same seller)
    def test_show_book_detail_same_seller(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('nurhadialdo')

        res = client.get('/users/buku/1', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
        assert res_json['can_add'] == True
    
    # Book Detail Page (There is already a book in cart with the different seller)
    def test_show_book_detail_different_seller(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('nurhadialdo')

        res = client.get('/users/buku/3', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
        assert res_json['can_add'] == False
    
    # Book Detail Page (The user is the owner of the book)
    def test_show_book_detail_own_self(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        res = client.get('/users/buku/1', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
        assert res_json['can_add'] == False

    # Add book to cart (Normal flow)
    def test_add_to_cart_normal_flow(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('nurhadialdo')

        # JSON Body
        data = {'jumlah_pembelian': 3}

        res = client.patch('/users/buku/1', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
        assert res_json['message'] == 'Sukses menambahkan buku ke keranjang'
    
    # Add book to cart (Negative input)
    def test_add_to_cart_negative_input(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('nurhadialdo')

        # JSON Body
        data = {'jumlah_pembelian': -1}

        res = client.patch('/users/buku/1', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 422
        assert res_json['message'] == 'Angka yang kamu masukkan haruslah berupa bilangan bulat non-negatif'
    
    # Add book to cart (More than the stock)
    def test_add_to_cart_more_than_stock(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('nurhadialdo')

        # JSON Body
        data = {'jumlah_pembelian': 100}

        res = client.patch('/users/buku/1', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 422
        assert res_json['message'] == 'Jumlah buku yang kamu inginkan melebihi stok yang tersedia'
    
    # Add book to cart (Made new transaction)
    def test_add_to_cart_new_transaction(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('budisetiawan')

        # JSON Body
        data = {'jumlah_pembelian': 1}

        res = client.patch('/users/buku/1', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Add book to cart (Minimum 1 item active transaction)
    def test_add_to_cart_minimum_1_item_active_transaction(self, client):
        # Prepare the DB and token
        token = create_token('budisetiawan')

        # JSON Body
        data = {'jumlah_pembelian': 0}

        res = client.patch('/users/buku/2', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200

    # Add book to cart (Active transaction)
    def test_add_to_cart_active_transaction(self, client):
        # Prepare the DB and token
        token = create_token('budisetiawan')

        # JSON Body
        data = {'jumlah_pembelian': 1}

        res = client.patch('/users/buku/2', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200

    # Add book to cart (Cancel order)
    def test_add_to_cart_cancel_order(self, client):
        token = create_token('budisetiawan')

        # JSON Body
        data = {'jumlah_pembelian': 0}

        res = client.patch('/users/buku/1', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Add book to cart (Cancel transaction)
    def test_add_to_cart_cancel_transaction(self, client):
        token = create_token('budisetiawan')

        # JSON Body
        data = {'jumlah_pembelian': 0}

        res = client.patch('/users/buku/2', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200

    # Add book to cart (Minimum 1 item new transaction)
    def test_add_to_cart_minimum_1_item_new_transaction(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('budisetiawan')

        # JSON Body
        data = {'jumlah_pembelian': 0}

        res = client.patch('/users/buku/1', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200