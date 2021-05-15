from flask import Flask, jsonify, request
from flask import render_template, redirect, make_response
import services

app = Flask(__name__)


@app.route('/')
def base_route(): return services.base(request)



@app.route('/paint')
def paint_view(): return services.paint_view(request)


@app.route('/id/<id>')
def photos_names(id): return services.photos_names(request, id)




if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
