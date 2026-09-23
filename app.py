import sqlite3
import csv
import io
from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart_traffic_secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize SQLite DB for local logging
def init_db():
    conn = sqlite3.connect('traffic_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            lane_1 INTEGER,
            lane_2 INTEGER,
            lane_3 INTEGER,
            lane_4 INTEGER,
            total_vehicles INTEGER,
            emergency_lane TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Global traffic state
traffic_state = {
    "counts": {"lane_1": 0, "lane_2": 0, "lane_3": 0, "lane_4": 0},
    "current_green": "lane_1",
    "green_duration": 10,
    "emergency_active": False,
    "emergency_lane": None
}

def log_to_sqlite(counts, emergency_lane):
    try:
        conn = sqlite3.connect('traffic_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO traffic_logs (timestamp, lane_1, lane_2, lane_3, lane_4, total_vehicles, emergency_lane)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            counts.get("lane_1", 0),
            counts.get("lane_2", 0),
            counts.get("lane_3", 0),
            counts.get("lane_4", 0),
            sum(counts.values()),
            emergency_lane
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database error: {e}")

def calculate_green_time(counts, emergency_lane=None):
    if emergency_lane and emergency_lane in counts:
        return emergency_lane, 30, True

    max_lane = max(counts, key=counts.get)
    max_count = counts[max_lane]

    if max_count == 0:
        duration = 5
    else:
        duration = min(max(5, max_count * 2), 30)

    return max_lane, duration, False

# Socket.IO Connection Event
@socketio.on('connect')
def handle_connect():
    emit('traffic_update', traffic_state)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/update-counts', methods=['POST'])
def update_counts():
    data = request.json or {}
    
    lane_counts = data.get('lane_counts', data.get('counts', traffic_state['counts']))
    emergency_lane = data.get('emergency_lane', traffic_state['emergency_lane'] if traffic_state['emergency_active'] else None)

    active_lane, duration, is_emergency = calculate_green_time(lane_counts, emergency_lane)

    traffic_state['counts'] = lane_counts
    traffic_state['current_green'] = active_lane
    traffic_state['green_duration'] = duration
    traffic_state['emergency_active'] = is_emergency
    traffic_state['emergency_lane'] = emergency_lane if is_emergency else None

    log_to_sqlite(lane_counts, emergency_lane)

    # Broadcast state update live
    socketio.emit('traffic_update', traffic_state)

    return jsonify({"status": "success", "state": traffic_state})

@app.route('/api/override-emergency', methods=['POST'])
def override_emergency():
    data = request.json or {}
    lane = data.get('lane')
    
    if lane in traffic_state['counts']:
        traffic_state['emergency_active'] = True
        traffic_state['emergency_lane'] = lane
        traffic_state['current_green'] = lane
        traffic_state['green_duration'] = 30
        
        log_to_sqlite(traffic_state['counts'], lane)
        socketio.emit('traffic_update', traffic_state)
        
        return jsonify({"status": "success", "message": f"Manual override set for {lane}", "state": traffic_state})
    
    return jsonify({"status": "error", "message": "Invalid lane specified"}), 400

@app.route('/api/clear-emergency', methods=['POST'])
def clear_emergency():
    traffic_state['emergency_active'] = False
    traffic_state['emergency_lane'] = None
    active_lane, duration, _ = calculate_green_time(traffic_state['counts'], None)
    traffic_state['current_green'] = active_lane
    traffic_state['green_duration'] = duration
    
    log_to_sqlite(traffic_state['counts'], None)
    socketio.emit('traffic_update', traffic_state)
    
    return jsonify({"status": "success", "message": "Emergency cleared", "state": traffic_state})

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(traffic_state)

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('traffic_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, lane_1, lane_2, lane_3, lane_4, total_vehicles FROM traffic_logs ORDER BY id DESC LIMIT 15')
    rows = cursor.fetchall()
    conn.close()

    history = [
        {
            "timestamp": row[0],
            "lane_1": row[1],
            "lane_2": row[2],
            "lane_3": row[3],
            "lane_4": row[4],
            "total": row[5]
        } for row in reversed(rows)
    ]
    return jsonify(history)

@app.route('/api/export-csv', methods=['GET'])
def export_csv():
    conn = sqlite3.connect('traffic_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, timestamp, lane_1, lane_2, lane_3, lane_4, total_vehicles, emergency_lane FROM traffic_logs ORDER BY id ASC')
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow(['Log ID', 'Timestamp', 'Lane 1 Count', 'Lane 2 Count', 'Lane 3 Count', 'Lane 4 Count', 'Total Vehicles', 'Emergency Lane'])
    
    # Data rows
    for row in rows:
        writer.writerow([
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7] if row[7] else 'None'
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            "Content-Disposition": "attachment; filename=traffic_logs_export.csv",
            "Content-Type": "text/csv; charset=utf-8"
        }
    )

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5001, debug=True)