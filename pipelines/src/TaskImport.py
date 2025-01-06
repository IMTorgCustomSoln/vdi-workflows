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
        self.target_extension.extend(['.txt','.md'])

    def run(self):
        for file in self.get_next_run_file():
            check = file.load_file(return_content=False)
            record = self.create_pipeline_record_from_file(file)
            doc = Doc.build(file.filepath)
            check = doc.run_extraction_pipeline()
            doc_record = doc.get_record()
            record.collected_docs.append(doc_record)
            self.pipeline_record_ids.append(record.id)
            self.export_pipeline_record_to_file(record)
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(self.pipeline_record_ids)} files matching {self.target_extension}")
        return True