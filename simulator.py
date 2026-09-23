import time
import random
import requests

# Flask server API endpoints
API_URL = "http://127.0.0.1:5001/api/update-counts"
OVERRIDE_URL = "http://127.0.0.1:5001/api/override-emergency"
CLEAR_URL = "http://127.0.0.1:5001/api/clear-emergency"

def generate_traffic_data():
    """Simulates real-time vehicle counts detected across 4 lanes."""
    return {
        "lane_counts": {
            "lane_1": random.randint(0, 25),
            "lane_2": random.randint(0, 25),
            "lane_3": random.randint(0, 25),
            "lane_4": random.randint(0, 25)
        }
    }

def run_simulation(interval_seconds=5):
    print("🚦 Dynamic Traffic & Emergency Simulator Started...")
    print(f"Target Base URL: {API_URL}")
    print("Press Ctrl+C to stop.\n" + "-"*50)

    emergency_active = False

    while True:
        try:
            # 1. Handle active emergency clearing (15% chance to clear if currently active)
            if emergency_active and random.random() < 0.15:
                res = requests.post(CLEAR_URL, json={}, timeout=3)
                if res.status_code == 200:
                    emergency_active = False
                    print("🚨 [EMERGENCY CLEARED] Returning to dynamic timing algorithm.\n")
                time.sleep(interval_seconds)
                continue

            # 2. Trigger new emergency (10% chance if not active)
            if not emergency_active and random.random() < 0.10:
                selected_lane = f"lane_{random.randint(1, 4)}"
                res = requests.post(OVERRIDE_URL, json={"lane": selected_lane}, timeout=3)
                
                if res.status_code == 200:
                    emergency_active = True
                    print(f"🚨 [EMERGENCY VEHICLE DETECTED] Priority override requested for {selected_lane.upper()}!\n")
                time.sleep(interval_seconds)
                continue

            # 3. Standard traffic count update
            payload = generate_traffic_data()
            if emergency_active:
                payload["emergency_lane"] = selected_lane

            res = requests.post(API_URL, json=payload, timeout=3)
            
            if res.status_code == 200:
                counts = payload["lane_counts"]
                state = res.json().get("state", {})
                
                status_str = f"[EMERGENCY ACTIVE: {state.get('emergency_lane', '').upper()}]" if state.get("emergency_active") else "[NORMAL CYCLE]"
                print(f"[SENT] {status_str} Counts -> L1={counts['lane_1']} | L2={counts['lane_2']} | L3={counts['lane_3']} | L4={counts['lane_4']}")
                print(f"       -> Active Signal: {state.get('current_green', '').upper()} ({state.get('green_duration')}s duration)\n")
            else:
                print(f"[SERVER ERROR] Status Code: {res.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"[CONNECTION FAILED] Ensure Flask app is running on port 5001. Error: {e}")

        time.sleep(interval_seconds)

if __name__ == "__main__":
    run_simulation(interval_seconds=5)