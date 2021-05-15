from flask import Flask, jsonify, request
from flask import render_template, redirect, make_response
import services
import pickle

app = Flask(__name__)


@app.route('/')
def base_route(): return services.base(request)


@app.route('/paint')
def paint_view(): return services.paint_view(request)


@app.route('/photos/<id>')
def photos_names(id): return services.photos_names(request, id)


@app.route('/text/<id>')
def photos_to_text(id): return services.photos_to_text(request, id)


@app.route('/bottom/<id>/<photo>')
def photo_bottom(id, photo): return services.photo_bottom(request, id, photo)


@app.route('/drawed-image', methods=['POST'])
def drawed_image(): return services.drawed_image(request)


@app.route('/gen-panorama', methods=['POST'])
def gen_panorama(): return services.gen_panorama(request)


if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
