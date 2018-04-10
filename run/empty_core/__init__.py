#!usr/bin/env/ python3

from flask import Flask

from core.controllers.Artists import controller as Artists
from core.controllers.Musicians import controller as Musicians
from core.controllers.Politicians import controller as Politicians
from core.controllers.Athletes import controller as Athletes
from core.controllers.CEOs import controller as CEOs
from core.controllers.Celebrities import controller as Celebrities

omnibus = Flask(__name__)
omnibus.register_blueprint(Artists)
omnibus.register_blueprint(Musicians)
omnibus.register_blueprint(Politicians)
omnibus.register_blueprint(Athletes)
omnibus.register_blueprint(CEOs)
omnibus.register_blueprint(Celebrities)


@omnibus.route('/',methods=['GET'])
def homepage():
    return render_template('index.html')
