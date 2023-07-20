from flask import Flask, jsonify, send_file, request
import fitz
import os
import io
from PIL import Image
import time
import requests

app = Flask(__name__)


# Function to convert first page of PDF to an image
def pdf_to_png(pdf_url, zoom=1):
    start_time = time.time()  # start timing

    # Download the PDF file
    response = requests.get(pdf_url)
    data = io.BytesIO(response.content)

    # Open the PDF file
    doc = fitz.open(stream=data, filetype='pdf')

    # Load the first page
    page = doc.load_page(0)  # load page 0

    # Define matrix for higher resolution images
    mat = fitz.Matrix(zoom, zoom)

    pix = page.get_pixmap(matrix=mat)  # render page to an image
    raw = pix.samples  # access raw image data

    image = Image.frombytes("RGB", [pix.width, pix.height], raw)

    # Save image to a BytesIO object
    img_io = io.BytesIO()
    image.save(img_io, 'PNG')
    img_io.seek(0)

    end_time = time.time()  # end timing
    elapsed_time = end_time - start_time
    return elapsed_time, img_io


@app.route('/')
def index():
    return jsonify({"Home": "PDF Preview Generator!"})


@app.route('/pdf_preview', methods=['GET'])
def pdf_preview():
    pdf_url = request.args.get('url')
    zoom = request.args.get('zoom')

    if zoom is None:
        zoom = 1

    if pdf_url is None:
        return "No PDF URL provided.", 400

    time_taken, img_io = pdf_to_png(pdf_url, int(zoom))

    print(f"Time taken to generate the image: {time_taken} seconds")

    return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=False, port=os.getenv("PORT", default=5000))
