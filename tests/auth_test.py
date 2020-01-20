import json
from . import app, client, cache, create_token, db_reset

class TestAuth():
    # Register session test for valid input 
    def test_register_valid(self, client):
        # Prepare the DB
        db_reset()

        # Prepare the data to be inputted
        data = {
            "email": "cauchyschwarz@gmail.com",
            "username": "cauchyschwarz",
            "password": "cauchyschwarz",
            "confirm_password": "cauchyschwarz",
            "nama_lengkap": "Cauchy Schwarz",
            "foto_profil": "Kosong Dulu",
            "alamat": "Bandung, Indonesia",
            "nomor_hp": '085210047623'
        }

        # Test the endpoints
        res = client.post('/register', json = data)
        res_json = json.loads(res.data)
        assert res.status_code == 200
        assert res_json['message'] == 'Selamat! Akunmu sudah terdaftar sekarang'
    
    # Register session test for dupliate email 
    def test_register_duplicate_email(self, client):
        # Prepare the DB
        db_reset()

        # Prepare the data to be inputted
        data = {
            "email": "garryarielcussoy@gmail.com",
            "username": "garrycussoy",
            "password": "Garryac1",
            "confirm_password": "Garryac1",
            "nama_lengkap": "Garry Ariel",
            "foto_profil": "Kosong Dulu",
            "alamat": "Jl. Madrasah no.44B, Bintaro, Pesanggrahan, Jakarta Selatan",
            "nomor_hp": '089514845202'
        }

        # Test the endpoints
        res = client.post('/register', json = data)
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Register session test for duplicate username 
    def test_register_duplicate_username(self, client):
        # Prepare the DB
        db_reset()

        # Prepare the data to be inputted
        data = {
            "email": "garry@alterra.id",
            "username": "garrycussoy",
            "password": "Garryac1",
            "confirm_password": "Garryac1",
            "nama_lengkap": "Garry Ariel",
            "foto_profil": "Kosong Dulu",
            "alamat": "Jl. Madrasah no.44B, Bintaro, Pesanggrahan, Jakarta Selatan",
            "nomor_hp": '089514845202'
        }

        # Test the endpoints
        res = client.post('/register', json = data)
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Register session test invalid email 
    def test_register_invalid_email(self, client):
        # Prepare the DB
        db_reset()

        # Prepare the data to be inputted
        data = {
            "email": "garry@alterra",
            "username": "garrycussoy",
            "password": "Garryac1",
            "confirm_password": "Garryac1",
            "nama_lengkap": "Garry Ariel",
            "foto_profil": "Kosong Dulu",
            "alamat": "Jl. Madrasah no.44B, Bintaro, Pesanggrahan, Jakarta Selatan",
            "nomor_hp": '089514845202'
        }

        # Test the endpoints
        res = client.post('/register', json = data)
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Register session test for invalid phone number 
    def test_register_invalid_phone(self, client):
        # Prepare the DB
        db_reset()

        # Prepare the data to be inputted
        data = {
            "email": "garry@alterra.id",
            "username": "garrycussoy",
            "password": "Garryac1",
            "confirm_password": "Garryac1",
            "nama_lengkap": "Garry Ariel",
            "foto_profil": "Kosong Dulu",
            "alamat": "Jl. Madrasah no.44B, Bintaro, Pesanggrahan, Jakarta Selatan",
            "nomor_hp": '089514845'
        }

        # Test the endpoints
        res = client.post('/register', json = data)
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Register session test where password contains less than 6 characters 
    def test_register_invalid_password(self, client):
        # Prepare the DB
        db_reset()

        # Prepare the data to be inputted
        data = {
            "email": "garry@alterra.id",
            "username": "garrycussoy",
            "password": "Garry",
            "confirm_password": "Garryac1",
            "nama_lengkap": "Garry Ariel",
            "foto_profil": "Kosong Dulu",
            "alamat": "Jl. Madrasah no.44B, Bintaro, Pesanggrahan, Jakarta Selatan",
            "nomor_hp": '089514845202'
        }

        # Test the endpoints
        res = client.post('/register', json = data)
        res_json = json.loads(res.data)
        assert res.status_code == 200

    # Register session test where password different to confirm password 
    def test_register_different_confirm_password(self, client):
        # Prepare the DB
        db_reset()

        # Prepare the data to be inputted
        data = {
            "email": "garry@alterra.com",
            "username": "garrycussoy123",
            "password": "Garryac",
            "confirm_password": "Garryac1",
            "nama_lengkap": "Garry Ariel",
            "foto_profil": "Kosong Dulu",
            "alamat": "Jl. Madrasah no.44B, Bintaro, Pesanggrahan, Jakarta Selatan",
            "nomor_hp": '089514845202'
        }

        # Test the endpoints
        res = client.post('/register', json = data)
        res_json = json.loads(res.data)
        assert res.status_code == 200

    # Login session test for valid user 
    def test_login_valid_user(self, client):
        # Prepare the DB
        db_reset()

        # Prepare the data to be inputted
        data = {
            "username": "garrycussoy",
            "password": "Garryac1",
        }

        # Test the endpoints
        res = client.post('/login', json = data)
        res_json = json.loads(res.data)
        assert res.status_code == 200

    # Login session test for admin 
    def test_login_admin(self, client):
        # Prepare the DB
        db_reset()

        # Prepare the data to be inputted
        data = {
            "username": "ADMIN",
            "password": "ADMIN1234",
        }

        # Test the endpoints
        res = client.post('/login', json = data)
        res_json = json.loads(res.data)
        assert res.status_code == 200

    # Login session test for invalid user 
    def test_login_invalid_user(self, client):
        # Prepare the DB
        db_reset()

        # Prepare the data to be inputted
        data = {
            "username": "patrick_star",
            "password": "PatrickStar",
        }

        # Test the endpoints
        res = client.post('/login', json = data)
        res_json = json.loads(res.data)
        assert res.status_code == 400
        assert res_json['status'] == 'BAD REQUEST'