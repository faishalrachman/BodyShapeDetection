from libs.body_shape import getShapeFromImage
from libs.mobilenetv2_model import load_model
from flask import Flask, request, render_template
import base64
from time import time


app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("index.html")


from flask import request, redirect
from werkzeug.utils import secure_filename

import os

app.config["IMAGE_UPLOADS"] = "uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG"]

#Load Segmentation Model
MODEL = load_model()

def allowed_image(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

@app.route("/upload", methods=["POST"])
def upload_image():
    if request.method == "POST":
        if request.files:
            timestamp = int(time())
            image = request.files["image"]
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], "temp-%d.jpg" % timestamp))
            shape = getShapeFromImage("uploads/temp-%d.jpg" % timestamp, MODEL)
            return shape
    return "Invalid Format"

app.run("0.0.0.0", 3000)