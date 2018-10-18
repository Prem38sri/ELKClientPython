import os
import datetime
from elasticsearch import Elasticsearch
from ssl import create_default_context

timestamp = datetime.datetime.now().strftime("%Y.%m.%d")
targetindex = "index-name-"+timestamp

with open('INSTALL_HOME/sample.html','r') as HTML:
        html = HTML.read()

file = open("INSTALL_HOME/report.html","w")

file.write(html)


es= Elasticsearch(
        ["node1","node2","node3"],
        http_auth=('elastic','7uDY5K7r8HEhm7mdTsMW'),
        port=9200,
        use_ssl=True,
        ca_certs='INSTALL_HOME/chain_bundle.pem'
)

res = es.search(index=targetindex ,_source=["@timestamp","emsobject.Name","emsobject.PendingMessageCount","emsobject.ReceiverCount"], body={
                "query": {
                                "bool": { "must":
                                [
                                        { "range": { "@timestamp": {"from": "now-15m","to": "now" }}},
                                        { "match": { "emsobject.URL": "EMS_URL" }},
                                        { "match": { "emsobject.type.keyword": "queue" }},
                                        { "terms": { "emsobject.Name.keyword": ["queue1","queue2"] }},
                                        { "range": { "emsobject.PendingMessageCount" : { "gte":2000} }}
                                ]
                                }
                        }
                }
        )
if res['hits']['total'] > 0:
        email = 1
        for eachrecord in range(0,len(res['hits']['hits'])):
            Name = res['hits']['hits'][eachrecord]['_source']['emsobject']['Name']
Pmc = res['hits']['hits'][eachrecord]['_source']['emsobject']['PendingMessageCount']
Rc = res['hits']['hits'][eachrecord]['_source']['emsobject']['ReceiverCount']
trd = '<tr><td>' + Name + '</td><td>' + str(Pmc) + '</td><td>' + str(Rc) + '</td></tr>'
file.write(trd)
file.write("\n")
#               report = report.write(abc)

file.write('</table><br/><br/><br/><br/></BODY></HTML>')
file.close()

if email == 1:
    os.system("INSTALL_HOME/SendMail.sh")
