from flask import Flask, request, jsonify, send_from_directory
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename
from flask_cors import CORS  # Enable CORS for frontend requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow cross-origin requests

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Function to process video
def create_long_exposure(video_path, output_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        return None

    blended_frame = np.zeros_like(frame, dtype=np.float32)
    frame_count = 0

    while ret:
        frame = frame.astype(np.float32) / 255.0
        frame = np.clip(frame * 1.3, 0, 1)
        mask = np.any(frame > 0.05, axis=2, keepdims=True)
        blended_frame = blended_frame * (1 - mask * (1 / (frame_count + 1))) + frame * mask

        frame_count += 1
        ret, frame = cap.read()

    cap.release()

    if frame_count > 0:
        blended_frame = (blended_frame - blended_frame.min()) / (blended_frame.max() - blended_frame.min()) * 255
        blended_frame = np.clip(blended_frame, 0, 255).astype(np.uint8)
        cv2.imwrite(output_path, blended_frame)

    return output_path

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    output_image_path = os.path.join(RESULT_FOLDER, 'long_exposure.png')
    processed_image = create_long_exposure(file_path, output_image_path)
    
    if not processed_image:
        return jsonify({"error": "Error processing video."}), 500

    return jsonify({"image_url": f"/results/long_exposure.png"})

# Route to serve images from the results folder
@app.route('/results/<filename>')
def serve_result_image(filename):
    return send_from_directory(RESULT_FOLDER, filename)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API is running!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
