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
        chunks = split_str_into_chunks(doc['clean_body'][0], N)
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


"""TODO:check and remove
class ApplyTextModelsTask(Task):
    '''Apply text models (keyterms, classification, etc.) to documents in most simple scenario.
    '''

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_files = output

    def run(self):
        TextClassifier.config(self.config)
        intermediate_save_dir=self.target_files.directory
        unprocessed_files = self.get_next_run_file()
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
        
        return True
"""