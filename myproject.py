from flask.helpers import send_file
from MLManager import MLManager
from flask import Flask,request,send_from_directory,jsonify
import os
import logging

# Imports the Cloud Logging client library
import google.cloud.logging

# Instantiates a client
client = google.cloud.logging.Client()

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
client.get_default_handler()
client.setup_logging()

app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
model = MLManager("best.pt")

# save the label and image path result
model_result = None
image_result_path = None

def delete_uploaded_image(path_to_img):
    os.remove(path_to_img)

@app.route("/")
def hello():
    return "Hi From Flask"

@app.route("/detectLabel",methods=["POST","GET"])
def detect():
    global model,image_result_path
    if request.method == "GET":
        return "To Detect from image use POST with 'file' with image to predict"

    # Handle POST

    # Validate Image is present and in correct file extension

    print("Getting image from POST")
    uploaded_image = request.files["file"]
    if uploaded_image.filename == "":
        # No file is present
        msg = "No file is present"
        logging.info(msg)
        return msg
    
    file_ext = os.path.splitext(uploaded_image.filename)[1]
    if file_ext not in app.config['UPLOAD_EXTENSIONS']:
        msg = "Image format not supported (only .jpeg, .jpg, .png)"
        logging.info(msg)
        return msg
    

    # Delete previous image result
    model.delete_detection_folder()
    image_result_path = None

    # save to directory of images-to-infer
    dir = os.path.join("images-to-infer",uploaded_image.filename)
    print(f"Save image to {dir}")
    uploaded_image.save(dir)

    # get result
    res = model.predict_image(dir)
    image_result_path = os.path.join("detection-result","exp",uploaded_image.filename)
    delete_uploaded_image(dir)
    logging.debug(res)
    return jsonify(res)

@app.route("/getImageDetectionResult",methods=["GET"])
def getImageDetectionResult():
    global image_result_path
    if image_result_path == None:
        return "Please made a detection request via /detectLabel"
    else:
        return send_file(image_result_path)


if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)