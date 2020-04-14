# Harvest Pure using Python

## Credits
Thanks to Elsevier for providing a code example. The link to the page in the Pure Client Space broke some time ago, so I included the example script in this repository.

Thank you, [Richard van Hoek](https://www.uu.nl/staff/RvanHoek), for doing the legwork on setting up python correctly and having a first go at the Elsevier example.

## References
General information on Pure web services:
[Pure Client Space](https://doc.pure.elsevier.com/display/PureClient/Webservices?src=sidebar) [Elsevier account required, please contact your Pure admin or IT engineer for access].

## Python setup

### Python download location
Download **Python 3.7.* or up** for your preferred OS from the [python.org website](https://www.python.org/downloads/).

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
lsevier's example script failed to loop due to a case sensitivity issue (xml parameter 'navigationLink' should read 'navigationlink') that was hard to spot but easy to fix.

Meanwhile, the script has changed dramatically. Core functions have remained intact, obviously, but some features were added, extended or modified. A short list:
1. Added logging of print statements to file for analysis in MS Excel.
2. Added code to enable running tests while varying webservice request sizes.
3. Added code to enable running tests with limited sets of data.
4. Added configuration file with parameters.
5. Added code and configuration parameters for output to json.
6. Added code and configuration parameters for looping through full set of records using a counter instead of the navigationlink property for (dramatic) performance enhancement.
7. Added code to save text files to mark start and end of running the script so it is clear to BI bods that the script has run a full cycle for a content type.

### Parameter configuration
The harvest script uses a configuration file with parameters for ease of testing and deployment. The name of the configuration file is hardcoded and shoud read **harvest-pure.cfg**. Parameters are divided into four groups as shown below.

#### Pure [PURE_PARAMS]
````python
PURE_API_VERSION = ws/api/<version>

Example: PURE_API_VERSION = ws/api/517
````
````python
PURE_API_KEY = <api key, see Pure admin section>
````
````python
PURE_URI = https://<yourPure>
````
````python
PURE_SYSTEM = <text, e.g. Staging, Production>

Example: PURE_SYSTEM = Staging
````
#### Webservice [WS_PARAMS]
````python
WS_OUTPUT = application/<outputType>

Example: WS_OUTPUT = application/json
````
````python
WS_FILETYPE = <filenameExtension>

Example: WS_FILETYPE = json
````
````python
WS_RENDERING = <rendering1>,<rendering2>...,<rendering.>

Example: WS_RENDERING = apa,harvard,mla
````
````python
WS_FIELDS = <field1>,<field2>...,<field.> or * for all fields

Example: WS_FIELDS = *
````

#### Run mode [RUN_PARAMS]
````python
RUN_METHOD = <0 = use navigationlink to next record set as returned by webservice call (performance hit), 1 = use counter of total number of records per site as returned by first webservice call>

Example: RUN_METHOD = 0
````
````python
RUN_BLNSAVE = <True = save file to disk, False = do not save file>

Example: RUN_BLNSAVE = True
````
````python
RUN_NUM_RECORDS = <n, number of records to retrieve per webservice request, use smaller numbers when testing>

Example: RUN_NUM_RECORDS = 500
````
````python
RUN_NUM_RUNS = <number of consecutive webservice calls, 0 = loop through full record set, > 0 when testing>

Example: RUN_NUM_RUNS = 5
````
````python
RUN_RESUME = <False = Start from scratch, anything before last download offset may be outdated, True = Continue from the last downloaded offset>

Example: RUN_RESUME = False
````
````python
RUN_BACKUP = <True = save file as copy to [PATH_OUTPUT_BACKUP], False = no extra save>

Example: RUN_BACKUP = True
````

#### Paths [PATH_PARAMS_HARVEST]
````python
Example: PATH_OUTPUT = /home/harvest-pure/data
````
````python
Example: PATH_OUTPUT_BACKUP = /home/harvest-pure/backup
````
````python
Example: PATH_LOG = /home/harvest-pure/logs
````
The parameters listed here are base paths. At runtime they will be filled out with
- PURE_API_VERSION
- PURE_SYSTEM
- RUN_METHOD
- WS_FILETYPE
- endpoint

Therefore, considering the parameter examples listed above, the full filepath of the first research output file saved to disk will read

````
/home/harvest-pure/data/s/api/517/Staging/0/json/research-outputs/20200414_research-outputs_000000.json
````

## Scheduling the script
[TODO]
