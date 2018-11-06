from __future__ import division
import sys
import os
import datetime
import json
import elasticsearch
from elasticsearch import Elasticsearch
from ssl import create_default_context


home_loc="/Enter home location/"
inp_loc=home_loc+"input/"
opt_loc=home_loc+"output/"
certs_loc=home_loc+"certs/"
timestamp = datetime.datetime.now().strftime("%Y.%m.%d")
targetindex = "*-emsbeat-"+timestamp
email = 0

with open(inp_loc+"exception.list","r") as et:
        explst = et.readlines()

with open(inp_loc+"sample.html","r") as HTML:
        html = HTML.read()

file = open(opt_loc+"report.html","w")

file.write(html)


es= Elasticsearch(
        ["nodes"],
        http_auth=('usr','pw'),
        port=9200,
        use_ssl=True,
        ca_certs=certs_loc+"chain_bundle.pem"
)

with open(inp_loc+"emspendingmessage.json","r") as Query:
        query = Query.read()


try:
        res = es.search(index=targetindex ,_source=["emsobject.URL","emsobject.Name","emsobject.PendingMessageCount","emsobject.PendingMessageSize","emsobject.ReceiverC  ount"], body=query
        )
except elasticsearch.exceptions.ConnectionError as e:
        print e
        errorhandle = open(opt_loc+"error.txt",'w')
        errorhandle.write("Error in connection to ELK Cluster, please check if port is correct and cluster is up\n")
        errorhandle.write(sys.argv[0])
        errorhandle.write(str(e))
        errorhandle.close()
        os.system(home_loc+"SendMailError.sh")
        sys.exit()

except elasticsearch.exceptions.NotFoundError as e:
        errorhandle = open(opt_loc+"error.txt",'w')
        errorhandle.write("Index - "+targetindex+"  Not found, please correct the Error Message")
        errorhandle.write(sys.argv[0])
        errorhandle.write(str(e))
        errorhandle.close()
        os.system(home_loc+"SendMailError.sh")
        sys.exit()

except elasticsearch.exceptions.RequestError as e:
        errorhandle = open(opt_loc+"error.txt",'w')
        errorhandle.write("Query has some error\n")
        errorhandle.write(sys.argv[0])
        errorhandle.write(str(e))
        errorhandle.close()
        os.system(home_loc+"SendMailError.sh")
        sys.exit()

except elasticsearch.exceptions.TransportError as e:
        errorhandle = open(opt_loc+"error.txt",'w')
        errorhandle.write("Error in json parsing, validate query\n")
        errorhandle.write(sys.argv[0])
        errorhandle.write(str(e))
        errorhandle.close()
        os.system(home_loc+"SendMailError.sh")
        sys.exit()


if res['hits']['total'] > 0:
        for eachrecord in range(0,len(res['hits']['hits'])):
                url = res['hits']['hits'][eachrecord]['_source']['emsobject']['URL']
                name = res['hits']['hits'][eachrecord]['_source']['emsobject']['Name']
                pmcount = res['hits']['hits'][eachrecord]['_source']['emsobject']['PendingMessageCount']
                pmsize = res['hits']['hits'][eachrecord]['_source']['emsobject']['PendingMessageSize']
                print type(pmsize)
                pmsize = pmsize / 1073741824
                print type(pmsize)
                print pmsize
                reccount = res['hits']['hits'][eachrecord]['_source']['emsobject']['ReceiverCount']
                #print str(url)+" "+str(name)+" "+str(pmcount)+" "+str(pmsize)+" "+str(reccount)
                if str(url+"-"+name) in explst:
                        print "Wakka Wakka"
                else:
                        email = 1
                        trd = '<tr><td>'+str(url)+'</td><td>'+str(name)+'</td><td>'+str(pmcount)+'</td><td>'+str(pmsize)+'</td><td>'+str(reccount)+'</td></tr>'
                        file.write(trd)
                        file.write("\n")
#               report = report.write(abc)

file.write('</table><br/><br/><br/><br/></BODY></HTML>')
file.close()

if email == 1:
        os.system(home_loc+"SendMail.sh")
