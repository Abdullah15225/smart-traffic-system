import cv2
from ultralytics import YOLO

# 1. Load the pre-trained YOLOv8 model (downloads automatically on first run)
model = YOLO('yolov8n.pt')

# Target vehicle class IDs in YOLO COCO dataset:
# 2: car, 3: motorcycle, 5: bus, 7: truck
VEHICLE_CLASSES = [2, 3, 5, 7]

def process_video(video_source=0):
    # Open webcam (0) or a video file path (e.g., 'sample_traffic.mp4')
    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    print("Starting Traffic Detection... Press 'q' to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO detection
        results = model(frame, verbose=False)

        vehicle_count = 0
        emergency_detected = False

        # Loop through detections
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                # Check if detected object is a vehicle
                if class_id in VEHICLE_CLASSES and confidence > 0.4:
                    vehicle_count += 1
                    
                    # Draw bounding box on frame
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = f"{model.names[class_id]} {confidence:.2f}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Overlay Vehicle Count on display
        cv2.putText(frame, f"Total Vehicles Detected: {vehicle_count}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        # Display output window
        cv2.imshow("Smart Traffic Control - Real-Time Detection", frame)

        # Press 'q' on keyboard to close window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Uses your Mac webcam by default
    process_video(0)