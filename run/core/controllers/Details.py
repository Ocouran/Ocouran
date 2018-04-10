#!/usr/bin/env python3

from flask import Blueprint, render_template

controller = Blueprint('Details',__name__,url_prefix='/Details')


@controller.route('/', methods=['GET'])
def lookup(name='Details'):
    return render_template('Details.html', name=name)


@controller.route('/<string:word>', methods=['GET'])
def lookup2(word):
    name='Details loves '+word
    return render_template('Details.html', name=name)

