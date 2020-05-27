from libs.body_shape import getShapeFromImage
from libs.mobilenetv2_model import load_model
from flask import Flask, request, render_template
import base64
from time import time
# momod = load_model()
# image_file = "data/testing.jpg"
# body_measurement = getShapeFromImage(image_file)
# print(body_measurement)

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("index.html")


from flask import request, redirect
from werkzeug.utils import secure_filename

import os
app.config["FILE_DESTINATION"] = "C:\\Users\\Ipat\\Documents\\Project\\TA Rafiqi Bgst ga lulus2"
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
    return "hahaha"
    #         if image.filename == "":
    #             print("No filename")
    #             return redirect(request.url)
    #         if allowed_image(image.filename):
    #             filename = secure_filename(image.filename)
    #             image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
    #             print("Image saved")
    #             return redirect(request.url)
    #         else:
    #             print("That file extension is not allowed")
    #             return redirect(request.url)
    # return render_template("public/upload_image.html")


app.run("0.0.0.0", 3000)