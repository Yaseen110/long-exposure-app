from flask import Flask, request, render_template, send_file
import os
import cv2
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
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

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded.", 400

        file = request.files['file']
        if file.filename == '':
            return "No selected file.", 400

        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        output_image_path = os.path.join(RESULT_FOLDER, 'long_exposure.png')
        create_long_exposure(file_path, output_image_path)

        return send_file(output_image_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
