#!/usr/bin/env python3

import requests
import time
from neo4jrestclient.client import GraphDatabase
from py2neo import Graph, authenticate, Node, Relationship
import csv
import os
from neo4j.v1 import GraphDatabase


#db = GraphDatabase("http://localhost:7474", username="neo4j", password="swordfish")

#Local Testing (uncomment both lines below)
#authenticate("localhost:7474", "neo4j", "swordfish")
#graph = Graph()

uri = "bolt://67.205.151.165:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "@OcouranByte99"))



#authenticate("0.0.0.0:7473", "neo4j", "@OcouranByte99")
#authenticate("67.205.151.165:7687", "neo4j", "@OcouranByte99")
#authenticate("67.205.151.165:7687/db/data", "neo4j", "@OcouranByte99")
#graph = Graph('http://Neo4j:@OcouranByte99@67.205.151.165:7687/db/data/')

# set up authentication parameters
#authenticate("67.205.151.165:7474", "neo4j", "@OcouranByte99")
# connect to authenticated graph database
#graph = Graph("http://67.205.151.165:7474/db/data")

#graph = Graph('http://67.205.151.165:7474/db/data', user='neo4j', password='@OcouranByte99')


#Organisation's repos
#curl https://api.github.com/orgs/bitcoin/repos

#Project
#curl https://api.github.com/repos/bitcoin/bitcoin

#Project Contributors
#curl https://api.github.com/repos/monero-project/monero/contributors

#User
#curl https://api.github.com/users/

#Users Following 
#https://api.github.com/users/{user}/following

#User again

#Get Github API token
#tokenfile = open('~/.pat/.git_ocouran','r')
#gittoken = tokenfile.read()
#print(gittoken)

def get_json(path):
    r = requests.get(path, headers={'Authorization': '9096affa3b2c68ed2d2afefc8b4fa9128a63cf6f'}).json()
    return(r)    

def schema_set_project():
    #run this just once
    graph = Graph()   
    #Set uniqueness relationships in DB
    graph.schema.create_uniqueness_constraint('Organisation', 'name')
    #graph.schema.create_uniqueness_constraint('Repo', 'name')  #giving problems
    graph.schema.create_uniqueness_constraint('License', 'name')


def repos_from_list(filename):
    with open(filename, 'r') as csvfile:
        orgs = csv.reader(csvfile)
        for org in orgs:
            #try:
            path = 'https://api.github.com/orgs/{}/repos'.format(org[0])
            insert_repos(org[0],get_json(path))
            #except:
            #    print("Could not get:", org[0])

def insert_repos(repo, jsoninfo):
    #Repo json comes as a list of dictionaries

    #Create Transaction to DB
    tx = graph.begin()
    #Create Repo Node
    org1 = Node('Organisation', name=repo, lastupdate=time.time())
    tx.merge(org1)
    try:
        tx.commit()
    except:
        print('Error pushing data')

    for repo_json in jsoninfo:
        print('Repo_json:',repo_json)
        p1,l1,o1 = insert_project('Repo', repo_json) 
        r1 = Relationship(p1, "BelongsTo", org1)
        graph.create(r1)
        

def insert_project(nodetype, jsoninfo):
    ''' 
    NodeType is the type of item being inserted: Organisation, repo
    '''
    print('Insert Project >>', jsoninfo)

    keys = [*jsoninfo]
    #print(jsoninfo)
    project = {}
    newdicts = []

    #Unpack json into n dictionaries, dict names held in newdicts
    for k in keys:  
        #print('k:',k) 
        #res = jsoninfo[k]
        try:
            if type(jsoninfo[k]) != dict:
                project[k] = jsoninfo[k]
            else:
                newdicts.append(k)
                globals()[k] = jsoninfo[k]
        except:
            pass
    #Create a name field, so its labelled in graph db
    print(newdicts)
    print(jsoninfo)
    owner['name'] = owner['login']    

    #Create Transaction to DB
    tx = graph.begin()

    #Create Project Node
    p1 = Node(nodetype, **project)
    tx.merge(p1)
    
    #Create License Node
    if len(license) == 0:
        license['name'] = 'None'
    l1 = Node('License', **license)
    tx.merge(l1)
    
    #Create Owner Node
    #o1 = Node('Owner',**owner)
    #tx.merge(o1)
    o1 = 1

    #Commit Transaction to DB
    tx.commit()

    #Create Relationships
    r1 = Relationship(p1, "HasLicense", l1)
    graph.create(r1)
    #r2 = Relationship(p1, "OwnedBy", o1)
    #graph.create(r2)

    return p1,l1,o1

def insert_contributor():
    pass


    







if __name__ == '__main__':
    schema_set_project()
    #proj = get_json('https://api.github.com/repos/monero-project/monero')
    #proj = get_json('https://api.github.com/repos/ethereum/go-ethereum')
    #proj = get_json('https://api.github.com/repos/ethereum/web3.py')
    #proj = get_json('https://api.github.com/repos/bitcoin/bitcoin')
    #something = insert_project('repo', proj)

    #repos = get_json('https://api.github.com/orgs/bitcoin/repos')
    #repos = get_json('https://api.github.com/orgs/ripple/repos')
    #something = insert_repos('Bitcoin',repos)
    
    repos_from_list('org_list.txt')
