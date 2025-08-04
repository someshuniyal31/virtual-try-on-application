# Use Python=3.12.8 
from flask import Flask, render_template, request, redirect, url_for, jsonify 
from flask_cors import CORS 
import os 
from werkzeug.utils import secure_filename 
import base64 
from valid_logic import check_human_pose_with_hands  # Import the pose validation function 
from shirt_fitting import apply_shirt_to_person  # Import the shirt fitting function

app = Flask(__name__) 
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            # Handle photo upload
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Validate the person's pose
                is_valid = check_human_pose_with_hands(filepath)
                if not is_valid:
                    os.remove(filepath)  # Remove invalid file
                    return render_template('index.html', message="Invalid Pose! Please try again.")

                # Save the validated image
                validated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'validated_person_image.png')
                if os.path.exists(validated_image_path):
                    os.remove(validated_image_path) 
                os.rename(filepath, validated_image_path)

                return render_template('index.html', message="Photo validated! You can now proceed to shirt fitting.", show_shirt_fitting=True)
        else:
            return render_template('index.html', message="No file uploaded.")

    return render_template('index.html')

@app.route('/capture_photo', methods=['POST'])
def capture_photo():
    if request.method == 'POST':
        data = request.json.get('image_data')
        if not data:
            return jsonify({'error': 'No image data received'}), 400

        # Decode the base64 image data
        image_data = base64.b64decode(data.split(',')[1])
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'webcam_photo.png')
        with open(filepath, 'wb') as f:
            f.write(image_data)


            
        # Validate the person's pose
        is_valid = check_human_pose_with_hands(filepath)
        if not is_valid:
            os.remove(filepath)
            return jsonify({'message': 'Invalid Pose! Please try again.', 'success': False})

        # Save the validated image
        validated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'validated_person_image.png')
        os.rename(filepath, validated_image_path)

        return jsonify({'message': 'Photo validated! You can now proceed to shirt fitting.', 'success': True})

@app.route('/upload_shirt', methods=['GET', 'POST'])
def upload_shirt():
    if request.method == 'POST':
        if 'shirt' not in request.files:
            return render_template('upload_shirt.html', message="No shirt file uploaded.")

        shirt_file = request.files['shirt']
        if shirt_file and allowed_file(shirt_file.filename):
            shirt_filename = secure_filename(shirt_file.filename)
            shirt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], shirt_filename)
            shirt_file.save(shirt_filepath)

            person_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'validated_person_image.png')
            output_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'final_image.png')

            apply_shirt_to_person(person_image_path, shirt_filepath, output_image_path)

            return render_template('upload_shirt.html', final_image_url=url_for('static', filename='uploads/final_image.png'))

    return render_template('upload_shirt.html')

if __name__ == '__main__':
    app.run(debug=True)