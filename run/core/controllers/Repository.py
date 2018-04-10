#!/usr/bin/env python3

from flask import Blueprint, render_template

controller = Blueprint('Repository',__name__,url_prefix='/Repository')


@controller.route('/', methods=['GET'])
def lookup(name='Repository'):
    return render_template('Repository.html', name=name)


@controller.route('/<string:word>', methods=['GET'])
def lookup2(word):
    name='Repository loves '+word
    return render_template('Repository.html', name=name)

