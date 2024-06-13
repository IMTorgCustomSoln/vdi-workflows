#!/usr/bin/env python3
"""
Task class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Files import File
from src.io import export

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
        """Get the files that should be provided to run()
        Typically:
        * get input files
        * get output files
        * get remainder files by comparing input to output
        """
        input_names = set(self.input_files.get_files(type='name_only'))
        processed_names = set([file.replace(self.name_diff,'') for file in self.output_files.get_files(type='name_only')])
        remainder_names = list( input_names.difference(processed_names) )
        remainder_paths = [file for file in self.input_files.get_files() if file.name in remainder_names]
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

class AsrWithTextClassificationTask(Task):
    """Apply Automatic Speech Recognition and Text Classification to
    audio files"""

    def __init__(self, config, input, output, name_diff):
        super().__init__(config, input, output, name_diff)
        self.target_files = output
        self.infer_text_classify_only = False       #TODO:separate into another Task???

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
            dialogues = [File(file, 'json').load_file(return_content=True)
                         for file in batch
                         ]
            check = export.export_to_output(
                schema=self.config['WORKSPACE_SCHEMA'], 
                dialogues=dialogues, 
                filepath=export_filepath, 
                output_type='vdi_workspace'
                )
            cnt = len(batch)
            self.config['LOGGER'].info(f"Data processed for batch-{idx+1}: {check}")
        return True


from .Files import File
from web.url import UniformResourceLocator
from web.crawler import Crawler

class ValidateUrlsTask(Task):
    """..."""

    def run(self):
        input_files = [file for file in self.input_files.get_files()]
        if len(input_files) > 1:
            self.config['LOGGER'].error(f'ERROR: there should be 1 file, but there are {len(input_files)}')
        input_file = input_files[0]
        urls = File(filepath=input_file, type='txt').load_file(return_content=True)
        url_list = [UniformResourceLocator(url) for url in urls]
        ValidatedUrls = Crawler.check_urls_are_valid(url_list)
        
        out_file = File(filepath=self.output_files, type='txt')
        out_file.content = ValidatedUrls
        out_file.export_to_file()
        self.config['LOGGER'].info(f"end ingest file of {len(input_files)} files from location {self.input_files.resolve().__str__()} ")
        self.config['LOGGER'].info(f"validated {len(ValidatedUrls)} urls and saved to location {self.output_files.resolve().__str__()} ")
        return True


class CrawlUrlsTask(Task):
    """..."""

    def run(self):
        #input
        input_files = [file for file in self.input_files.get_files()]
        if len(input_files) > 1:
            self.config['LOGGER'].error(f'ERROR: there should be 1 file, but there are {len(input_files)}')
        input_file = input_files[0]
        urls = File(filepath=input_file, type='txt').load_file(return_content=True)
        url_list = [UniformResourceLocator(url) for url in urls]
        #process
        results = []
        for Url in url_list:
            UrlCrawl = Crawler(Url, self.config['LOGGER'])
            result_urls = UrlCrawl.generate_href_chain()
            results.append(result_urls)
        #output
        out_file = File(filepath=self.output_files, type='txt')
        out_file.content = results
        out_file.export_to_file()
        self.config['LOGGER'].info(f"end ingest file of {len(input_files)} files from location {self.input_files.resolve().__str__()} ")
        self.config['LOGGER'].info(f"validated {len(results)} urls and saved to location {self.output_files.resolve().__str__()} ")
        return True


class ConvertUrlDocToPdf(Task):
    """Download URL document to memory then convert to PDF Format."""


#TODO REMOVE
class DownloadlUrlsTask(Task):
    """..."""

#TODO REMOVE
class ConvertPdfsTask(Task):
    """..."""

class ApplyModelsTask(Task):
    """..."""