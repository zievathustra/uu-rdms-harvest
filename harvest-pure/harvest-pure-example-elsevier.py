###################################################
# This work is licensed under the Creative Commons Attribution 4.0 International License.
# To view a copy of this license, visit http://creativecommons.org/licenses/by/4.0/.
###################################################

import os
import fnmatch
import requests
from bs4 import BeautifulSoup as bs
import urllib3
import urllib
from urllib.parse import urlparse, parse_qs

# Threading - 1 thread per site
from multiprocessing.dummy import Pool as ThreadPool

# Suppress SSL warnings
urllib3.disable_warnings()

# Global properties
api_version = "ws/api/511"
output = "application/xml"

# save files yes/no
save = True

# contiue from the last downloaded offset, to avoid starting from scratch
resume = True

# Sites to harvest, base URL and API key required for each URL
# Name used for output folder
sites = [
    { "name": "YOUR_SITE",  "url": "https://YOUR_SITE.elsevierpure.com",    "api-key": "<YOUR_API_KEY>" },
]

# Endpoints to download for each site
endpoints = [
    "organisational-units",
    "persons",
    "journals",
    "events",
    "publishers",
    "research-outputs"
]

# content-specific parameters, e.g. rendering, ordering, etc.
content_parameters = {
    "research-outputs":
    [
        ("rendering", "BIBTEX"),
        ("rendering", "RIS"),
        ("fields", "*") # If you want renderings AND the fields, add this...
    ]
}

def main():

    pool = ThreadPool(len(sites))
    pool.map(get_site_contents, sites)
    #for site in sites:
    pool.close()
    pool.join()

def get_site_contents(site):
    print("{0} ({1}): ".format(site['name'], site['url']))

    for endpoint in endpoints:
        total = get_count(site, endpoint)
        print("{0}: {1}".format(endpoint, total))
        harvest_endpoint(site, endpoint, total)


# Harvests all content form an endpoint
def harvest_endpoint(site, endpoint, total):

    # add parameters:
    url = init_url(site['url'], endpoint)
    headers = get_headers(site)

    # if resuming from earlier, set start to where we left off
    start_offset = 0
    more_records = True

    if resume:
        start_offset = get_latest_offset(site, endpoint)
        print("Resuming {2} {3} from: {0} of {1}...".format(start_offset, total, site['name'], endpoint))

    while more_records:

        response = request(url, headers, {'offset': start_offset})

        # Parse out offset from URL provided by navigationLink
        offset = get_offset(response.url)
        print("Offset {0}...".format(offset))

        # Save page to disk
        if save:
            save_file(response, site['name'], "{0}_{1}".format(endpoint, offset))

        # Get XML data
        xml = bs(response.text, 'lxml')

        # Get next set of pages with navigation link
        navigationlink = xml.find('navigationLink', attrs = {"ref": "next"})
        if navigationlink:
            url = navigationlink['href']
        else:
            more_records = False

    print("Done with {0}'s {1}!".format(site['name'], endpoint))

# Gets the last offset for output files
# Note: does not handle 'gaps' - reharvest instead to fill in.
def get_latest_offset(site, endpoint):
    ep_files = []
    maximum = 0

    for dir, sub, files in os.walk("./" + site['name']+"/"):
        ep_files = list(f for f in files if endpoint in f)

    if ep_files:
        for f in ep_files:
            idx = int(f.split("_")[1].split(".")[0])
            maximum = max(idx, maximum)

    return maximum

# Get accept and api-key headers
def get_headers(site):
    return {
        "Accept": output,
        "api-key": site['api-key']
    }

# Get total number of records in endpoint
def get_count(site, endpoint):

    req = request(init_url(site['url'], endpoint), get_headers(site), {'pageSize': 1})
    count = bs(req.text, 'lxml').find('count')

    if count:
        return int(count.text)

    return 0

# add parameters and init URL
def init_url(url, endpoint):
    parameters = urllib.parse.urlencode(get_endpoint_parameters(endpoint), doseq=True)
    return "{0}/{1}/{2}?{3}".format(url, api_version, endpoint, parameters)

# Get content-specific parameters, if any, e.g. renderings, orderBy...
def get_endpoint_parameters(endpoint):
    if endpoint in content_parameters:
        return content_parameters[endpoint]
    return {}

# Save results to file
def save_file(response, folder, name):

    if not os.path.exists(folder):
        os.makedirs(folder)

    with open("{0}/{1}.xml".format(folder, name), 'wb') as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)

# Get page offset in the URL
def get_offset(url):
    q = parse_qs(urlparse(url).query)
    if 'offset' in q:
        return q['offset'][0]
    return 0

# Make HTTP request
def request(url, headers = {}, parameters = {}):
    return requests.get(url, parameters, headers = headers, verify = False)

# Call to main
main()
