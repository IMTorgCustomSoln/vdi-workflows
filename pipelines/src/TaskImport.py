#!/usr/bin/env python3
"""
TaskImport classes

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

Doc = DocumentFactory()

class ImportFromLocalFileTask(Task):
    """Simple import of local files."""
    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        #self.target_folder = output.directory
        self.target_extension.extend(['.txt','.md'])

    def create_pipeline_record_from_file(self, file):
        record = self.factory.create_from_id(
            id=file.filepath.stem, 
            source_type='single_file', 
            root_source=file.filepath
            )
        doc = Doc.build(file.filepath)
        record.collected_docs.append(doc)
        return record

    def run(self):
        #intermediate_save_dir=self.target_folder => USE self.output_files.directory
        for file in self.get_next_run_file():
            check = file.load_file(return_content=False)
            record = self.create_pipeline_record_from_file(file)
            record.collected_docs
            self.pipeline_record_ids.append(record.id)
            self.export_pipeline_record_to_file(record)
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(self.pipeline_record_ids)} files matching {self.target_extension}")

        """
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
            self.file_records.append(file_record)
        self.file_records = [file for file in self.file_records if file!=None]
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(self.file_records)} files matching {self.target_extension}")
        save_json_paths = []
        if intermediate_save_dir:
            for idx, file_record in enumerate(self.file_records):
                save_path = Path(intermediate_save_dir) / f'{file_record["file_name"]}.json'
                try:
                    with open(save_path, 'w') as f:
                        json.dump(file_record, f)
                    save_json_paths.append( str(save_path) )
                    self.config['LOGGER'].info(f'saved intermediate file {idx} - {save_path}')
                except Exception as e:
                    print(e)
        self.config['LOGGER'].info(f"end intermediate file save location at {intermediate_save_dir.resolve().__str__()} with {len(save_json_paths)} files matching {self.target_extension}")
        """
        return True