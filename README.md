# Harvest Pure using Python
Please note that links will NOT open in a new tab or window, so please use right-mouse-click and the appropriate action to open. This is due to limitations to GitHubs markdown implementation (no support for ``{:target="_blank"}``). And my sticking to readability of my own markdown input in Atom as opposed to replacing all links with ``<a></a>`` tags, to be frank.

## Credits
Thanks to Elsevier for providing a code example. The link to the page in the Pure Client Space broke some time ago, so I included the example script in this repository.

Thank you, [Richard van Hoek](https://www.uu.nl/staff/RvanHoek), for doing the legwork on setting up python correctly and having a first go at the Elsevier example.

## References
General information on Pure web services:
[Pure Client Space](https://doc.pure.elsevier.com/display/PureClient/Webservices?src=sidebar) [Elsevier account required, please contact your Pure admin or IT engineer for access].

## Python setup

### Python download location
Download **Python 3.7.x or up** for your preferred OS from the [python.org website](https://www.python.org/downloads/).

### Python packages
Make sure you have these packages installed, too:
1. [pip](https://pypi.org/project/pip/)
2. [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
3. [lxml](https://pypi.org/project/lxml/)
4. [requests](https://pypi.org/project/requests/)

### Python IDE
The python download comes with the [Python IDLE](https://docs.python.org/3/library/idle.html) IDE. It's basic but functional. Should you require more code editing tools or GitHub support, please find a tool of your liking on the net. I use [Atom](https://atom.io/) and [PyCharm Professional](https://www.jetbrains.com/pycharm/) concurrently.

## Harvesting Pure - output to xml, JSON

### Basics
The Pure API is designed to retrieve a limited number of records per request. Therefore, multiple requests are needed to harvest all records of any given content type. The default is set to ten (10) records at a time, but it is allowed to overrule this setting. Any given response includes a navigation link in order to launch a new request from an offset point, thus allowing for looping through the full record set. Alternatively, the record count that is listed in the resulting xml or json object may be used for 'smart' looping.

The python code harvests ALL records of a given content type. Ideally, processing changes only would be the sensible option, but since the datamodel and its relations / associations are not transparent this may prove to be a cumbersome exercise, as illustrated in the Elsevier documentation as follows:

> **Changes in associated content**    
    The changes API will only return changes within a single content item and not that of its associated content. For example if a ResearchOutput changes its title or year it will be output as a change event of type ResearchOutput whereas if the name of an associated author changes that will not be included in the ResearchOutput change. In stead it will be part of a Person change. If you need data to be re-fetched when associated data changes, for example in the above example where a rendering of the author list could be affected, you will need to keep track on the relation between content items in such a way that the person change can be used to lookup affected research output. [link](https://doc.pure.elsevier.com/pages/viewpage.action?pageId=27697561)


### Example
Elsevier has developed a basic script to harvest Pure. It is designed to harvest multiple endpoints and write the output to file. Please note that a single request will result in saving a corresponding, single file. Moreover, not all endpoints are included in the example and only basic content parameters are listed. A more comprehensive study of the API documentation should open up the full potential of the script.

### Put to work
Elsevier's example script failed to loop due to a case sensitivity issue (xml parameter 'navigationLink' should read 'navigationlink') that was hard to spot but easy to fix.

Meanwhile, the script has changed dramatically. Core functions have remained intact, obviously, but some features were added, extended or modified. A short list:
1. Added logging of print statements to file for analysis.
2. Added code to enable running tests while varying webservice request sizes.
3. Added code to enable running tests with limited sets of data.
4. Added configuration file with parameters.
5. Added code and configuration parameters for output to json.
6. Added code and configuration parameters for looping through full set of records using a counter instead of the navigationlink property for (dramatic) performance enhancement.
7. Added code to save text files to mark start and end of running the script so it is clear to whomever uses the files that the script has run a full cycle for a content type.

### Parameter configuration
The harvest script uses a configuration file with parameters for ease of testing and deployment. The name of the configuration file is hardcoded and shoud read **harvest-pure.cfg**. Parameters are divided into four groups as shown below.

#### Pure [PURE_PARAMS]
````json
PURE_API_VERSION = ws/api/<version>

Example: PURE_API_VERSION = ws/api/517
````
````json
PURE_API_KEY = <api key, see Pure admin section>
````
````json
PURE_URI = https://<yourPure>
````
````json
PURE_SYSTEM = <text, e.g. Staging, Production>

Example: PURE_SYSTEM = Staging
````
#### Webservice [WS_PARAMS]
````json
WS_OUTPUT = application/<outputType>

Example: WS_OUTPUT = application/json
````
````json
WS_FILETYPE = <filenameExtension>

Example: WS_FILETYPE = json
````
````json
WS_RENDERING = <rendering1>,<rendering2>...,<rendering.>

Example: WS_RENDERING = apa,harvard,mla
````
````json
WS_FIELDS = <field1>,<field2>...,<field.> or * for all fields

Example: WS_FIELDS = *
````

#### Run mode [RUN_PARAMS]
````json
RUN_METHOD = <0 = use navigationlink to next record set as returned by webservice call (performance hit), 1 = use counter of total number of records per site as returned by first webservice call>

Example: RUN_METHOD = 0
````
````json
RUN_BLNOVERRIDE = <True = skip adding PURE_PARAMS and WS_PARAMS to file path, False = add PURE_PARAMS and WS_PARAMS to file path>

Example: RUN_BLNOVERRIDE = False
````

````json
RUN_BLNSAVE = <True = save file to disk, False = do not save file>

Example: RUN_BLNSAVE = True
````
````json
RUN_NUM_RECORDS = <n, number of records to retrieve per webservice request, use smaller numbers when testing>

Example: RUN_NUM_RECORDS = 500
````
````json
RUN_NUM_RUNS = <number of consecutive webservice calls, 0 = loop through full record set, > 0 when testing>

Example: RUN_NUM_RUNS = 5
````
````json
RUN_RESUME = <False = Start from scratch, anything before last download offset may be outdated, True = Continue from the last downloaded offset>

Example: RUN_RESUME = False
````
````json
RUN_BACKUP = <True = save file as copy to [PATH_OUTPUT_BACKUP], False = no extra save>

Example: RUN_BACKUP = True
````

#### Paths [PATH_PARAMS_HARVEST, Linux version]
````json
Example: PATH_OUTPUT = /home/harvest-pure/data
````
````json
Example: PATH_OUTPUT_BACKUP = /home/harvest-pure/backup
````
````json
Example: PATH_LOG = /home/harvest-pure/logs
````
The parameters listed here are base paths. At runtime they will be filled out with
- PURE_API_VERSION
- PURE_SYSTEM
- RUN_METHOD
- WS_FILETYPE
- endpoint

**unless** the RUN parameter BLN_OVERRIDE is set to True.

Therefore, when BLN_OVERRIDE is set to False, considering the parameter examples listed above, the full filepath of the first research output file saved to disk will read

````
/home/harvest-pure/data/s/api/517/Staging/0/json/research-outputs/20200414_research-outputs_000000.json
````

## Scheduling

### Linux
Use [crontab](https://tecadmin.net/crontab-in-linux-with-20-examples-of-cron-schedule/) to schedule a cron job to run the script at intervals. Define the crontab parameters in e text file and add the job to the cron list a terminal window as follows.
```
crontab <filename>
```
List the currently active cron jobs in a terminal window using
```
crontab -l
```
An example cron job running daily at 17h00 could look like
```
0 17 * * * /usr/bin/python3.7 /home/sieve002/uu-rdms-harvest/harvest-pure.py
```

### Windows (client, server)
Use the Windows Task Scheduler to run the script at intervals on Windows machines. Configure authorisation and trigger(s) as you see fit. The action should be configured as follows:

**Command**
```
<path to python executable>\python.exe
```
**Arguments**
```
harvest-pure.py
```
**Working directory**
```
<path to working directory = path to harvest-pure.py and harvest-pure.cfg>
```

## Disclaimer
I'm no python guru...so I started with basic knowledge, I searched the net and where I hit a wall I tried and failed until I got it working again, step by step. Please allow for code that won't win awards and feel free to share your suggestions for improvement.

You're welcome to find me at [Utrecht University](https://www.uu.nl/staff/JASieverink) or at [LinkedIn](https://www.linkedin.com/in/arjansieverink).
