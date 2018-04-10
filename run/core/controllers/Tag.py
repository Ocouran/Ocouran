#!/usr/bin/env python3

from flask import Blueprint, render_template
from py2neo import Graph,authenticate,Node, Relationship

#Authenticate DB
authenticate("localhost:7474","neo4j","swordfish")
graph = Graph()

controller = Blueprint('Tag',__name__,url_prefix='/Tag', static_folder='static')


@controller.route('/', methods=['GET', 'POST'])
def lookup(name='Tag'):
    #if flask.request.method == 'GET':
    return render_template('add_project.html', name=name)
    #else:
        #applicable_tags = flask.request.values.get['tags']
        #pass


