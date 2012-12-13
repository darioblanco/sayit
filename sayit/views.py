# -*- coding: UTF-8 -*-
from flask import render_template

from sayit import app


@app.route('/')
def main():
    return render_template('main.html')
