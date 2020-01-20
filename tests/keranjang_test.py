import json
from unittest import mock
from unittest.mock import patch
from . import app, client, cache, create_token, db_reset

class TestKeranjang():
    # Show all books in cart
    def test_show_books_in_cart(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('nurhadialdo')

        res = client.get('/users/keranjang', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Empty cart
    def test_empty_cart(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        res = client.get('/users/keranjang', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Send a cart that is not empty
    def test_send_cart(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('nurhadialdo')

        res = client.put('/users/keranjang', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Send a cart that has a book stock < request
    def test_send_cart_stock_less_than_request(self, client):
        # Prepare the DB and token
        db_reset()
        token_user_1 = create_token('nurhadialdo')
        token_user_2 = create_token('sandycheeks')

        # Add to cart
        client.patch('/users/buku/1', json={'jumlah_pembelian': 20}, headers={'Authorization': 'Bearer ' + token_user_1})
        client.patch('/users/buku/1', json={'jumlah_pembelian': 20}, headers={'Authorization': 'Bearer ' + token_user_2})

        # Send the cart
        client.put('/users/keranjang', headers={'Authorization': 'Bearer ' + token_user_1})
        res = client.put('/users/keranjang', headers={'Authorization': 'Bearer ' + token_user_2})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Send a cart that is empty
    def test_send_empty_cart(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        res = client.put('/users/keranjang', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Send a cart that make an item out of stock
    def test_send_cart_make_out_of_stock(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('sandycheeks')

        res = client.put('/users/keranjang', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200