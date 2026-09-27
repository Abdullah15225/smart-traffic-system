import pytest
from controller import TrafficController

@pytest.fixture
def controller():
    return TrafficController()

def test_controller_initialization(controller):
    assert controller is not None
