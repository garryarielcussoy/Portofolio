import json
from . import app, client, cache, create_token, db_reset

class TestUsersProfile():
    # Test for showing user profile without shopping history
    def test_show_profile_without_shopping_history(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        res = client.get('/users/profile', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Test for showing user profile with shopping history
    def test_show_profile_with_shopping_history(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('nurhadialdo')

        res = client.get('/users/profile', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Test for accepting order
    def test_accept_order(self,client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        # JSON Body
        data = {
            'transaction_id': 2,
            'status': 'terima'
        }

        res = client.post('/users/profile', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Test for rejecting order
    def test_reject_order(self,client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        # JSON Body
        data = {
            'transaction_id': 2,
            'status': 'tolak'
        }

        res = client.post('/users/profile', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Test for rejecting order with a zero stock book
    def test_reject_order_zero_stock(self,client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        # JSON Body
        data = {
            'transaction_id': 5,
            'status': 'tolak'
        }

        res = client.post('/users/profile', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200

class TestUsersProfileAddBook():
    # Test add new book by user
    def test_add_new_book(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        # JSON Body
        data = {
            "judul_buku": "Celetuk",
            "pengarang": "Lelianto Eko Pradana",
            "penerbit": "Ellunar Publisher",
            "nomor_isbn": "978-623-204-269-8 ",
            "deskripsi_buku": "Buku ini berisi materi dan soal-soal latihan (disertai pembahasan) untuk persiapan olimpiade matematika tingkat SMA",
            "kategori": "Non-Fiksi",
            "foto_buku": "Kosong Dulu",
            "harga_satuan": 100000,
            "stok": 10
        }

        res = client.post('/users/profile/tambah', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Test add duplicate book by user
    def test_add_duplicate_book(self, client):
        # Prepare the token
        token = create_token('garrycussoy')

        # JSON Body
        data = {
            "judul_buku": "Celetuk",
            "pengarang": "Lelianto Eko Pradana",
            "penerbit": "Ellunar Publisher",
            "nomor_isbn": "978-623-204-269-8 ",
            "deskripsi_buku": "Buku ini berisi materi dan soal-soal latihan (disertai pembahasan) untuk persiapan olimpiade matematika tingkat SMA",
            "kategori": "Non-Fiksi",
            "foto_buku": "Kosong Dulu",
            "harga_satuan": 100000,
            "stok": 10
        }

        res = client.post('/users/profile/tambah', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 409

class TestUsersProfileEditBook():
    # Get a book to be editted
    def test_get_edit_book(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        res = client.get('/users/profile/edit-buku/1', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Get a book but using invalid ID Book
    def test_get_edit_book_invalid(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        res = client.get('/users/profile/edit-buku/3', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 404
    
    # Edit a book
    def test_put_edit_book(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        # JSON Body
        data = {
            "judul_buku": "Celetuk",
            "pengarang": "Lelianto Eko Pradana",
            "penerbit": "Ellunar Publisher",
            "nomor_isbn": "978-623-204-269-8 ",
            "deskripsi_buku": "Buku ini berisi materi dan soal-soal latihan (disertai pembahasan) untuk persiapan olimpiade matematika tingkat SMA",
            "kategori": "Non-Fiksi",
            "foto_buku": "Kosong Dulu",
            "harga_satuan": 100000,
            "stok": 10
        }

        res = client.put('/users/profile/edit-buku/1', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200