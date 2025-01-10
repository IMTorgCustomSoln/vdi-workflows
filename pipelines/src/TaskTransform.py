#!/usr/bin/env python3
"""
TaskExport classes

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Task import Task
from src.models.classification import TextClassifier

import pandas as pd

import time
import copy



class CreatePresentationDocument(Task):
    """Create the presentation Document from multiple collected, added Documents.
    The `.presentation_doc` is used for final export.
    
    """

    def __init__(self, config, input, output):
        super().__init__(config, input, output)

    def run(self):
        for file in self.get_next_run_file():
            check = file.load_file(return_content=False)
            record = file.get_content()
            check = record.populate_presentation_doc()
            self.pipeline_record_ids.append(record.id)
            filepath = self.export_pipeline_record_to_file(record)
            self.config['LOGGER'].info(f"exported processed file to: {filepath}")
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(self.pipeline_record_ids)} files matching {self.target_extension}")
        return True



def split_str_into_chunks(str_item, N):
    """Split string into list of equal length chunks."""
    chunks = [{'text': str_item[i:i+N]} for i in range(0, len(str_item), N)]
    return chunks


class ApplyTextModelsTask(Task):
    """Apply text models (keyterms, classification, etc.) to documents in most 
    simple scenario.
    """

    def __init__(self, config, input, output):
        super().__init__(config, input, output)

    def apply_models(self, record):
        N = 500
        doc = copy.deepcopy(record.presentation_doc)
        models = []
        chunks = split_str_into_chunks(doc['clean_body'], N)
        for chunk in chunks:
            results = TextClassifier.run(chunk)
            for result in results:
                if result != None:
                    models.append(result)
                else:
                    models.append({})
        #TODO:fix time_asr
        doc['models'] = models
        doc['time_asr'] = 0
        doc['time_textmdl'] = time.time() - self.config['START_TIME']
        self.config['LOGGER'].info(f'text-classification processed for file {record.id} - {record.root_source}')
        return doc

    def run(self):
        TextClassifier.config(self.config)
        for file in self.get_next_run_file():
            check = file.load_file(return_content=False)
            record = file.get_content()
            new_presentation_doc = self.apply_models(record)
            record.presentation_doc = new_presentation_doc
            self.pipeline_record_ids.append(record.id)
            filepath = self.export_pipeline_record_to_file(record)
            if filepath:
                self.config['LOGGER'].info(f'saved intermediate file {record.id} - {filepath}')
            else:
                self.config['LOGGER'].info(f'failed to save intermediate file {record.id}')
        self.config['LOGGER'].info(f'completed text-classification processing for file {len(self.pipeline_record_ids)}')
        return True