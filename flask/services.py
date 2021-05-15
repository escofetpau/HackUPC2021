from flask import render_template, redirect, make_response
from flask import jsonify, send_file


def base(request):
    return render_template("index.html", user={'name': 'nico'})