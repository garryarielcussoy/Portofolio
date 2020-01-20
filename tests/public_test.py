import json
from . import app, client, cache, create_token, db_reset

class TestPublicUser():
    # Get list all of books
    def test_get_all_books_without_parameter(self, client):
        # Prepare the DB
        db_reset()

        res = client.get('/public/buku')
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Get list all of books using filter
    def test_get_all_books_with_parameter(self, client):
        # Prepare the DB
        db_reset()

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

        res = client.get('/public/buku', query_string = data)
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Get list all of books using filter but nothing match
    def test_get_all_books_with_parameter_nothing_match(self, client):
        # Prepare the DB
        db_reset()

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

        res = client.get('/public/buku', query_string = data)
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Search book by ID and match the book
    def test_get_book_by_id_match(self, client):
        # Prepare the DB
        db_reset()

        res = client.get('/public/buku/1')
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Search book by ID and did not match any book
    def test_get_book_by_id_not_match(self, client):
        # Prepare the DB
        db_reset()

        res = client.get('/public/buku/10')
        res_json = json.loads(res.data)
        assert res.status_code == 404