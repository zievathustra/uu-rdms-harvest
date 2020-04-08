# [REPOSITORY]     : https://github.com/zievathustra/uu-rdms-harvest
# [LICENSE]        : This work is licensed under the Creative Commons Zero v1.0 Universal license.
#                    To view a copy of this license, visit https://creativecommons.org/publicdomain/zero/1.0/.
# [SOURCE#1]       : Elsevier Python example, see files section in repository on GitHub                                                                                                                                       #
#                    https://doc.pure.elsevier.com/display/PureClient/Python+Examples#PythonExamples-PureWebService513Example
# [SOURCE#2]       : Logger class for outputting print statements to file]
#                    https://stackoverflow.com/questions/14906764/how-to-redirect-stdout-to-both-file-and-console-with-scripting/14906787
# [AUTHOR]         : Arjan Sieverink, Utrecht University
# [CONTACT#1]      : https://www.uu.nl/staff/JASieverink
# [CONTACT#2]      : https://www.linkedin.com/in/arjansieverink
# [REMARKS]        :

# IMPORTS
# *Generic
import os
import sys
import configparser
import datetime
import fnmatch
# *Logging
import traceback
import logging
# *Requests
import requests
import urllib3
import urllib
from urllib.parse import urlparse, parse_qs
# *XML
from bs4 import BeautifulSoup as bs
# *JSON
import json


try:
    # Get handle to configuration file, must be located in same folder as .py file
    config = configparser.ConfigParser()
    config.read('harvest-pure.cfg')

    # Threading - 1 thread per site
    from multiprocessing.dummy import Pool as ThreadPool

    # Suppress SSL warnings
    urllib3.disable_warnings()

    # Global properties
    api_version = config['PURE_PARAMS']['PURE_API_VERSION']
    output = config['WS_PARAMS']['WS_OUTPUT']
    fileType = config['WS_PARAMS']['WS_FILETYPE']
    blnSave = eval(config['WS_PARAMS']['WS_BLNSAVE'])
    run_method = config['RUN_PARAMS']['RUN_METHOD']
    num_records = config['RUN_PARAMS']['RUN_NUM_RECORDS']
    num_runs = config['RUN_PARAMS']['RUN_NUM_RUNS']
    resume = eval(config['RUN_PARAMS']['RUN_RESUME'])
    num_logLine = 0 # Enumerate log lines for sorting purposes
    path_output = config['PATH_PARAMS_HARVEST']['PATH_OUTPUT'] + "/" + config['PURE_PARAMS']['PURE_API_VERSION'] + "/" + config['PURE_PARAMS']['PURE_SYSTEM']
    path_log = config['PATH_PARAMS_HARVEST']['PATH_LOG'] + "/" + config['PURE_PARAMS']['PURE_API_VERSION'] + "/" + config['PURE_PARAMS']['PURE_SYSTEM']
    rendering = config['WS_PARAMS']['WS_RENDERING']
    fields = config['WS_PARAMS']['WS_FIELDS']


    # Save files yes/no, assign variables for proper saving
    save = blnSave
    path_output = path_output + "/" + str(run_method) + "/" + fileType
    if not os.path.exists(path_output):
        os.makedirs(path_output)
    path_log = path_log + "/" + str(run_method) + "/" + fileType + "/logs"
    if not os.path.exists(path_log):
        os.makedirs(path_log)

    # Sites to harvest, base URL and API key required for each URL
    # Name used for output folder
    sites = [
        { "name": "UU Pure " + config['PURE_PARAMS']['PURE_SYSTEM'] + " " + str(num_records),
        "url": config['PURE_PARAMS']['PURE_URI'],
        "api-key": config['PURE_PARAMS']['PURE_API_KEY'] },
    ]

    # Endpoints to download for each site, not all endpoints are relevant at this point in time.
    endpoints = [
        "activities",
    #    "applications",
    #    "author-collaborations",
    #    "awards",
    #    "classification-schemes",
    #    "curricula-vitae",
    #    "datasets",
    #    "equipments",
    #    "ethical-reviews",
    #    "events",
    #    "external-organisations",
    #    "external-persons",
    #    "funding-opportunities",
    #    "impacts",
    #    "journals",
    #    "keyword-group-configuration",
        "organisational-units",
    #    "organisational-units/active",
    #    "organisational-units/former",
        "persons",
        "press-media",
        "prizes",
    #    "projects",
    #    "publishers",
	    "research-outputs",
    #    "student-theses"
    ]

    # content-specific parameters, e.g. rendering, ordering, etc.
    content_parameters = {
        "activities":
        [
            ("size", num_records)
        ],
        "applications":
        [
            ("size", num_records)
        ],
        "author-collaborations":
        [
            ("size", num_records)
        ],
        "awards":
        [
            ("size", num_records)
        ],
        "classification-schemes":
        [
            ("size", num_records)
        ],
        "curricula-vitae":
        [
            ("size", num_records)
        ],
        "datasets":
        [
            ("size", num_records)
        ],
        "equipments":
        [
            ("size", num_records)
        ],
        "ethical-reviews":
        [
            ("size", num_records)
        ],
        "events":
        [
            ("size", num_records)
        ],
        "external-organisations":
        [
            ("size", num_records)
        ],
        "external-persons":
        [
            ("size", num_records)
        ],
        "funding-opportunities":
        [
            ("size", num_records)
        ],
        "impacts":
        [
            ("size", num_records)
        ],
        "journals":
        [
            ("size", num_records)
        ],
        "keyword-group-configuration":
        [
            ("size", num_records)
        ],
        "organisational-units":
        [
            ("size", num_records)
        ],
        "organisational-units/active":
        [
            ("size", num_records)
        ],
        "organisational-units/former":
        [
            ("size", num_records)
        ],
        "persons":
        [
            ("size", num_records)
        ],
        "press-media":
        [
            ("size", num_records)
        ],
        "prizes":
        [
            ("size", num_records)
        ],
        "projects":
        [
            ("size", num_records)
        ],
        "publishers":
        [
            ("size", num_records)
        ],
        "research-outputs":
        [
            ("size", num_records),
			("rendering", rendering),
			("fields", fields)
        ],
        "student-theses":
        [
            ("size", num_records)
        ]
    }

