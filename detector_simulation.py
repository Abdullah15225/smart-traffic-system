import time
import random
import requests

API_URL = "http://127.0.0.1:5001/api/update-counts"

def generate_mock_traffic():
    """Simulates dynamic vehicle counts across 4 lanes."""
    return {
        "lane_1": random.randint(2, 25),
        "lane_2": random.randint(1, 18),
        "lane_3": random.randint(0, 20),
        "lane_4": random.randint(3, 15)
    }

def run_simulation():
    print("🚀 Starting Traffic Detection Simulation...")
    print("Press CTRL+C to stop.\n")
    
    step = 0
    while True:
        step += 1
        lane_counts = generate_mock_traffic()
        
        # Simulate an emergency vehicle every 5 cycles (~25 seconds)
        emergency_lane = None
        if step % 5 == 0:
            emergency_lane = f"lane_{random.randint(1, 4)}"
            print(f"⚠️  [SIMULATION] Emergency vehicle detected in {emergency_lane.upper()}!")

        payload = {
            "lane_counts": lane_counts,
            "emergency_lane": emergency_lane
        }

        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                print(f"[Cycle {step}] Counts sent successfully: {lane_counts}")
            else:
                print(f"[Cycle {step}] Server returned error: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to connect to Flask API: {e}")

        # Wait 5 seconds before next detection cycle
        time.sleep(5)

if __name__ == "__main__":
    run_simulation()