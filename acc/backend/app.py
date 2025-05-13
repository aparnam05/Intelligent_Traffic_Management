from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sock import Sock
from ultralytics import YOLO
from PIL import Image
import io
import json

app = Flask(__name__)
CORS(app)
sock = Sock(app)

# Load YOLOv8 accident detection model
model = YOLO(r'C:\SE_combined\runs\detect\train\weights\best.pt')

# Store active WebSocket connections
connections = set()

# Function to detect accidents
def detect_accident(uploaded_image):
    image = Image.open(io.BytesIO(uploaded_image))
    results = model(image)
    
    accident_detected = False
    detections = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            if box.conf > 0.5:  # Confidence threshold
                accident_detected = True
                detections.append({
                    "class_id": int(box.cls),
                    "confidence": float(box.conf),
                    "bbox": box.xyxy.tolist()
                })
    
    return accident_detected, detections

# WebSocket Route
@sock.route('/ws')
def handle_ws(ws):
    """Handles WebSocket connections."""
    connections.add(ws)
    try:
        while True:
            ws.receive()  # Keep connection alive
    except:
        connections.discard(ws)  # Remove closed connection

# Image Upload Route
@app.route('/upload', methods=['POST'])
def upload_image():
    """Handles image uploads and triggers accident detection."""
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files['image'].read()
    location = request.form.get('location', 'Unknown Location')

    # Detect accident
    accident_detected, detections = detect_accident(image)

    if accident_detected:
        # Construct notification
        notification = {
            "message": "Accident detected!",
            "location": location,
            "detections": detections
        }

        # Broadcast notification to all connected WebSocket clients
        for conn in list(connections):
            try:
                conn.send(json.dumps(notification))
            except:
                connections.discard(conn)  # Remove closed connections
        
        return jsonify({"message": "Accident detected! Notification sent.", "detections": detections}), 200
    else:
        return jsonify({"message": "No accident detected."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
