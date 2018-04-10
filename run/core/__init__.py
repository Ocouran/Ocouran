#!usr/bin/env/ python3

from flask import Flask, render_template

#from core.controllers.index import controller as index
from core.controllers.Oauth import controller as Oauth
from core.controllers.Organisation import controller as Organisation
from core.controllers.Repository import controller as Repository
from core.controllers.Contributor import controller as Contributor
from core.controllers.Tag import controller as Tag
from core.controllers.Details import controller as Details
from core.controllers.Mvp import controller as Mvp

omnibus = Flask(__name__)
omnibus.config['SESSION_TYPE'] = 'memcached'
omnibus.config['SECRET_KEY'] = 't7W_YlRctNwvGmrNNlxlIL_N'


#omnibus.register_blueprint(index)
omnibus.register_blueprint(Oauth)
omnibus.register_blueprint(Organisation)
omnibus.register_blueprint(Repository)
omnibus.register_blueprint(Contributor)
omnibus.register_blueprint(Tag)
omnibus.register_blueprint(Details)
omnibus.register_blueprint(Mvp)

#@omnibus.route('/',methods=['GET'])
#def homepage():
#    return render_template('index.html')