except Exception as e:
    print(traceback.format_exc())

# Output print statements to file, too.
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(path_log + "/{:%Y%m%d}".format(datetime.datetime.now()) + "_harvestPure_{0:0>4}".format(num_records) + "_" + "{0:0>4}".format(num_runs) + ".log", "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # This flush method is needed for python 3 compatibility.
        # This handles the flush command by doing nothing.
        # You might want to specify some extra behaviour here.
        pass

sys.stdout = Logger()


def main():
    try:
        global num_logLine
        num_logLine += 1
        print(str(num_logLine) + "," + str(num_records) + ",,,,START," + str(datetime.datetime.now()))
        pool = ThreadPool(len(sites))
        pool.map(get_site_contents, sites)
        #for site in sites:
        pool.close()
        pool.join()
        num_logLine += 1
        print(str(num_logLine) + "," + str(num_records) + ",,,,STOP," + str(datetime.datetime.now()))
    except Exception as e:
         print(traceback.format_exc())
    quit()

def get_site_contents(site):
    try:
        global num_logLine
        num_logLine += 1
        print(str(num_logLine) + "," + str(num_records) + ",,,,{0} ({1}): ".format(site['name'], site['url']) + "," + str(datetime.datetime.now()))

        for endpoint in endpoints:
            total = get_count(site, endpoint)
            num_logLine += 1
            print(str(num_logLine) + "," + str(num_records) + ",," + str(total) + ",{0}".format(endpoint) + ",START," + str(datetime.datetime.now()))
            # write text file to indicate start harvesting for <endpoint>, format yyyy-<endpoint>-start.text
            save_file(True, "start", path_output + "/" + endpoint.replace('/', '-'), "{0}_{1}_{2}".format("{:%Y%m%d}".format(datetime.datetime.now()),endpoint.replace('/', '-'), "start"), "txt")
            harvest_endpoint(site, endpoint, total)
            # write text file to indicate end harvesting for <endpoint>, format yyyy_<endpoint>_start.text
            save_file(True, "end", path_output + "/" + endpoint.replace('/', '-'), "{0}_{1}_{2}".format("{:%Y%m%d}".format(datetime.datetime.now()),endpoint.replace('/', '-'), "end"), "txt")
            num_logLine += 1
            print(str(num_logLine) + "," + str(num_records) + ",," + str(total) + ",{0}".format(endpoint) + ",STOP," + str(datetime.datetime.now()))
    except Exception as e:
        print(traceback.format_exc())


# Harvests all content form an endpoint
def harvest_endpoint(site, endpoint, total):
    try:

        # set log line number
        global num_logLine

        # add parameters:
        url = init_url(site['url'], endpoint, True)
        headers = get_headers(site)

        # initialize run parameters
        if int(num_runs) > 0: # then we're NOT processing the full record set, just a defined number of runs (=loops)
               run_times = 0
        else:
               run_times = -1 # then we ARE processing the full record set, since a. run_times will not be updated after initialze and b. run_times will stay less than int(num_runs)
        more_records = True

        # if resuming from earlier, set start to where we left off
        if resume:
            start_offset = get_latest_offset(site, endpoint)
            total_remainder = total - (start_offset - int(num_records))
        else:
            start_offset = 0
            total_remainder = total


        # loop through record sets for current endpoint
        while more_records and run_times < int(num_runs):
            # Set run_times
            if int(num_runs) > 0:
                run_times = run_times + 1

            # Get response
            num_logLine += 1
            print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",Webservice request" + ","  + str(datetime.datetime.now()))
            response = request(url, headers, {'offset': start_offset})
            num_logLine += 1
            print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",Webservice response" + "," + str(datetime.datetime.now()))

            # Save page to disk
            if save:
                num_logLine += 1
                print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",Start save page to disk" + "," + str(datetime.datetime.now()))
                #save_file(response, path_output, "{0}_{1}_{2}".format("{:%Y%m%d}".format(datetime.datetime.now()),endpoint.replace('/', '-'), "{0:0>6}".format(start_offset)), fileType)
                save_file(False, response, path_output + "/" + endpoint.replace('/', '-'), "{0}_{1}_{2}".format("{:%Y%m%d}".format(datetime.datetime.now()),endpoint.replace('/', '-'), "{0:0>6}".format(start_offset)), fileType)
                num_logLine += 1
                print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",End save page to disk" + "," + str(datetime.datetime.now()))

            total_remainder = total_remainder - int(num_records)

            if int(run_method) > 0: # Do NOT use navigationLink property to get next offset, use counter instead
                if total_remainder > 0:
                    start_offset = start_offset + int(num_records)
                else:
                    more_records = False
            else:
                # Get XML or JSON data in order to get a handle to navigationlink later on
                if output == 'application/xml': # Get XML data
                    num_logLine += 1
                    print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",Start Get XML data" + "," + str(datetime.datetime.now()))
                    xml = bs(response.text, 'lxml')
                    num_logLine += 1
                    print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",End Get XML data" + "," + str(datetime.datetime.now()))

                    # Get next set of pages with navigation link
                    num_logLine += 1
                    print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",Start Get next set of pages with navigation link" + "," + str(datetime.datetime.now()))
                    navigationlink = xml.find('navigationlink', attrs = {"ref": "next"})
                    num_logLine += 1
                    print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",End Get next set of pages with navigation link" + "," + str(datetime.datetime.now()))
                else: # Get JSON data
                    num_logLine += 1
                    print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",Start Get JSON data" + "," + str(datetime.datetime.now()))
                    response_dict['navigationLink'] = list(filter(lambda x: x['ref'] == 'next', response_dict['navigationLink']))
                    num_logLine += 1
                    print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",End Get JSON data" + "," + str(datetime.datetime.now()))

                    # Get next set of pages with navigation link
                    num_logLine += 1
                    print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",Start Get next set of pages with navigation link" + "," + str(datetime.datetime.now()))
                    navigationlink = response_dict['navigationLink']
                    num_logLine += 1
                    print(str(num_logLine) + "," + str(num_records) + "," + str(run_times) + "," + str(total_remainder)+ "," + endpoint + ",End Get next set of pages with navigation link" + "," + str(datetime.datetime.now()))
                if navigationlink:
                    if output == 'application/xml':
                        url = navigationlink['href']
                    else:
                        url = navigationlink[0]['href']
                    # Parse offset from URL provided by navigationLink
                    start_offset = get_offset(url)
                else:
                    more_records = False

    except Exception as e:
        print(traceback.format_exc())

