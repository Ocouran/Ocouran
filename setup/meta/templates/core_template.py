#!usr/bin/env/ python3

from flask import Flask, render_template

from core.controllers.index import controller as index
from core.controllers.{contr} import controller as {contr}

omnibus = Flask(__name__)
omnibus.register_blueprint(index)
omnibus.register_blueprint({contr})


#@omnibus.route('/',methods=['GET'])
#def homepage():
#    return render_template('index.html')
