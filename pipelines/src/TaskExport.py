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
import json
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
            'doc': None
        }

    def convert_pipeline_record_to_table_record(self, pipeline_record):
        records = []
        for doc in pipeline_record.collected_docs:
            temp = copy.deepcopy(self._table_record_template)
            temp['record_id'] = pipeline_record.id
            temp['source_type'] = pipeline_record.source_type
            temp['root_source'] = pipeline_record.root_source
            temp['added_sources'] = ', '.join(pipeline_record.added_sources)
            #TODO:add attributes as k,v to the dict: `.get_display_attr()`
            #these attributes should be selected for a flat file, as opposed to those needed for the VdiWorkspace, such as pdf array
            temp['doc'] = doc
            records.append(temp)
        return records

    def run(self):
        table_records = []
        for file in self.get_next_run_file():
            check = file.load_file(return_content=False)
            record = file.get_content()
            table_row_records = self.convert_pipeline_record_to_table_record(record)
            table_records.extend(table_row_records)
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
    





class ExportToVdiWorkspaceTask(Task):
    """Export pipeline records to VDI Workspace file."""

    def __init__(self, config, input, output, vdi_schema):
        super().__init__(config, input, output)
        self._vdi_schema = File(vdi_schema, filetype='json').load_file(return_content=True)
    
    #def convert_pipeline_record_to_table_record(self, pipeline_record):
    #    pass

    def run(self):
        workspace_schema = copy.deepcopy(self._vdi_schema)
        workspace_documents = []
        for file in self.get_next_run_file():
            check = file.load_file(return_content=False)
            record = file.get_content()
            workspace_document = xform_record_to_workspace_documents(self._vdi_schema, record)
            workspace_documents.extend(workspace_document)
        workspace_schema['documentsIndex']['documents'] = workspace_documents
        filepath_export_wksp_gzip = self.output_files.directory / 'VDI_ApplicationStateData_vTEST.gz'
        #filepath_export_wksp_gzip = filepath
        with gzip.open(filepath_export_wksp_gzip, 'wb') as f_out:
            f_out.write( bytes(json.dumps(workspace_schema, default=utils.date_handler), encoding='utf8') )    #TODO: datetime handlder, ref: https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
        return True



import gzip
import json

#def export_documents_to_vdiworkspace(schema, records):
def xform_record_to_workspace_documents(schema, record):
    workspace_schema = copy.deepcopy(schema)
    documents_schema = workspace_schema['documentsIndex']['documents']
    #doc_filenames = record[list(record.keys())[0]]['docs']
    documents = []
    for idx, rec in enumerate(record.collected_docs):
        document_record = copy.deepcopy(documents_schema)

        #for body_pages, but is it necessary???
        #byte_string = bytes(rec['file_str'].encode('utf-8'))
        '''
        pdf_pages = {}
        with io.BytesIO(byte_string) as open_pdf_file:
            reader = PdfReader(open_pdf_file)
            for page in range( len(reader.pages) ):
                text = reader.pages[page].extract_text()
                pdf_pages[page+1] = text
        '''

        #raw
        document_record['id'] = str(idx)
        document_record['body_chars'] = None    #{idx+1: len(page) for idx, page in enumerate(pdf_pages.values())}                 #{1: 3958, 2: 3747, 3: 4156, 4: 4111,
        document_record['body_pages'] = None           #{1: 'Weakly-Supervised Questions for Zero-Shot Relation…a- arXiv:2301.09640v1 [cs.CL] 21 Jan 2023<br><br>', 2: 'tive approach without using any gold question temp…et al., 2018) with unanswerable questions<br><br>', 3: 'by generating a special unknown token in the out- …ng training. These spurious questions can<br><b
        document_record['date_created'] = rec['date']
        #document_record['length_lines'] = None    #0
        #document_record['length_lines_array'] = None    #[26, 26, 7, 
        document_record['page_nos'] = rec['page_nos']
        document_record['length_lines'] = rec['length_lines']

        #data_array = {idx: val for idx,val in enumerate(list( byte_string ))} 
        #data_array = [x for x in byte_string]
        #document_record['dataArray'] = data_array
        document_record['dataArray'] = rec['file_str']
        document_record['toc'] = rec['toc']
        document_record['pp_toc'] = rec['pp_toc']
        document_record['body_pages'] = rec['body_pages']
        #document_record['clean_body'] = rec['clean_body']     #''.join(rec['clean_body'])          #NOTE:created during workspace import
        #file info
        #record_path = Path(rec['dialogue']['file_path'])
        document_record['file_extension'] = rec['file_extension']
        document_record['file_size_mb'] = rec['file_size_mb']
        document_record['filename_original'] = rec['filename_original']
        document_record['title'] = rec['title']
        document_record['filepath'] = rec['filepath']
        document_record['filetype'] = rec['filetype']
        document_record['author'] = rec['author']
        document_record['subject'] = rec['subject']
        #models
        if 'classifier' in rec.keys():#TODO:move 'classifier to ???
            highest_pred_target = max(rec['dialogue']['classifier'], key=lambda model: model['pred'] if 'pred' in model.keys() else 0 )
            hit_count = len([model for model in rec['dialogue']['classifier'] if model!={}])
            models = rec['dialogue']['classifier']
            time_asr = rec['time_asr']
            time_textmdl = rec['time_textmdl']
        else:
            highest_pred_target = {}
            hit_count = None
            models = None
            time_asr = None
            time_textmdl = None
        document_record['sort_key'] = highest_pred_target['pred'] if 'pred' in highest_pred_target.keys() else 0.0
        document_record['hit_count'] = hit_count
        document_record['time_asr'] = time_asr
        document_record['time_textmdl'] = time_textmdl
        #display
        document_record['snippets'] = []
        document_record['summary'] = "TODO:summary"
        document_record['_showDetails'] = False
        document_record['_activeDetailsTab'] = 0
        document_record['models'] = models
        documents.append(document_record)
    return documents