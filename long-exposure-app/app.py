# import os
# import cv2
# import numpy as np
# from flask import Flask, request, render_template, send_file
# from werkzeug.utils import secure_filename
# import matplotlib.pyplot as plt
# app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads'
# RESULT_FOLDER = 'results'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(RESULT_FOLDER, exist_ok=True)

# def enhance_image(image, output_path):
#     # Convert from BGR to LAB color space
#     lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
#     # Split LAB channels
#     l, a, b = cv2.split(lab)
    
#     # Apply CLAHE to the L channel
#     clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
#     l_enhanced = clahe.apply(l)
    
#     # Merge enhanced L channel back
#     lab_enhanced = cv2.merge((l_enhanced, a, b))
    
#     # Convert back to BGR color space
#     enhanced_image = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
    
#     # Apply sharpening filter
#     kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
#     sharpened_image = cv2.filter2D(enhanced_image, -1, kernel)
    
#     # Save the enhanced image
#     cv2.imwrite(output_path, sharpened_image)
    
#     # Show the images
#     plt.figure(figsize=(10, 5))
#     plt.subplot(1, 2, 1)
#     plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#     plt.title("Original Image")
#     plt.axis("off")
#     cv2.imwrite(output_path, image)
    
#     plt.subplot(1, 2, 2)
#     plt.imshow(cv2.cvtColor(sharpened_image, cv2.COLOR_BGR2RGB))
#     plt.title("Enhanced Image")
#     plt.axis("off")
    
#     plt.show()
#     cv2.imwrite(output_path, sharpened_image)

# # Function to process video and create long exposure image
# def create_long_exposure(video_path, output_path, alpha=0.2):
#     cap = cv2.VideoCapture(video_path)
#     ret, frame = cap.read()
    
#     if not ret:
#         print("Error: Could not read video.")
#         return
    
#     blended_frame = np.zeros_like(frame, dtype=np.float32)
#     frame_count = 0
    
#     while ret:
#         frame = frame.astype(np.float32) / 255.0  # Normalize to [0,1] range
        
#         # Boost brightness slightly to prevent dim results
#         frame = np.clip(frame * 1.3, 0, 1) 
        
#         # Ignore near-black pixels to prevent dark dominance
#         mask = np.any(frame > 0.05, axis=2, keepdims=True)  # Threshold
#         blended_frame = blended_frame * (1 - mask * (1 / (frame_count + 1))) + frame * mask
        
#         frame_count += 1
#         ret, frame = cap.read()
    
#     cap.release()
    
#     if frame_count > 0:
#         min_val = np.min(blended_frame)
#         max_val = np.max(blended_frame)
#         blended_frame = (blended_frame - min_val) / (max_val - min_val) * 255  # Normalize
#         blended_frame = np.clip(blended_frame, 0, 255).astype(np.uint8)  # Convert back to uint8
#         enhance_image(blended_frame, output_path)
    
#     return output_path

# @app.route('/', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return 'No file part'
#         file = request.files['file']
#         if file.filename == '':
#             return 'No selected file'
        
#         filename = secure_filename(file.filename)
#         file_path = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(file_path)
        
#         output_image_path = os.path.join(RESULT_FOLDER, 'long_exposure.png')
#         create_long_exposure(file_path, output_image_path)
        
#         return send_file(output_image_path, as_attachment=True)
    
#     return '''
#     <!doctype html>
#     <title>Upload Video</title>
#     <h1>Upload a Video to Create a Long Exposure Shot</h1>
#     <form method=post enctype=multipart/form-data>
#       <input type=file name=file>
#       <input type=submit value=Upload>
#     </form>
#     '''

# if __name__ == '__main__':
#     app.run(debug=True)


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
