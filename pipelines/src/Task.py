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
    
    def get_next_run_files(self, method='same'):
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
            input_names = set(self.input_files.get_files(filetype=Type))
            processed_names = set([file.replace(self.name_diff,'') for file in self.output_files.get_files(filetype=Type)])
            remainder_names = list( input_names.difference(processed_names) )
            if len(remainder_names)>0 and Type == 'name_only':
                remainder_paths = [file for file in self.input_files.get_files() 
                                   if utils.remove_all_extensions_from_filename(file.stem) in remainder_names    #TODO:possible error for workflow_site_scrape
                                   ]
            else:
                remainder_paths = []
            return remainder_paths
        
        elif method == 'update':      #TODO:improve this idea
            Type = 'name_only'
            input_names = set(self.input_files.get_files(filetype=Type))
            processed_names = set([file.replace(self.name_diff,'') for file in self.output_files.get_files(filetype=Type)])
            if len(processed_names) >= len(input_names):
                remainder_paths = []
            else:
                remainder_paths = list( self.input_files.get_files() )
            return remainder_paths

    def run(self):
        """Run processing steps on input files"""
        pass


class ImportFromLocalFileTask(Task):
    """Simple import of local files."""
    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_folder = output.directory
        self.target_extension=['.txt','.md']

    def run(self):
        file_records = []
        intermediate_save_dir=self.target_folder
        for file in self.get_next_run_files():
            with open(file, 'r') as f:
                lines = f.readlines()
            content = ' '.join(lines)
            simulated_chunks = []
            for idx,line in enumerate(lines):
                simulated_chunks.append( {
                    'idx': idx,
                    'text': line
                    })
            file_record = {
                'file_name': file.name,
                'content': content,
                'chunks': simulated_chunks
            }
            file_records.append(file_record)
        file_records = [file for file in file_records if file!=None]
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(file_records)} files matching {self.target_extension}")
        
        save_json_paths = []
        if intermediate_save_dir:
            for idx, file_record in enumerate(file_records):
                save_path = Path(intermediate_save_dir) / f'{file_record["file_name"]}.json'
                try:
                    with open(save_path, 'w') as f:
                        json.dump(file_record, f)
                    save_json_paths.append( str(save_path) )
                    self.config['LOGGER'].info(f'saved intermediate file {idx} - {save_path}')
                except Exception as e:
                    print(e)
        self.config['LOGGER'].info(f"end intermediate file save location at {intermediate_save_dir.resolve().__str__()} with {len(save_json_paths)} files matching {self.target_extension}")
        return True


class ExportToLocalTableTask(Task):
    """Simple export to local .csv table."""
    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_folder = output.directory

    def run(self):
        filename = 'export'
        unprocessed_files = self.get_next_run_files()
        if len(unprocessed_files)>0:
            #process by batch of files
            if 'BATCH_COUNT' in list(self.config.keys()):
                idx = 0
                for bidx, batch in enumerate( utils.get_next_batch_from_list(unprocessed_files, self.config['BATCH_COUNT']) ):
                    records = []
                    for fidx, file in enumerate( batch ):
                        record_content = File(filepath=file, filetype='json').load_file(return_content=True)
                        records.append(record_content)
                        self.config['LOGGER'].info(f'text-classification processing for file {idx} - {file.stem}')
                        idx += 1
                    df = pd.DataFrame(records)
                    df.to_csv(self.target_folder / f'{filename}-{bidx}.csv')
            #process by file
            else:
                records = []
                for fidx, file in enumerate( unprocessed_files ):
                    record_content = File(filepath=file, filetype='json').load_file(return_content=True)
                    records.append(record_content)
                    self.config['LOGGER'].info(f'text-classification processing for file {fidx} - {file.stem}')
                df = pd.DataFrame(records)
                df.to_csv(self.target_folder / f'{filename}-{fidx+1}.csv')
        return True


from src.models.classification import TextClassifier
import time
import json

class ApplyTextModelsTask(Task):
    """Apply text models (keyterms, classification, etc.) to documents in most simple scenario.
    """

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_files = output

    def run(self):
        TextClassifier.config(self.config)
        intermediate_save_dir=self.target_files.directory
        unprocessed_files = self.get_next_run_files()
        all_save_files = []
        if len(unprocessed_files)>0:
            #process by batch
            for idx, batch in enumerate( utils.get_next_batch_from_list(unprocessed_files, self.config['BATCH_COUNT']) ):
                #run classification models on each: chunk,item
                records = []
                for idx, file in enumerate(batch):
                    record = File(filepath=file, filetype='json').load_file(return_content=True)
                    record['classifier'] = []
                    for chunk in record['chunks']:
                        results = TextClassifier.run(chunk)
                        for result in results:
                            if result != None:
                                record['classifier'].append(result)
                            else:
                                record['classifier'].append({})
                    record['time_textmdl'] = time.time() - self.config['START_TIME']
                    records.append(record)
                    self.config['LOGGER'].info(f'text-classification processing for file {idx} - {record["file_name"]}')
       
                #save
                from src.io import export

                save_json_paths = []
                if intermediate_save_dir:
                    for idx, record in enumerate(records):
                        save_path = Path(intermediate_save_dir) / f'{record["file_name"]}.json'
                        out_file = File(filepath=save_path, filetype='json')
                        out_file.content = record
                        check = out_file.export_to_file()
                        if check:
                            save_json_paths.append( str(save_path) )
                            self.config['LOGGER'].info(f'saved intermediate file {idx} - {save_path}')
                        else:
                            self.config['LOGGER'].info(f'failed to save intermediate file {idx} - {save_path}')
                all_save_files.extend(save_json_paths)

        self.config['LOGGER'].info(f'completed text-classification processing for file {len(all_save_files)}')
        return True