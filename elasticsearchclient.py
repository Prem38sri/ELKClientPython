import sys
import os
import datetime
import json
import elasticsearch
from elasticsearch import Elasticsearch
from ssl import create_default_context

timestamp = datetime.datetime.now().strftime("%Y.%m.%d")
targetindex = "index"+timestamp
email = 0



with open('INSTALL_HOME/input/sample.html','r') as HTML:
        html = HTML.read()

file = open("INSTALL_HOME/output/report.html","w")

file.write(html)


es= Elasticsearch(
        ["node1","node2"],
        http_auth=('user','password'),
        port=9200,
        use_ssl=True,
        ca_certs='INSTALL_HOME/certs/chain_bundle.pem'
)

with open('INSTALL_HOME/input/query.json','r') as Query:
        query = Query.read()


try:
        res = es.search(index=targetindex ,_source=["@timestamp","emsobject.Name","emsobject.PendingMessageCount","emsobject.ReceiverCount"], body=query
        )
except elasticsearch.exceptions.ConnectionError as e:
        errorhandle = open("INSTALL_HOME/output/error.txt",'w')
        errorhandle.write("Error in connection to ELK Cluster, please check if port is correct and cluster is up\n")
        errorhandle.write(sys.argv[0])
        errorhandle.write(str(e))
        errorhandle.close()
        os.system("INSTALL_HOME/SendMailError.sh")
        sys.exit()

except elasticsearch.exceptions.NotFoundError as e:
        errorhandle = open("INSTALL_HOME/output/error.txt",'w')
        errorhandle.write("Index - "+targetindex+"  Not found, please correct the Error Message")
        errorhandle.write(sys.argv[0])
        errorhandle.write(str(e))
        errorhandle.close()
        os.system("INSTALL_HOME/SendMailError.sh")
        sys.exit()

except elasticsearch.exceptions.RequestError as e:
        errorhandle = open("INSTALL_HOME/output/error.txt",'w')
        errorhandle.write("Query has some error\n")
        errorhandle.write(sys.argv[0])
        errorhandle.write(str(e))
        errorhandle.close()
        os.system("INSTALL_HOME/SendMailError.sh")
        sys.exit()

except elasticsearch.exceptions.TransportError as e:
        errorhandle = open("INSTALL_HOME/output/error.txt",'w')
        errorhandle.write("Error in json parsing, validate query\n")
        errorhandle.write(sys.argv[0])
        errorhandle.write(str(e))
        errorhandle.close()
        os.system("INSTALL_HOME/SendMailError.sh")
        sys.exit()


if res['hits']['total'] > 0:
        email = 1
        for eachrecord in range(0,len(res['hits']['hits'])):
                Name = res['hits']['hits'][eachrecord]['_source']['emsobject']['Name']
                Pmc = res['hits']['hits'][eachrecord]['_source']['emsobject']['PendingMessageCount']
                Rc = res['hits']['hits'][eachrecord]['_source']['emsobject']['ReceiverCount']
                trd = '<tr><td>'+Name+'</td><td>'+str(Pmc)+'</td><td>'+str(Rc)+'</td></tr>'
                file.write(trd)
                file.write("\n")
#               report = report.write(abc)

file.write('</table><br/><br/><br/><br/></BODY></HTML>')
file.close()


if email == 1:
        os.system("INSTALL_HOME/SendMail.sh")
