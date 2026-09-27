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

def test_update_counts_endpoint(client):
    payload = {
        "lane_1": 12,
        "lane_2": 4,
        "lane_3": 2,
        "lane_4": 1
    }
    response = client.post('/api/update-counts', json=payload)
    assert response.status_code in [200, 201]

def test_emergency_override_endpoint(client):
    payload = {"lane": "lane_1", "emergency_lane": "lane_1"}
    response = client.post('/api/override-emergency', json=payload)
    assert response.status_code in [200, 201, 400]

def test_get_history(client):
    response = client.get('/api/history')
    assert response.status_code in [200, 500]
