from neo4jrestclient.client import GraphDatabase
import orm

 
db = GraphDatabase("http://localhost:7474", username="neo4j", password="root")
 
# Create some nodes with labels
#user = db.labels.create("User")
#u1 = db.nodes.create(name="Marco")
#user.add(u1)

source = db.labels.create("source")                         #create a label
s1 = db.nodes.create(name="Wikipedia")                      #create a node
source.add(s1)                                              #add the node to the label

celeb_graph = db.labels.create("Celeb")   #create a label
instagram_account = db.labels.create("instagram_account")   #create a label

[c,conn] = orm.do_connect()

for n in range(1,30):
    print(n)
    ci = orm.select_celeb_data_by_id(c,[n])
    print(ci)
    name = ci[1]+ci[2]
    c1 = db.nodes.create(name=name, firstname=ci[1], \
         lastname=ci[2],created_on=ci[3],lastupdate=ci[4],\
         status=ci[5], sql_id=n)              #create a node
    celeb_graph.add(c1)                               #add the node to the label
    c1.relationships.create("comes_from",s1)



orm.dis_connect([c,conn])
































