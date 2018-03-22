#!/usr/bin/env python3

import requests
import time
from neo4jrestclient.client import GraphDatabase
from py2neo import Graph, authenticate, Node, Relationship
import csv
import os

#Local Testing (uncomment both lines below)
authenticate("localhost:7474", "neo4j", "neo4j")
graph = Graph()

#Get Neo4j password
tokenfile = open(os.path.expanduser("~")+'/.pat/.neo4j_pass','r')
neo4jpass = str(tokenfile.read())
#Get Github API token
tokenfile = open(os.path.expanduser("~")+'/.pat/.git_ocouran','r')
gittoken = str(tokenfile.read())

#Remote Authentication
#authenticate("67.205.151.165:7474", "neo4j", neo4jpass)
#graph = Graph('http://67.205.151.165:7474', user='neo4j', password='swordfish')

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

def get_json(path):
    #Unauthenticated Request
    #r = requests.get(path).json()
    #Authenticated Request
    ratedata = get_ratelimit_auth()['resources']['core']
    #print(ratedata)    
    remaining = ratedata['remaining']
    reset = ratedata['reset']
    print('remaining:',remaining,' >>>','Resetting at:', reset)
    r = requests.get(path, headers={'Authorization': 'token '+gittoken}).json()

    return(r)    

def get_head(path):
    r = requests.head(path, headers={'Authorization': 'token '+gittoken})
    return(r.text)   

def get_ratelimit_auth():
    path='https://api.github.com/rate_limit'
    r = requests.get(path, headers={'Authorization': 'token '+gittoken})
    return(r.json())   

def get_ratelimit_unauth(path='https://api.github.com/rate_limit'):
    r = requests.get(path)
    return(r.json())   

 

def schema_set_project():
    #run this just once
    #graph = Graph()   
    #Set uniqueness relationships in DB    
    #graph.schema.create_uniqueness_constraint('Repo', 'id')
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
    #graph.create(org1)
    tx.merge(org1)
    print("Insert Organisation")
    try:
        tx.commit()
    except:
        print('Error pushing data')

    for repo_json in jsoninfo:
        #print('Repo_json:',repo_json)
        p1,l1,o1 = insert_project('Repo', repo_json) 
        r1 = Relationship(p1, "BelongsTo", org1)
        graph.create(r1)
        print("Created Relationship: Belongs To")
        

def insert_project(nodetype, jsoninfo):
    ''' 
    NodeType is the type of item being inserted: Organisation, repo
    '''
    #print('Insert Project >>', jsoninfo)

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
    print("Created License Node")
    #Create Owner Node
    #o1 = Node('Owner',**owner)
    #tx.merge(o1)
    o1 = 1

    #Commit Transaction to DB
    tx.commit()
    print("tx.commit")
    #Create Relationships
    r1 = Relationship(p1, "HasLicense", l1)
    graph.create(r1)
    print("create relationship: Project to License")
    #r2 = Relationship(p1, "OwnedBy", o1)
    #graph.create(r2)

    return p1,l1,o1

def get_contributors():
    
    repos = graph.run("match (n:Repo) return n.id as ID,n.name as repo, n.contributors_url as contributors_url")
    for repo in repos:
        ID = repo[0]
        print('Getting Contributors for Repo ID:', ID)
        try:
            contributors = get_json(repo['contributors_url'])
            #print(type(contributors))
            #print(contributors)
            for contributor in contributors:
                #print(contributor)
                contributor['name'] = contributor['login']  #add a name field
                
                #tx = graph.begin()
                #Create User node
                #u1 = Node(contributor['type'],**contributor)
                #tx.merge(u1)
                #tx.commit()
                #Create Relationship
                #r1 = Relationship(u1, "Contributor", nr)
                #graph.create(r1)
    
                #Create Contributor Node and relationship
                #graph.run("CREATE (a:User {data})<-[:Contributor]-(b:Repo{id:{ID}})", data = {**contributor}, ID=ID)
                graph.run("MATCH (b:Repo{id:{ID}}) CREATE (a:User {data})<-[:Contributor]-(b)", data = {**contributor}, ID=ID)
        except:
            print('Could not get Contributors for repo ID:',ID)







if __name__ == '__main__':
    #schema_set_project()
    #proj = get_json('https://api.github.com/repos/monero-project/monero')
    #proj = get_json('https://api.github.com/repos/ethereum/go-ethereum')
    #proj = get_json('https://api.github.com/repos/ethereum/web3.py')
    #proj = get_json('https://api.github.com/repos/bitcoin/bitcoin')
    #something = insert_project('repo', proj)

    #repos = get_json('https://api.github.com/orgs/bitcoin/repos')
    #repos = get_json('https://api.github.com/orgs/saltstack/repos')
    #something = insert_repos('Bitcoin',repos)
    
    repos_from_list('org_list.txt')
    
    get_contributors()
    

    #print(get_ratelimit_auth())
    #print(get_ratelimit_unauth())
    #print(get_head('https://api.github.com/orgs/ripple/repos'))

