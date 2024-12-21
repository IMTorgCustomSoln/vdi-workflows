#!/usr/bin/env python3
"""
TaskExport classes

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Task import Task
from src.Files import File
from src.io import export
from src.io import utils
from src.modules.enterodoc.entero_document.url import UrlFactory#, UrlEncoder
from src.modules.enterodoc.entero_document.record import DocumentRecord
from src.modules.enterodoc.entero_document.document_factory import DocumentFactory
from src.modules.enterodoc.entero_document.document import Document

import pandas as pd

from pathlib import Path
import sys
import datetime
import copy


  
class ExportToLocalTableTask(Task):
    """Simple export to local .csv table by flattening pipeline records."""

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self._table_record_template = {
            'id': None,
            'source_type': None,
            'root_source': None,
            'added_sources': None,
            'doc': None,
        }

    def convert_pipeline_record_to_table_record(self, pipeline_record):
        temp = copy.deepcopy(self._table_record_template)
        for doc in pipeline_record.collected_docs:
            temp['record_id'] = pipeline_record.id
            temp['source_type'] = pipeline_record.source_type
            temp['root_source'] = pipeline_record.root_source
            temp['added_sources'] = ', '.join(pipeline_record.added_sources)
            #TODO:add attributes as k,v to the dict: `.get_display_attr()`
            #these attributes should be selected for a flat file, as opposed to those needed for the VdiWorkspace, such as pdf array
            temp['doc'] = doc
        return temp

    def run(self):
        table_records = []
        for file in self.get_next_run_file():
            check = file.load_file(return_content=False)
            record = file.get_content()
            table_record = self.convert_pipeline_record_to_table_record(record)
            table_records.append(table_record)
            self.pipeline_record_ids.append(record.id)
        df = pd.DataFrame(table_records)
        #TODO: enable return of DataFrame and make dump to file optional (if no output_files)
        filename = f'export-{self.pipeline_record_ids.__len__()}'
        output_filepath = self.output_files.directory / f'{filename}.csv'
        df.to_csv(output_filepath, index=False)
        self.config['LOGGER'].info(f"end table creation file {output_filepath.__str__()} with {len(self.pipeline_record_ids)} files")
        
        """
        #self.target_folder = output.directory
        ....
        filename = 'export'
        unprocessed_files = self.get_next_run_file()
        if len(unprocessed_files)>0:                        #TODO: is this necessary?
            #process by batch of files
            if 'BATCH_COUNT' in list(self.config.keys()):    #TODO: add batch processing
                idx = 0
                for bidx, batch in enumerate( utils.get_next_batch_from_list(unprocessed_files, self.config['BATCH_COUNT']) ):   #TODO:should be added to Task() base class???
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
        """
        return True