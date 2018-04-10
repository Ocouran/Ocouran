#!/usr/bin/env python3

from flask import Blueprint, render_template

controller = Blueprint('{contr}',__name__,url_prefix='/{contr}')


@controller.route('/', methods=['GET'])
def lookup(name='{contr}'):
    return render_template('{contr}.html', name=name)


@controller.route('/<string:word>', methods=['GET'])
def lookup2(word):
    name='{contr} loves '+word
    return render_template('{contr}.html', name=name)

