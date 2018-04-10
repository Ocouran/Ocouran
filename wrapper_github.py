#!/usr/bin/env python3

import requests
import time, datetime
from neo4jrestclient.client import GraphDatabase
from py2neo import Graph, authenticate, Node, Relationship
import csv
import os

#Local Testing (uncomment both lines below)
authenticate("localhost:7474", "neo4j", "swordfish")
graph = Graph()

#Get Neo4j password
tokenfile = open(os.path.expanduser("~")+'/.pat/.neo4j_pass','r')
neo4jpass = str(tokenfile.read())
#print(neo4jpass)
#Get Github API token
tokenfile = open(os.path.expanduser("~")+'/.pat/.git_ocouran','r')
gittoken = str(tokenfile.read())[0:-1]

#Remote Authentication
#authenticate("67.205.151.165:7474", "neo4j", neo4jpass)
#graph = Graph('http://67.205.151.165:7474', user='neo4j', password=neo4jpass)

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
    if remaining == 1:
        print("Too many requests, sleeping until reset")
        time.sleep(reset-time.time()+5)
        r = requests.get(path, headers={'Authorization': 'token '+gittoken}).json()
    else:
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
    #Create DataInput Node
    d1 = Node('DataInput', CreatedOn=datetime.datetime.now().strftime("%y-%m-%d"), epoch=time.time())
    graph.create(d1)

    with open(filename, 'r') as csvfile:
        orgs = csv.reader(csvfile)
        for org in orgs:
            #try:

            path = 'https://api.github.com/orgs/{}/repos'.format(org[0])
            insert_repos(d1, org[0],get_json(path))
            #except:
            #    print("Could not get:", org[0])

def insert_repos(d1, repo, jsoninfo):
    #Repo json comes as a list of dictionaries

    #Create Transaction to DB
    tx = graph.begin()

    #Create Org Node
    org1 = Node('Organisation', name=repo, lastupdate=time.time())
    #graph.create(org1)
    tx.create(org1)
    print("Insert Organisation:",repo)
    try:
        tx.commit()
    except:
        print('Error pushing data')

    y1 = Relationship(org1, "ImportedOn", d1)
    graph.create(y1)

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
    tx.create(p1)

    #Create License Node
    if len(license) == 0:
        license['name'] = 'None'
    l1 = Node('License', **license)
    tx.create(l1)
    print("Created License Node")
    #Create Owner Node
    #o1 = Node('Owner',**owner)
    #tx.merge(o1)
    o1 = 1

    #Commit Transaction to DB
    tx.commit()
    print("tx.commit")
    #Create Ralationships
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
                added_info = get_json(contributor['url'])
                contributor.update(added_info)
                u_id = contributor['id']
                #Does this person already exist in DB?
                exists = graph.run("MATCH (u:User) WHERE u.id={u_id} RETURN count(u)",u_id=u_id).data()
                if exists[0]['count(u)'] == 0:
                    #Create Contributor Node and relationship
                    graph.run("MATCH (b:Repo{id:{ID}}) CREATE (a:User {data})<-[:Contributor]-(b)", data = {**contributor}, ID=ID)
                else:
                    #Create new "Contributor" relationship to existing node
                    graph.run("MATCH (r:Repo{id:{ID}}),(n:User {id:{u_id}}) CREATE (r)-[:Contributor]->(n)", ID=ID, u_id=u_id)
                    print(">>> >>> >>> This contributor also contributed to another repo:",u_id, '--Contibutor--> ',ID)
                
        except:
            print('Could not get Contributors for repo ID:',ID)


def get_following(datainput='18-04-08'):
    #Get users,and the following URL
    users = graph.run("match (d:DataInput)-[]-(o:Organisation)-[]-(r:Repo)-[]-(u:User) WHERE d.CreatedOn='{datainput}' RETURN u.name, u.id, u.following, u.following_url".format(datainput=datainput)).data()
    #For each user, get following
    for user in users:
        userId = user['u.id']  #this is the main user we are using to scrape, we get all the other users he/she is following
        print(">>> >>> >>> Getting followers for user ID:",userId)
        u_following = get_json(user['u.following_url'][:-13])  #remove the last 13 characters before getting URL
        #Save in DB as node + relationship
        for new_user in u_following:
            #get User info
            followed = get_json(new_user['url'])
            f_id = followed['id']
            #Does Followed person already exist in DB?
            exists = graph.run("MATCH (u:User) WHERE u.id={f_id} RETURN count(u)",f_id=f_id).data()
            has_relationship = graph.run("MATCH (u:User)-[:Following]-(v:User) WHERE u.id={userId} AND v.id={f_id} RETURN count(u)",f_id=f_id,userId=userId).data()
            # Save in DB 
            if has_relationship[0]['count(u)'] > 0:
                print(">>> Nodes and relationships already exist, do nothing")
            elif exists[0]['count(u)'] == 0:
                #Create new User node and "Following" relationship
                graph.run("MATCH (u:User{id:{ID}}) CREATE (n:User {data})<-[:Following]-(u)", data = {**followed}, ID=userId)
                print(">>> >>> >>> Added new user and Relationship to:",userId)
            else:
                #Create new "Following" relationship to existing nodes
                graph.run("MATCH (u:User{id:{ID}}),(n:User {id:{f_id}}) CREATE (n)<-[:Following]-(u)", f_id=f_id, ID=userId)
                print(">>> >>> >>> Added new Relationship to existing nodes:",userId, '--Following--> ',f_id)
                






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
    
    #-------------------------------
    repos_from_list('org_list.txt')
    get_contributors()
    get_following()
    #-------------------------------
    
    #print(get_ratelimit_auth())
    #print(get_ratelimit_unauth())
    #print(get_head('https://api.github.com/orgs/ripple/repos'))

