#!/usr/bin/env python3

from flask import Blueprint, render_template, request
import flask_login
import os
import flask
import requests
import json

#DB imports
from py2neo import Graph, authenticate, Node, Relationship
import time, datetime

#DRIVE IMPORTS
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
#PEOPL IMPORTS
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools

#Authenticate DB
authenticate("localhost:7474", "neo4j", "swordfish")
graph = Graph()

controller = Blueprint('Oauth',__name__, static_folder='static')

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"
# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
#SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly','https://www.googleapis.com/auth/userinfo.email']
SCOPES = ['https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/contacts',
            'profile', 'https://www.googleapis.com/auth/plus.login']
API_SERVICE_NAME = 'people'  # was 'drive'
API_VERSION = 'v1' #for drive 'v2'


@controller.route('/')
def index():
    return render_template('cover.html') 

@controller.route('/signin')
def signin():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')
  return flask.redirect('index_si')
     
@controller.route('/index_si')
def index_si():
    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
    # Build the request
    peeps = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    # execute and get data
    files = peeps.people().get(resourceName='people/me', personFields='names,emailAddresses').execute()
    flask.session['userinfo'] = {'displayName': files['names'][0]['displayName'],
                                 'givenName':files['names'][0]['givenName'],
                                 'familyName':files['names'][0]['familyName'],
                                 'email':files['emailAddresses'][0]['value'],
                                 'googleAccountId':files['names'][0]['metadata']['source']['id']}
    #Check if user is already in DB
    userrequest = graph.run("match (u:siteUser) where u.googleAccountId='{ID}' return count(u) as num,max(id(u)) as neoId".format(ID=flask.session['userinfo']['googleAccountId'])).data()  #neoId is the DB node ID, not using the user's google ID
    if userrequest is None:
        returnUser = 0
        neoId = None
    else:
        returnUser = userrequest[0]['num']
        neoId = userrequest[0]['neoId']
    if returnUser == 0:
        #Create siteUser in DB
        u1 = Node("siteUser",**flask.session['userinfo'],CreatedOn=datetime.datetime.now().strftime("%y-%m-%d"),epoch=time.time())
        graph.create(u1)
        neoId = graph.run("match (u:siteUser) where u.googleAccountId='{ID}' return max(id(u)) as neoId".format(ID=flask.session['userinfo']['googleAccountId'])).data()[0]['neoId']
    #Save NeoID in session for later use
    flask.session['neoId'] = int(neoId)
    return render_template('cover_si.html',message=files['names'][0]['displayName']) 

@controller.route('/Tags', methods=['GET', 'POST'])
def tags():
    if request.method == 'GET':
        #Get tags from DB
        tags = graph.run("match (t:Tag) return t.name as tagName, t.Description as Description, t.creator as tagCreator order by t.name desc").data()
        #Send tags to UI
        return render_template('Tags.html', tags=tags,tags_num=len(tags)) 
    else: #New tag is created
        #Get inputs
        tagData = {}
        tagData['name'] = request.form['tagName']
        tagData['Description'] = request.form['tagDesc']
        tagCreator = flask.session['neoId']
        userNode = graph.run("match (u:siteUser) where id(u)='{ID}' return u".format(ID=tagCreator))
        #create tags in DB
        t1 = Node("Tag",**tagData)
        graph.create(t1)
        #Create relationship to User
        #r1 = Relationship(userNode, 'Created', t1)
        string1 = "{"+"googleAccountId:'{ID}'".format(ID=flask.session['userinfo']['googleAccountId'])+"}"
        string2 = "{"+"name:'{name}'".format(name=tagData['name'])+"}"
        graph.run("MATCH (u:siteUser {string1}), (t:Tag {string2}) CREATE (u)-[r:Created]->(t)".format(string1=string1, string2=string2))
        return flask.redirect('Tags')


######## Oauth Routes ##########

@controller.route('/test')
def test_api_request():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')
  
  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])
  #drive stuff
  drive = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

  files = drive.files().list().execute()

  #Open ID stuff
  #userinfo = people.getOpenIdConnect
  #print(userinfo)  
  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.jsonify(**files)
  

@controller.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  flow.redirect_uri = flask.url_for('Oauth.oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)


@controller.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('Oauth.oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  #Original  
  #return flask.redirect(flask.url_for('Oauth.test_api_request'))
  #Mine
  return flask.redirect(flask.url_for('Oauth.index_si'))

@controller.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@controller.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  #return ('Credentials have been cleared.<br><br>' +
  #        print_index_table())
  return flask.redirect(flask.url_for('Oauth.index'))


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')
