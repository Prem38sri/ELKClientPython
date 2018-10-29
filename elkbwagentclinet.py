import sys
import os
import datetime
import json
import elasticsearch
from elasticsearch import Elasticsearch
from ssl import create_default_context

home_loc="/apps/tibco/TIBCO_ALERTS/BWAGENT/"
inp_loc=home_loc+"input/"
opt_loc=home_loc+"output/"
certs_loc=home_loc+"certs/"
timestamp = datetime.datetime.now().strftime("%Y.%m.%d")
targetindex = "*-tibcobeat-"+timestamp
email = 0



with open(inp_loc+"sample.html","r") as HTML:
        html = HTML.read()

file = open(opt_loc+"report.html","w")

file.write(html)


es= Elasticsearch(
        ["nod01","nod02","nod03"],
        http_auth=('home','pwd'),
        port=9200,
        use_ssl=True,
        ca_certs=certs_loc+"chain_bundle.pem"
)

with open(inp_loc+"querybwagent.json","r") as Query:
        query = Query.read()


try:
        res = es.search(index=targetindex ,_source=["BW6agent.instance","BW6agent.agent","BW6agent.machine","BW6agent.machin","BW6agent.state"], body=query
        )
except elasticsearch.exceptions.ConnectionError as e:
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
        email = 1
        for eachrecord in range(0,len(res['hits']['hits'])):
                instance = res['hits']['hits'][eachrecord]['_source']['BW6agent']['instance']
                agent = res['hits']['hits'][eachrecord]['_source']['BW6agent']['agent']
                machine = res['hits']['hits'][eachrecord]['_source']['BW6agent']['machine']
                status = res['hits']['hits'][eachrecord]['_source']['BW6agent']['state']
                print str(instance)+" "+str(agent)+" "+str(machine)+" "+str(status)
                trd = '<tr><td>'+str(instance)+'</td><td>'+str(agent)+'</td><td>'+str(machine)+'</td><td>+str(status)+</td></tr>'
                file.write(trd)
                file.write("\n")
#               report = report.write(abc)

file.write('</table><br/><br/><br/><br/></BODY></HTML>')
file.close()


if email == 1:
        os.system(home_loc+"SendMail.sh")
