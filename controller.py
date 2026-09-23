class TrafficController:
    def __init__(self, min_green=10, max_green=60, base_time=15):
        self.min_green = min_green  # Minimum signal time in seconds
        self.max_green = max_green  # Maximum signal time in seconds
        self.base_time = base_time  # Standard signal time

    def calculate_signal_times(self, lane_counts, emergency_lane=None):
        """
        lane_counts: Dict with count of vehicles per lane e.g. {'lane_1': 12, 'lane_2': 3, ...}
        emergency_lane: Name of lane containing an emergency vehicle (if any)
        """
        # RULE 1: Emergency Vehicle Priority
        if emergency_lane and emergency_lane in lane_counts:
            print(f"\n🚨 EMERGENCY PRIORITY TRIGGERED FOR {emergency_lane.upper()}! 🚨")
            signal_plan = {}
            for lane in lane_counts:
                if lane == emergency_lane:
                    signal_plan[lane] = {"state": "GREEN", "duration": self.max_green}
                else:
                    signal_plan[lane] = {"state": "RED", "duration": self.max_green}
            return signal_plan

        # RULE 2: Dynamic Density Timing Allocation
        total_vehicles = sum(lane_counts.values())
        signal_plan = {}

        if total_vehicles == 0:
            # Default fallback when roads are empty
            for lane in lane_counts:
                signal_plan[lane] = {"state": "GREEN", "duration": self.base_time}
            return signal_plan

        print("\n🚦 CALCULATING DYNAMIC SIGNAL TIMES BASED ON TRAFFIC DENSITY 🚦")
        for lane, count in lane_counts.items():
            # Allocate green time proportional to lane density ratio
            density_ratio = count / total_vehicles
            calculated_duration = int(self.min_green + (density_ratio * (self.max_green - self.min_green)))
            
            # Clamp between min and max bounds
            duration = max(self.min_green, min(self.max_green, calculated_duration))
            
            signal_plan[lane] = {
                "vehicle_count": count,
                "allocated_green_time": duration
            }

        return signal_plan

# Quick self-test script
if __name__ == "__main__":
    controller = TrafficController()

    # Test Scenario 1: Normal Multi-Lane Traffic
    test_lanes = {
        "lane_1": 25,  # Heavy traffic
        "lane_2": 8,   # Moderate traffic
        "lane_3": 2,   # Light traffic
        "lane_4": 15   # Medium-heavy traffic
    }

    print("--- SCENARIO 1: Normal Adaptive Signal Allocation ---")
    plan1 = controller.calculate_signal_times(test_lanes)
    for lane, info in plan1.items():
        print(f"{lane.upper()}: {info['vehicle_count']} vehicles -> Allocated Green Time: {info['allocated_green_time']}s")

    # Test Scenario 2: Emergency Vehicle Detected on Lane 3
    print("\n--- SCENARIO 2: Emergency Vehicle Override ---")
    plan2 = controller.calculate_signal_times(test_lanes, emergency_lane="lane_3")
    for lane, info in plan2.items():
        print(f"{lane.upper()}: State = {info['state']}, Duration = {info['duration']}s")