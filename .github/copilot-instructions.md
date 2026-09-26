# Workspace Rules for Smart Traffic Control System

## Role & Project Purpose
You are an expert AI engineer maintaining a real-time, computer vision-based traffic management system (`Abdullah15225/smart-traffic-system`).

## System Architecture
- **Backend (`app.py`):** Flask server running on `http://127.0.0.1:5001` with `Flask-SocketIO` for WebSocket streaming.
- **Logic (`controller.py`):** Dynamic timing state machine calculating signal durations from vehicle density.
- **Vision Pipeline (`yolo_detector.py`):** YOLOv8 + OpenCV tracking vehicles across 4 lane regions.
- **Simulator (`simulator.py`):** Mock traffic generator sending HTTP POSTs to update counts and trigger emergency overrides.
- **Frontend (`templates/index.html`):** Real-time Chart.js dashboard listening for Socket.IO events.

## Code Guidelines
- Write modular, clean Python code with type hints where applicable.
- Ensure all API endpoints handle JSON requests safely with proper status codes.
- Preserve existing Socket.IO event names (`update_counts`, `emergency_override`).
