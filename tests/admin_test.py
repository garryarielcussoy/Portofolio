import json
from . import app, client, cache, create_token, db_reset

class TestAdminUser():
    # Show all users data
    def test_admin_get_users(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('ADMIN')

        res = client.get('/admin/users', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200
    
    # Not an admin
    def test_not_admin(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('garrycussoy')

        res = client.get('/admin/users', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 403
    
    # Delete user
    def test_admin_delete_users(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('ADMIN')

        # JSON Body
        data = {'user_id': 1}

        res = client.delete('/admin/users', json = data, headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200

class TestAdminTransaksi():
    # Show all transactions data
    def test_admin_get_transactions(self, client):
        # Prepare the DB and token
        db_reset()
        token = create_token('ADMIN')

        res = client.get('/admin/transaksi', headers={'Authorization': 'Bearer ' + token})
        res_json = json.loads(res.data)
        assert res.status_code == 200