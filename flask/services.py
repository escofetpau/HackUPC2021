from flask import render_template, redirect, make_response
from flask import jsonify, send_file
import os


def base(request):
    return render_template("index.html", user={'name': 'nico'})


def paint_view(request):
    return render_template("pintar.html")

def photos_names(request, id):
    if id is None or not os.path.isdir(f'static/dataset/{id}'):
        return 'ID does not exist', 400

    photos = os.listdir(f'static/dataset/{id}')
    return jsonify(photos)

def photos_to_text(request, id):
    return 'OK'


def drawed_image(request):
    print('hpli')
    print(request.files['file'])
    return 'ok', 200