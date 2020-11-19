from urllib.parse import urlencode
from urllib.request import urlopen
from xml.dom.minidom import parse, parseString
import sys
import os
import datetime
import configparser

config = configparser.ConfigParser()
config.read('config_yoda.ini')

path_output = config['PATH_PARAMS_HARVEST']['PATH_OUTPUT']
if not os.path.exists(path_output):
    os.makedirs(path_output)

path_log = config['PATH_PARAMS_HARVEST']['PATH_LOG']
if not os.path.exists(path_log):
    os.makedirs(path_log)

init_baseURL = config['YODA_PARAMS']['YODA_BASE_URI']
init_verb = config['YODA_PARAMS']['YODA_VERB']
init_meta = config['YODA_PARAMS']['YODA_META']
init_set = config['YODA_PARAMS']['YODA_SET']
getRecordsURL = init_baseURL + init_verb + init_meta + init_set

# Output print statements to file, too.
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(path_log + "/harvestYoda.log", "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass

sys.stdout = Logger()

# function for return dom response after parsting oai-pmh URL
def oaipmh_response(URL):
 file = urlopen(URL)
 data = file.read()
 file.close()

 dom = parseString(data)
 return dom

# function for getting value of resumptionToken after parsting oai-pmh URL
def oaipmh_resumptionToken(URL):
 file = urlopen(URL)
 data = file.read()
 file.close()

 dom = parseString(data)
 print("START: "+str(datetime.datetime.now()))
 tags = dom.getElementsByTagName('resumptionToken')
 if tags :
     if tags[0].firstChild is not None :
         return tags[0].firstChild.nodeValue
     else:
         return ""
 else:
     return ""

# function for writing to output files
def write_xml_file(inputData, outputFile):
 oaipmhResponse = open(outputFile, mode="w", encoding='utf-8')
 oaipmhResponse.write(inputData)
 oaipmhResponse.close()
 print("END: " + str(datetime.datetime.now()))

# main code

# initial parse phase
pageCounter = 0
resumptionToken = oaipmh_resumptionToken(getRecordsURL) # get initial resumptionToken
print("Resumption Token: "+resumptionToken)
outputFile = path_output + "/harvest-page-{0:0>4}".format(pageCounter) + '.xml' # define initial file to use for writing response
write_xml_file(oaipmh_response(getRecordsURL).toxml(), outputFile)

# loop parse phase
pageCounter = 1
while resumptionToken != "":
 print("URL ENCODED TOKEN: "+resumptionToken)
 resumptionToken = urlencode({'resumptionToken':resumptionToken}) # create resumptionToken URL parameter
 print("Resumption Token: "+resumptionToken)
 getRecordsURLLoop = str(init_baseURL + init_verb + '&' + resumptionToken)
 oaipmhXML = oaipmh_response(getRecordsURLLoop).toxml()
 outputFile = path_output + "/harvest-page-{0:0>4}".format(pageCounter) + '.xml' # create file name to use for writing response
 write_xml_file(oaipmhXML, outputFile) # write response to output file

 resumptionToken = oaipmh_resumptionToken(getRecordsURLLoop)
 pageCounter += 1 # increment page counter
