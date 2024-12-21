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
from src.modules.enterodoc.entero_document.url import UrlFactory#, UrlEncoder

import pandas as pd

from pathlib import Path
import sys
import datetime



class PipelineRecordFactory():
    """TODO: maybe later create different subclasses from PipelineRecords."""
    def __init__(self):
        """..."""
        pass

    def create_from_id(self, id, source_type, root_source=None):
        if source_type not in ['single_file', 'single_url', 'multiple_files']:
            return None
        return PipelineRecord(id, source_type, root_source)
    #def create_from_record(self, record):
    #    pass


class PipelineRecord():
    """..."""
    def __init__(self, id, source_type=None, root_source=None):
        """..."""
        self.id = id
        self.source_type = source_type
        self.root_source = root_source
        self.added_sources = []
        self.collected_docs = []
        self.classifier = []
        
    def _populate_pdf_from_string(self):
        pass
    #def export_to_json(self):
    #    """TODO: this is too complicated because of the nested internal classes"""
    #    return True
    def export_to_vdi_workspace(self):
        """..."""
        return True
    def export_to_excel(self):
        """..."""
        return True



class Task:
    """..."""

    def __init__(self, config, input, output, name_diff=''):
        #standard inputs
        self.config = config
        self.input_files = None
        self.output_files = None
        #TODOif type(config) == Config:
        #    self.config = config
        if input.directory.is_dir():
            self.input_files = input
        else:
            raise Exception(f'input not found: {input}')
        if output.directory.is_dir():
            self.output_files = output
        else:
            raise Exception(f'output not found: {output}')
        self.name_diff = name_diff

        #standard data
        self.target_extension=[]
        self.factory = PipelineRecordFactory()
        self.pipeline_record_ids = []

    def run(self):
        """Run processing steps on input Files"""
        pass

    def create_pipeline_record_from_file(self, file):
        """Create PipelineRecords from File.
        Typically, this is only needed for initial file import - not intermediate files.
        """
        record = self.factory.create_from_id(
            id=file.filepath.stem, 
            source_type='single_file', 
            root_source=file.filepath
            )
        return record

    def get_next_run_file(self, method='same'):
        """Get the remaining files that should be provided to run()
        Each record is an file and they are processed, individually, as opposed
        to multiple records within a file.

        Typically:
        * get input files
        * get output files
        * get remainder files by comparing input to output

        TODO:add as function to Files.py and ensure appropriate attr: .name, .stem, etc.
        """
        if method == 'same':
            Type = 'name_only'
            input_names = set([file.filepath.name for file in self.input_files.get_files(filetype=Type)])
            #processed_names = set([file.replace(self.name_diff,'') for file in self.output_files.get_files(filetype=Type)])
            processed_names = set([file.filepath.name for file in self.output_files.get_files(filetype=Type)])
            remainder_names = list( input_names.difference(processed_names) )
            if len(remainder_names)>0 and Type == 'name_only':
                remainder_files = [file for file in self.input_files.get_files()
                                    if file.filepath.name in remainder_names
                                   #if utils.remove_all_extensions_from_filename(file.stem) in remainder_names    #TODO:possible error for workflow_site_scrape
                                   ]
            else:
                remainder_files = []
            return remainder_files
        """
        elif method == 'update':      #TODO:improve this idea
            Type = 'name_only'
            input_names = set(self.input_files.get_files(filetype=Type))
            processed_names = set([file.replace(self.name_diff,'') for file in self.output_files.get_files(filetype=Type)])
            if len(processed_names) >= len(input_names):
                remainder_paths = []
            else:
                remainder_paths = list( self.input_files.get_files() )
            return remainder_paths
        """
    
    def export_pipeline_record_to_file(self, record, type='pickle'):
        """...
        
        NOTE: only 'pickle' is possible because of complicated structure
        """
        #TODO: add self.name_diff in-case a name change is needed
        filename = record.id
        filepath = self.output_files.directory / f'{filename}.pickle'
        new_file = File(filepath, type)
        new_file.content = record
        check = new_file.export_to_file()
        return check