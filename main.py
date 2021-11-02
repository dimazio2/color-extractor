from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import os

UPLOAD_FOLDER = "./upload"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c71835efb0d2b358f7bbf35640715ce4'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Bootstrap(app)

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('image', filename=filename))
    else:
        return render_template("index.html")


def palette(img):
    arr = np.asarray(img)
    colors, count = np.unique(arr.reshape(-1, 3), return_counts=True, axis=0)
    sorted_colors = colors[np.argsort(-count)]
    sorted_count = count[np.argsort(-count)]
    sorted_percentage = 100.0 * sorted_count / count.sum()
    colors_merged = [pair for pair in zip(sorted_colors, sorted_percentage)]
    return colors_merged


@app.route('/image/<filename>')
def image(filename):
    img = Image.open(app.config['UPLOAD_FOLDER'] + '/' + filename).convert('RGB')

    colors = []
    for color in palette(img)[:10]:
        # colors.append(f"#{color[0][0]:02x}{color[0][1]:02x}{color[0][2]:02x}")
        colors.append((f"#{color[0][0]:02x}{color[0][1]:02x}{color[0][2]:02x}", f"{color[1]:.1f}%"))
    print(colors)
    return render_template("image.html", filename=filename, colors=colors)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