# Gets the latest offset for output files
# Note: does not handle 'gaps' - reharvest instead to fill in.
# Note: os,walk does not seem to work properly on Linux, further troubleshooting needed
def get_latest_offset(site, endpoint):
    try:
        ep_files = []
        maximum = 0
        for root, dirs, files in os.walk(path_output + "/"):
            ep_files = list(f for f in files if endpoint in f)

        if ep_files:
            for f in ep_files:
                idx = int(f.split("_")[1].split(".")[0])
                maximum = max(idx, maximum)
        return maximum
    except Exception as e:
        print(traceback.format_exc())

# Get accept and api-key headers
def get_headers(site):
    try:
        return {
            "Accept": output,
            "api-key": site['api-key']
        }
    except Exception as e:
        print(traceback.format_exc())

# Get total number of records in endpoint
def get_count(site, endpoint):
    try:
        req = request(init_url(site['url'], endpoint, False), get_headers(site), {'pageSize': 1})
        if output == 'application/json':
            req_dict = json.loads(req.text)
            count = req_dict['count']
        else:
            count = bs(req.text, 'lxml').find('count')
            count = count.text

        if count:
            return int(count)

        return 0
    except Exception as e:
       print(traceback.format_exc())


# add parameters and init URL
def init_url(url, endpoint, getParams):
    try:
        if getParams: # We need different uri's for getting the count and looping through the record set
            parameters = urllib.parse.urlencode(get_endpoint_parameters(endpoint), doseq=True)
            return "{0}/{1}/{2}?{3}".format(url, api_version, endpoint, parameters)
        return "{0}/{1}/{2}?{3}".format(url, api_version, endpoint, {})
    except Exception as e:
        print(traceback.format_exc())

# Get content-specific parameters, if any, e.g. renderings, orderBy...
def get_endpoint_parameters(endpoint):
    try:
        if endpoint in content_parameters:
            return content_parameters[endpoint]
        return {}
    except Exception as e:
        print(traceback.format_exc())

# Save results to file
def save_file(blnTextOnly, response, folder, name, fileType):
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)

        if blnTextOnly:
            file = open("{0}/{1}.{2}".format(folder, name, fileType), 'w')
            file.write(response)
            file.close()
        else:
            with open("{0}/{1}.{2}".format(folder, name, fileType), 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
    except Exception as e:
        print(traceback.format_exc())

# Get page offset in the URL
def get_offset(url):
    try:
        q = parse_qs(urlparse(url).query)
        if 'offset' in q:
            return q['offset'][0]
        return 0
    except Exception as e:
        print(traceback.format_exc())

# Make HTTP request
def request(url, headers = {}, parameters = {}):
    try:
        return requests.get(url, parameters, headers = headers, verify = False)
    except Exception as e:
        print(traceback.format_exc())

# Call to main
main()
