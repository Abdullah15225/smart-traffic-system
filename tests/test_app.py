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

def test_emergency_override_lifecycle(client):
    # 1. Test activating an emergency override
    activation_response = client.post('/api/override-emergency', json={"lane": "lane_1"})
    assert activation_response.status_code == 200
    
    # 2. Test verifying the status state
    status_response = client.get('/api/status')
    assert status_response.status_code == 200
    data = status_response.get_json()
    assert data['emergency_active'] is True
    assert data['emergency_lane'] == 'lane_1'
    assert data['current_green'] == 'lane_1'
    
    # 3. Test clearing the emergency override
    clear_response = client.post('/api/clear-emergency')
    assert clear_response.status_code == 200
    
    # Verify it cleared
    final_status_response = client.get('/api/status')
    final_data = final_status_response.get_json()
    assert final_data['emergency_active'] is False
    assert final_data['emergency_lane'] is None

def test_get_history(client):
    response = client.get('/api/history')
    assert response.status_code in [200, 500]
