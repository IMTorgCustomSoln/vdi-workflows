#!/usr/bin/env python3
"""
Task class


TODO: apply `get_next_run_files()` to new Tasks
  - but instead of simple review of files, apply to content of files
  - ensure it picks-up at last url - it is currently only designed for last file
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Files import File
from src.io import export
from src.io import utils
from src.modules.enterodoc.url import UrlFactory#, UrlEncoder

from pathlib import Path
import sys
import datetime


class Task:
    """..."""

    def __init__(self, config, input, output, name_diff=''):
        self.config = config
        self.input_files = input
        if output.directory.is_dir():
            self.output_files = output
        else:
            raise Exception(f'target_folder not found: {output}')
        self.name_diff = name_diff
    
    def get_next_run_files(self):
        """Get the remaining files that should be provided to run()
        Each record is an file and they are processed, individually, as opposed
        to multiple records within a file.

        Typically:
        * get input files
        * get output files
        * get remainder files by comparing input to output

        TODO:add as function to Files.py and ensure appropriate attr: .name, .stem, etc.
        """
        Type = 'name_only'
        input_names = set(self.input_files.get_files(type=Type))
        processed_names = set([file.replace(self.name_diff,'') for file in self.output_files.get_files(type=Type)])
        remainder_names = list( input_names.difference(processed_names) )
        if len(remainder_names)>0 and Type == 'name_only':
            remainder_paths = [file for file in self.input_files.get_files() 
                               if utils.remove_all_extensions_from_filename(file.stem) in remainder_names    #TODO:possible error for workflow_site_scrape
                               ]
        else:
            remainder_paths = []
        return remainder_paths

    def run(self):
        """Run processing steps on input files"""
        pass


class ImportTask(Task):
    """..."""



class ExportTask(Task):
    """..."""





from src.io import utils

class UnzipTask(Task):
    """Decompress archive files in a folder"""

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_folder = output.directory
        self.target_extension=['.wav','.mp3']

    def run(self):
        sound_files_list = []
        for file in self.get_next_run_files():
            extracted_sound_files = utils.decompress_filepath_archives(
                filepath=file,
                extract_dir=self.target_folder,
                target_extension=self.target_extension
                )
            sound_files_list.extend(extracted_sound_files)
        sound_files_list = [file for file in set(sound_files_list) if file!=None]
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(sound_files_list)} files matching {self.target_extension}")
        return True


from src.models import asr

class AsrTask(Task):
    """Apply Automatic Speech Recognition to audio files
    """

    def __init__(self, config, input, output, name_diff):
        super().__init__(config, input, output, name_diff)
        self.target_files = output
        #self.infer_text_classify_only = False       #TODO:separate into another Task???

    def run(self):
        unprocessed_files = self.get_next_run_files()
        if len(unprocessed_files)>0:
            #process by batch
            for idx, batch in enumerate( utils.get_next_batch_from_list(unprocessed_files, self.config['BATCH_COUNT']) ):
                batch_files = asr.run_workflow(
                    config=self.config,
                    sound_files=batch, 
                    intermediate_save_dir=self.target_files.directory,
                    infer_text_classify_only=False
                    )
                self.config['LOGGER'].info(f"end model workflow, batch-index: {idx} with {len(batch_files)} files")
        return True
    

#from src.models.classification import classifier
from src.models.classification import TextClassifier
import time
import json

class TextClassificationTask(Task):
    """Apply text classification to documents
    """

    def __init__(self, config, input, output, name_diff):
        super().__init__(config, input, output, name_diff)
        self.target_files = output

    def run(self):
        TextClassifier.config(self.config)
        intermediate_save_dir=self.target_files.directory
        unprocessed_files = self.get_next_run_files()
        if len(unprocessed_files)>0:
            #process by batch
            for idx, batches in enumerate( utils.get_next_batch_from_list(unprocessed_files, self.config['BATCH_COUNT']) ):
                '''
                batch_files = asr.run_workflow(
                    config=self.config,
                    sound_files=batch, 
                    intermediate_save_dir=self.target_files.directory,
                    infer_text_classify_only=False
                    )
                self.config['LOGGER'].info(f"end model workflow, batch-index: {idx} with {len(batch_files)} files")

                '''
                #run classification models on each: chunk,item
                dialogues = []
                for idx, batch in enumerate(batches):
                    with open(batch, 'r') as f_in:
                        dialogue = json.load(f_in)
                    #dialogues[idx]['classifier'] = []
                    dialogue['classifier'] = []
                    for chunk in dialogue['chunks']:
                        results = TextClassifier.run(chunk)
                        for result in results:
                            if result != None:
                                dialogue['classifier'].append(result)
                            else:
                                dialogue['classifier'].append({})
                    dialogue['time_textmdl'] = time.time() - self.config['START_TIME']
                    dialogues.append(dialogue)
                    self.config['LOGGER'].info(f'text-classification processing for file {idx} - {dialogue["file_name"]}')
                
        #save
        from src.io import export

        save_json_paths = []
        if intermediate_save_dir:
            for idx, dialogue in enumerate(dialogues):
                save_path = Path(intermediate_save_dir) / f'{dialogue["file_name"]}.json'
                try:
                    with open(save_path, 'w') as f:
                        json.dump(dialogue, f)
                    save_json_paths.append( str(save_path) )
                    self.config['LOGGER'].info(f'saved intermediate file {idx} - {save_path}')
                except Exception as e:
                    print(e)
                #TODO:   dialogues.extend(processed_dialogues)   #combine records of previously processed dialogues

        return save_json_paths





        return True


class ExportAsrToVdiWorkspaceTask(Task):
    """Export files to a VDI Workspace file."""

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_folder = output.directory

    def run(self):
        #load schema
        workspace_filepath = self.config['WORKING_DIR'] / 'workspace_schema_v0.2.1.json'
        if workspace_filepath.is_file():
            self.config['WORKSPACE_SCHEMA'] = File(workspace_filepath, 'schema').load_file(return_content=True)
            self.config['LOGGER'].info(f"workspace schema loaded")
        else:
            self.config['LOGGER'].info(f"run prepare() to load workspace schema")
            sys.exit()

        #export by batch
        processed_files = self.get_next_run_files()
        cnt = 0
        for idx, batch in enumerate( utils.get_next_batch_from_list(processed_files, self.config['BATCH_COUNT']) ):
            self.config['LOGGER'].info("begin export")
            batch_span = f'{cnt+idx}-{len(batch)}'
            dt = datetime.datetime.now().isoformat().split('T')[0].replace('-','')
            export_filepath = self.target_folder / f'VDI_ApplicationStateData_v0.2.1_{dt}_{batch_span}.gz'    #v0.2.1_YYYYMMDD_0-100.gz
            dialogues = [File(file, 'json').load_file(return_content=True)
                         for file in batch
                         ]
            check = export.export_dialogues_to_output(
                schema=self.config['WORKSPACE_SCHEMA'], 
                dialogues=dialogues, 
                filepath=export_filepath, 
                output_type='vdi_workspace'
                )
            cnt = len(batch)
            self.config['LOGGER'].info(f"Data processed for batch-{idx+1}: {check}")
        return True


from .Files import File
from src.modules.enterodoc.url import UrlFactory, UniformResourceLocator
from .web.crawler import Crawler, empty_scenario

import copy


class ImportAndValidateUrlsTask(Task):
    """Import initial root URL list and validate they exist."""

    def run(self):
        URL = UrlFactory()
        crawler = Crawler(
                scenario=empty_scenario,
                logger=self.config['LOGGER'],
                exporter=None
            )
        input_files = self.get_next_run_files()
        if len(input_files) == 1:
            input_file = input_files[0]
            urls = File(filepath=input_file, type='yaml').load_file(return_content=True)
            for key, item in urls.items():
                item['given_urls'].insert(0, item['root_url'])
                url_list = [URL.build(url) for url in item['given_urls'] if URL.build(url) != None]
                new_scenario = copy.deepcopy(empty_scenario)
                new_scenario.urls = url_list
                crawler.add_scenario(new_scenario)
                valid_urls = crawler.check_urls_are_valid(url_list)
                valid_urls_str = [url.__repr__() for url in valid_urls]
                item['_valid_urls'] = valid_urls_str
                self.config['LOGGER'].info(f"validated {len(valid_urls)} urls and saved to location {key} ")
            outfile = self.output_files.directory / 'urls.json'
            out_file = File(filepath=outfile, type='json')
            out_file.content = urls
            check = out_file.export_to_file()
            self.config['LOGGER'].info(f"end ingest file of {len(input_files)} files")
        else:
            self.config['LOGGER'].info(f"urls previously validated")
            check=True
        return check


class CrawlUrlsTask(Task):
    """Collect branch-and-leaf URLs from initial roots."""

    def run(self):
        """
        #input
        input_files = [file for file in self.input_files.get_files()]
        if len(input_files) > 1:
            self.config['LOGGER'].error(f'ERROR: there should be 1 file, but there are {len(input_files)}')
        input_file = input_files[0]
        """
        URL = UrlFactory()
        input_files = self.get_next_run_files()
        if len(input_files) == 1:
            input_file = input_files[0]
            urls = File(filepath=input_file, type='txt').load_file(return_content=True)
            url_list = [URL.build(url) for url in urls]
            #process
            results = {}
            for Url in url_list:
                #UrlCrawl = crawler(Url, self.config['LOGGER'])
                empty_scenario.url = Url
                empty_scenario.depth = 0
                UrlCrawl = Crawler(
                    scenario=empty_scenario,
                    logger=self.config['LOGGER'],
                    exporter=''
                    )
                result_urls = UrlCrawl.generate_href_chain()
                #results.append(result_urls)
                k = str( list(result_urls.keys())[0] )
                v = [str(item) for item in result_urls[Url]]
                results[k] = v
            #output
            outfile = self.output_files.directory / 'urls.json'
            out_file = File(filepath=outfile, type='json')
            out_file.content = results
            check = out_file.export_to_file()
            self.config['LOGGER'].info(f"end ingest file of {len(input_files)} files")
            self.config['LOGGER'].info(f"validated {len(results)} urls and saved to location {self.output_files.directory.__str__()} ")
        else:
            self.config['LOGGER'].info(f"urls previously validated")
            check=True
        return check



from src.modules.enterodoc.config import ConfigObj
from src.modules.enterodoc.document_factory import DocumentFactory
from src.modules.enterodoc.record import DocumentRecord

class ConvertUrlDocToPdf(Task):
    """Download URL document to memory then convert to PDF Format."""

    def run(self):
        #input
        """
        input_files = [file for file in self.input_files.get_files()]
        if len(input_files) > 1:
            self.config['LOGGER'].error(f'ERROR: there should be 1 file, but there are {len(input_files)}')
        input_file = input_files[0]
        """
        URL = UrlFactory()
        input_files = self.get_next_run_files()
        if len(input_files) == 1:
            input_file = input_files[0]
            root_urls = File(filepath=input_file, type='json').load_file(return_content=True)
            #process
            ConfigObj.set_logger(self.config['LOGGER'])
            Doc = DocumentFactory(ConfigObj)
            results = []
            for root, urls in root_urls.items():
                for url_str in urls:
                    url = URL.build(url_str)
                    url.run_data_requests_()
                    doc = Doc.build(url)
                    docrec = DocumentRecord()
                    try:
                        check = docrec.validate_object_attrs(doc)
                    except Exception as e:
                        self.config['LOGGER'].info(f"DocumentRecord attribute validation error with url: {url_str}")
                        self.config['LOGGER'].info(e)
                        continue

                    #format
                    #TODO:use pickle to keep all data
                    #TODO:make DocumenRecord able to be pickled, ref: https://stackoverflow.com/questions/2049849/why-cant-i-pickle-this-object
                    doc.record['filepath'] = str(doc.record['filepath'])
                    doc.record['file_str'] = [x for x in doc.record['file_str']]    #convert bytes to uInt8Array for json
                    doc.record['date'] = str(doc.record['date'])
                    del doc.record['file_document']
                    #end changes
                    results.append(doc.record)
        
            #output
            outfile = self.output_files.directory / 'urls.json'
            out_file = File(filepath=outfile, type='json')
            out_file.content = results
            check = out_file.export_to_file()
            self.config['LOGGER'].info(f"end ingest file of {len(input_files)} files")
            self.config['LOGGER'].info(f"validated {len(results)} urls and saved to location {self.output_files.directory.__str__()} ")
        else:
            self.config['LOGGER'].info(f"urls previously validated")
            check=True
        return check


class ApplyModelsTask(Task):
    """Apply models to each doc record text."""

    def run(self):
        input_files = self.get_next_run_files()
        if len(input_files) == 1:
            input_file = input_files[0]
            docs = File(filepath=input_file, type='json').load_file(return_content=True)
            results = []
            for doc in docs:
                results.append(doc)
            #output
            outfile = self.output_files.directory / 'urls.json'
            out_file = File(filepath=outfile, type='json')
            out_file.content = results
            check = out_file.export_to_file()
            self.config['LOGGER'].info(f"end ingest file of {len(input_files)} files")
            self.config['LOGGER'].info(f"validated {len(results)} urls and saved to location {self.output_files.directory.__str__()} ")
        else:
            self.config['LOGGER'].info(f"urls previously validated")
            check=True
        return check
    

class ExportVdiWorkspaceTask(Task):
    """Export files to a VDI Workspace file."""

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_folder = output.directory

    def run(self):
        #load schema
        workspace_filepath = self.config['WORKING_DIR'] / 'workspace_schema_v0.2.1.json'
        if workspace_filepath.is_file():
            self.config['WORKSPACE_SCHEMA'] = File(workspace_filepath, 'schema').load_file(return_content=True)
            self.config['LOGGER'].info(f"workspace schema loaded")
        else:
            self.config['LOGGER'].info(f"run prepare() to load workspace schema")
            sys.exit()

        #export by batch
        processed_files = self.get_next_run_files()
        cnt = 0
        for idx, batch in enumerate( utils.get_next_batch_from_list(processed_files, self.config['BATCH_COUNT']) ):
            self.config['LOGGER'].info("begin export")
            batch_span = f'{cnt+idx}-{len(batch)}'
            dt = datetime.datetime.now().isoformat().split('T')[0].replace('-','')
            export_filepath = self.target_folder / f'VDI_ApplicationStateData_v0.2.1_{dt}_{batch_span}.gz'    #v0.2.1_YYYYMMDD_0-100.gz
            #dialogues
            if False:
                documents = [File(file, 'json').load_file(return_content=True)
                         for file in batch
                         ]
                check = export.export_dialogues_to_output(
                    schema=self.config['WORKSPACE_SCHEMA'], 
                    records=documents, 
                    filepath=export_filepath,
                    output_type='vdi_workspace'
                    )
            #documents
            if True:
                file = batch[0]
                documents = File(file, 'json').load_file(return_content=True)
                check = export.export_documents_to_vdiworkspace(
                    schema=self.config['WORKSPACE_SCHEMA'], 
                    records=documents, 
                    filepath=export_filepath
                    )
            cnt = len(batch)
            self.config['LOGGER'].info(f"Data processed for batch-{idx+1}: {check}")
        return True