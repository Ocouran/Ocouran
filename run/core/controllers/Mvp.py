#!/usr/bin/env python3

from flask import Blueprint, render_template

from neo4jrestclient.client import GraphDatabase
from py2neo import Graph, authenticate, Node, Relationship
import random
# Data Manipulation
import pandas as pd
# Treemap Ploting
import squarify
# Matplotlib and Seaborn imports
import matplotlib
matplotlib.use('Agg')
from matplotlib import style
import matplotlib.pyplot as plt
import seaborn as sns
import mpld3
import json
#authenticate DB
authenticate("localhost:7474", "neo4j", "swordfish")
graph = Graph()


# Activate Seaborn
sns.set()
#matplotlib inline
# Large Plot
matplotlib.rcParams['figure.figsize'] = (15.0, 9.0)
# Use ggplot style
style.use('ggplot')

controller = Blueprint('Mvp',__name__,url_prefix='/Mvp',static_folder='static')

def map_key(key):
    ''' 
    key is the Dataframe column you wish to use to calculate the percentages and square size
    Ex: UniqueContributors
    '''
    df = pd.DataFrame(graph.run('''match p=(n:DataInput)-[]-(o:Organisation)-[]-(r:Repo)-[x:Contributor]-(c:User) 
                                    WHERE n.CreatedOn="18-03-24" RETURN distinct o.name as Organisation, 
                                    count(distinct r.name) as Repos,sum(r.size) as Size,
                                    count(distinct c.name) as UniqueContributors,count(x) as Contributors,
                                    MIN(r.created_at) as CreatedOn order by Organisation''').data())
    df = df.sort_values(by=key, ascending=False)
    # Find Percentage
    df["Key_perc"] = round(100 * df[key] / sum(df[key]), 2)
    # Create Treemap Labels
    df["Label"] = df["Organisation"] + " (" + df["Key_perc"].astype("str") + "%)"
    
    # Get Axis and Figure
    fig, ax = plt.subplots()
    # Our Colormap
    cmap = matplotlib.cm.coolwarm
    # Min and Max Values
    mini = min(df[key])
    maxi = max(df[key])
    # Finding Colors for each tile
    norm = matplotlib.colors.Normalize(vmin=mini, vmax=maxi)
    colors = [cmap(norm(value)) for value in df[key]]
    # Plotting
    squarify.plot(sizes=df[key], label=df["Label"], alpha=0.8, color=colors)
    # Removing Axis
    plt.axis('off')
    # Invert Y-Axis
    plt.gca().invert_yaxis()
    # Title
    plt.title(key, fontsize=32)
    # Title Positioning
    ttl = ax.title
    ttl.set_position([.5, 1.05])
    # BG Color
    fig.set_facecolor('#eeffee')
    
    #mpld3.save_html(fig, './core/templates/{}_fig.html'.format(key))
    json01 = json.dumps(mpld3.fig_to_dict(fig))
    return json01


def google_treemap():
    df1 = pd.DataFrame(graph.data('''MATCH p=(d:DataInput)<-[]-(o:Organisation)-[]-(r:Repo)-[]-(u:User) 
                                    WHERE d.CreatedOn='18-03-26' RETURN o.name as Org, 
                                    count(distinct r.name) as Repo, count(distinct u.name) as Contributors, 
                                    sum(r.size) as Size order by Org DESC'''))
    total_contribs = sum(df1['Contributors'])
    #print(df1)
    #initialize root leaf
    A = [['Projects','Parent', 'Contributors','Size']]
    A.append([{'v':'BlockchainProjects', 'f':'BlockchainProjects'},'', 0,0])  #v=value, f=formatted value
    #print(A)
    for index, row in df1.iterrows():  #row['Contributors']/total_contribs*100
        A.append([{'v':row['Org'], 'f':row['Org']}, 'BlockchainProjects', 0, row['Size']])

        parent = row['Org']
        df2 = pd.DataFrame(graph.data('''MATCH p=(d:DataInput)<-[]-(o:Organisation)-[]-(r:Repo)-[]-(u:User)
                                        WHERE d.CreatedOn='18-03-26' AND o.name="{parent}" RETURN distinct r.name as Repo, 
                                        o.name as Parent, count(distinct u.name) as Contributors, max(r.size) as Size
                                        ORDER BY Parent DESC'''.format(parent=parent)))
        total_contributors = sum(df2['Contributors'])
        for index, row in df2.iterrows():
            if row['Contributors']/total_contributors*100 != 100:
                A.append([{'v':row['Repo']+'-'+row['Parent'], 'f':row['Repo']},row['Parent'], row['Contributors']/total_contributors*100, row['Size']])

    #print(A)
        #print("New Row---------------------")

    return A

@controller.route('/',methods=['GET'])
def main(name='Mvp'):

    data = graph.run('''match (u:User)<-[r:Following]-() return u.name as Name,count(r) as NumberOfCon,
                        u.followers as Followers,u.contributions as Contributions,  
                        u.html_url as Link,u.avatar_url as Pic, u.login as Login, u.bio as Bio, u.blog as Blog,
                        u.email as email, u.location as location, u.hirable as hirable 
                        order by NumberOfCon DESC,
                        Followers DESC, Contributions DESC''').data()

    return render_template('Mvp.html', name=name, data=data)


#@controller.route('/<OrgName>',methods=['GET'])
def org(OrgName):
    data = graph.run('''MATCH p=(d:DataInput)<-[]-(o:Organisation)-[]-(r:Repo)-[]-(u:User) 
                        WHERE d.CreatedOn='18-03-26' AND o.name='{}' 
                        RETURN distinct o.name,max(o.lastupdate) as LastUpdate,
                        count(distinct r.name) as NumOfRepos,collect(distinct r.name) as Repos,
                        sum(r.size) as Size,collect(distinct r.html_url) as RepoGithub,
                        collect(distinct r.size) as RepoSize ,count(distinct u.name) as NumOfContributors, 
                        collect(distinct u.name) as Contributors, collect(distinct u.avatar_url) as ContributorUrl,
                        collect(distinct u.html_url) as UserGithub, collect(distinct u.contributions) as UContribs, 
                        collect(distinct u.blog) as UBlog, collect(distinct u.followers) as UFollowers, 
                        collect(distinct u.following) as UFollowing 
                        ORDER BY UContribs DESC'''.format(OrgName)).data()

    return render_template('OrgDetails.html', OrgName=OrgName, data=data, tag_url=OrgName+'/Tag')


#@controller.route('/newproject',methods=['GET'])
def newproject():
    return render_template('newproject.html')

#@controller.route('/<OrgName>/Tag',methods=['GET'])
def tag_org(OrgName):
    tags = graph.run("MATCH (t:Tag) return t.name").data()
    return render_template('tag_project.html',tags=tags)
    
