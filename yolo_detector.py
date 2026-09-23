import cv2
import requests
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

API_URL = "http://127.0.0.1:5001/api/update-counts"
VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck

def process_frame_with_quadrants(frame):
    height, width, _ = frame.shape
    mid_x, mid_y = width // 2, height // 2

    # Run YOLO detection
    results = model(frame, verbose=False)[0]

    lane_counts = {"lane_1": 0, "lane_2": 0, "lane_3": 0, "lane_4": 0}

    for box in results.boxes:
        cls_id = int(box.cls[0])
        if cls_id in VEHICLE_CLASSES:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            if center_x < mid_x and center_y < mid_y:
                lane_counts["lane_1"] += 1
            elif center_x >= mid_x and center_y < mid_y:
                lane_counts["lane_2"] += 1
            elif center_x < mid_x and center_y >= mid_y:
                lane_counts["lane_3"] += 1
            else:
                lane_counts["lane_4"] += 1

    payload = {"lane_counts": lane_counts, "emergency_lane": None}
    try:
        requests.post(API_URL, json=payload)
        print(f"📊 Quad Counts Sent: {lane_counts}")
    except Exception as e:
        print(f"❌ Flask post error: {e}")

    annotated = results.plot()
    cv2.line(annotated, (mid_x, 0), (mid_x, height), (255, 255, 0), 2)
    cv2.line(annotated, (0, mid_y), (width, mid_y), (255, 255, 0), 2)

    cv2.putText(annotated, f"Lane 1: {lane_counts['lane_1']}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(annotated, f"Lane 2: {lane_counts['lane_2']}", (mid_x + 20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(annotated, f"Lane 3: {lane_counts['lane_3']}", (20, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(annotated, f"Lane 4: {lane_counts['lane_4']}", (mid_x + 20, mid_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    return annotated

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera feed.")
        return

    print("🎥 Camera Active with Quadrant ROI Detection! Press 'q' to quit.")

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 30 == 0:
            display_frame = process_frame_with_quadrants(frame)
        else:
            display_frame = frame

        cv2.imshow("Smart Traffic - 4-Quadrant AI Detector", display_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()