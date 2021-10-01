import json

def test_getting_user_that_does_not_exist(test_client, init_database): 
    response = test_client.get('/user/user_not_in_db')
    
    data = json.loads(response.data)

    assert response.status_code == 200
    assert 'User does not exist' in data['message']

def test_getting_existing_user(test_client, init_database): 
    response = test_client.get('/user/user1')

    data = json.loads(response.data)

    assert response.status_code == 200
    assert 'User retrieved' in data['message']

def test_get_all_users(test_client, init_database): 
    response = test_client.get('/user/all')

    data = json.loads(response.data)

    assert response.status_code == 200
    assert 'User list retrieved' in data['message']
    assert 'user1' in data['data']['users']
    assert 'user2' in data['data']['users']

def test_create_new_user(test_client, init_database): 
    response = test_client.post('/user/create_this_user')

    data = json.loads(response.data)

    assert 'User created' in data['message']

def test_updating_user(test_client, init_database): 
    response = test_client.put('/user/user1')

    data = json.loads(response.data)

    assert 'Update not allowed' in data['message']
    
def test_deleting_user(test_client, init_database):
    response = test_client.delete('/user/user1')

    data = json.loads(response.data)

    assert 'User deleted' in data['message']
    assert 'user1' in data['data']['user']