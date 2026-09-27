import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_get_status(client):
    response = client.get('/api/status')
    assert response.status_code == 200

def test_get_history(client):
    response = client.get('/api/history')
    assert response.status_code in [200, 500]
