import pytest
from controller import TrafficController

@pytest.fixture
def controller():
    return TrafficController()

def test_controller_initialization(controller):
    assert controller is not None

def test_calculate_signal_times_keys(controller):
    test_lanes = {"lane_1": 0, "lane_2": 0, "lane_3": 0, "lane_4": 0}
    plan = controller.calculate_signal_times(test_lanes)
    assert isinstance(plan, dict)

def test_calculate_signal_times_with_emergency(controller):
    test_lanes = {"lane_1": 5, "lane_2": 2, "lane_3": 1, "lane_4": 0}
    plan = controller.calculate_signal_times(test_lanes, emergency_lane="lane_1")
    assert plan is not None
