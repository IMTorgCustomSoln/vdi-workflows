


## Usage

### All Workflows

* add `.env` file with the following variables: 
    - HF_TOKEN - huggingface account
    - HF_HOME - models dir
    - CURL_CA_BUNDLE - public key (.pem)
* ensure folders are populated:
    - `logs/`
    - `pretrained_models/`
* set the following in `src/workflow_*.py`
    - `CONFIG['INPUT_DIR']` - location of input files
    - `CONFIG['WORKING_DIR']` - location for all files produced
* choose the workflow file from the `workflows/` directory.
* register it in the `main.py` file at `#register here`

```
python main.py workflow_* prepare_workspace
python main.py workflow_* run
```


### Automatic speech recognition, `-asr`

...


### Identifying and scraping websites, `-site_scrape`

* delete `tests/test_site_scrape/tmp/`
* set list of initial urls (one for each bank) in: `urls.txt`


### eComms discovery, `-ecomms`

...


### Text classification, `-text_classify`

...





## TODO:

* ???create separate `workflow-text_classify` and remove from ASR, Site_Scrape
* ~~create `workflow-template` to be used as a template~~
* add `workflow_template` Tasks tests


### Ecomms

* output to .json
* ingest data
  - create proper eDiscovery class with config (include col names)
  - ~~enable mapping provided .dat column names to default set~~
  - add text msg parse to ediscovery
  - (later)setup ediscovery with .msg parse
  - ~~improve validation rules~~
  - test
  - add to Task
* orgchart
  - ~~load orgchart~~
  - integrate org chart file: just get titles
  - add to Task
* prepare models
* export to VDI client
* (later) add visual message display


### ASR

* ~~create .csv list of files that are in each batch .gz
* ~~perform analysis on log files to estimate processing time
* integrate tests/
  - ~~test_workflow_asr.py~~
  - test_prepare_config.py
  - test_export.py
  - test_export_to_vdi_workspace.py
  - test_main.py
* maybe integrate improved whisper? english-only!, [ref: whisper-medusa](https://huggingface.co/aiola/whisper-medusa-v1)
* ensure multi-lingual whisper, [ref: multilingual](https://huggingface.co/openai/whisper-large-v3)


### Site_Scrape

* make modules
  - EnteroDoc
  - URL
* ~~mod  `urls.txt` and ValidateUrlsTask~~
  - ~~ValidateUrlsTask => ImportAndValidateUrlsTask~~
  - ~~change `urls.txt` to `urls.json`:~~
  ~~```urls.json
  {
  'bank_name': {
    'root_url: 'https://www...',
    'given_urls: [url1,url2, ...],
    }
  }
  ```~~
  - ~~`tmp/1_VALIDATED/urls.txt` to `valid_urls.json`~~
* mod Crawler
  - ~~`scenario.url` conflicts with crawler.check_urls_are_valid(url_list)~~
  - use consistent naming across tasks: ValidateUrlsTask, CrawlUrlsTask
  - remove: ~~generalize so 'jpmorgan' references is added to scenario~~
  - remove: ~~generalize so scenario, 'list_of_search_terms', can be changed~~
  - check why following are validated:
    + https://www.cardcenterdirect.com/
    + https://www.umb.edu/media/umassboston/editor-uploads/research/research-amp-sponsored-programs/Cost-Transfer-Policy--Procedures.pdf
* apply models
* ~~add new workflow-scraping~~
* ~~generalize classes for extensibility of workflows~~
* documentation
  - explain configuration adjustments
* ~~Workspace export~~
  - ~~no models applied~~
  - ~~record objects are not populated - only the first is repeated~~
* create reports
  - urls collected, validated, selected(reason)
  - document text results: hits, counts, snippets => VDI b-table export to excel, [ref](https://stackoverflow.com/questions/71465593/exporting-bootstrap-table-to-excel-or-pdf)
* compress pdf size with [`pdfsizeopt](https://github.com/pts/pdfsizeopt), but must update for py3.*, first