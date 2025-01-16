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

DocFactory = DocumentFactory()

class ImportFromLocalFileTask(Task):
    """Simple import of local files."""
    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_extension.extend(['.txt','.md'])

    def run(self):
        for file in self.get_next_run_file():
            check = file.load_file(return_content=False)
            record = self.create_pipeline_record_from_file(file, source_type='single_file')
            doc = DocFactory.build(file.filepath)
            doc_record = doc.get_record()
            record.collected_docs.append(doc_record)
            self.pipeline_record_ids.append(record.id)
            filepath = self.export_pipeline_record_to_file(record)
            self.config['LOGGER'].info(f"exported processed file to: {filepath}")
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(self.pipeline_record_ids)} files matching {self.target_extension}")
        return True

class ImportBatchDocsFromLocalFileTask(Task):
    """Simple import of local files where one record contains multiple documents."""
    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_extension.extend(['.rec'])

    def run(self):
        for file in self.get_next_run_file():
            check = file.load_file(return_content=False)
            record = self.create_pipeline_record_from_file(file, source_type='multiple_files')
            content = file.get_content()
            doc_filenames = content[list(content.keys())[0]]['docs']
            for doc_filename in doc_filenames:
                doc_filepath = file.filepath.parent / doc_filename
                doc = DocFactory.build(doc_filepath)
                check = doc.run_extraction_pipeline()
                doc_record = doc.get_record()
                record.collected_docs.append(doc_record)
            #record.populate_presentation_doc()
            self.pipeline_record_ids.append(record.id)
            filepath = self.export_pipeline_record_to_file(record)
            self.config['LOGGER'].info(f"exported processed file to: {filepath}")
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(self.pipeline_record_ids)} files matching {self.target_extension}")
        return True
    




from .Files import File
from src.modules.parse_emails.parse_emails import EmailParser
from src.modules.parse_ediscovery.loadfile import (
    collect_workspace_files,
    copy_dat_file_with_fixed_format,
    get_table_rows_from_dat_file,
)
from src.modules.parse_orgchart.orgchart import OrgChartParser

class ImportValidateCombineEcommsTask(Task):
    """Import variety of e-communication files and validate quality.
    
    ecomms types:
    * email - .eml, .msg, .pst, .mbox, ...
    * chat - Teams, Bloomburg: .json
    * legal - .dat, .opt, .txt, ...
    * org chart - .csv
    """

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_extension=['.mdat','.txt','.eml','.msg']

    def run(self):
        #load orgchart
        file_path_csv = self.config['INPUT_DIR'] / 'org1.csv'
        orgchart_parser = OrgChartParser(file_path=file_path_csv)
        check = orgchart_parser.validate()
        #load and collect msg records
        dfdats = pd.DataFrame()
        file_collection = collect_workspace_files(self.config['INPUT_DIR'])
        for idx, volume_key in enumerate(file_collection.keys()):
            if file_collection[volume_key]['mdat']:
                dat_file = file_collection[volume_key]['mdat']
                dfdat = get_table_rows_from_dat_file(
                    dat_file, 
                    type='df', 
                    sep='\x14', 
                    #rename_fields={}
                    )
                dfdat['text'] = None
                contents = []
                #TODO:there is too much presentation logic here
                for idx, row in enumerate(dfdat.to_dict('records')):
                    txt = row['textLink']
                    txt_file = self.config['INPUT_DIR'] / volume_key / Path(txt)
                    if txt_file.suffix in self.target_extension:
                        with open(txt_file, 'r') as f:
                            content = f.read()
                            #content = txt + '\n' + f.read()
                            formatted_content = f'''{txt}\n
FROM: {row['from']}\n
TO: {row['to']}\n
SUBJECT: {row['subject']}\n
{content}\n
'''
                            contents.append(formatted_content )
                    else:
                        contents.append(None)
                dfdat['text'] = contents
                dfdat['volume'] = volume_key
                dfdats = pd.concat([dfdats, dfdat])
            else:
                raise Exception
        #group into discussions ('subject')
        dfdats.reset_index(inplace=True)
        dfdats['Date Received'] = pd.to_datetime(dfdats['Date Received'])
        dfdats.sort_values(by=['subject','documentID','Date Received','from'], inplace=True, ascending=True)
        dfdats['Date Received'] = dfdats['Date Received'].astype(str)
        #cols=['subject','documentID','Date Received','from']
        #dfdats[['documentID','groupID','Date Received','from','to','subject','text']]

        #group by subject to create dialogues
        # collect msgs into one pipeline_record
        for subject in list(dfdats['subject'].unique()):
            dfsubj = dfdats[dfdats['subject']==subject].reset_index()
            filename = f"filegrp-subj_{dfsubj['documentID'][0]}_{dfsubj.shape[0]}"
            ftype = self.output_files.extension_patterns[0].replace('.','')
            output_file = self.output_files.directory / f"{filename}.{ftype}"

            #output to pipeline_record
            outfile = File(output_file, ftype)
            outfile.load_file(return_content=False)
            record = self.create_pipeline_record_from_file(outfile, source_type='multiple_files')
            dialogue_rec = dfsubj.to_dict('records')
            record.added_sources = dialogue_rec
            body_pages = {idx:page['text'] for idx,page in enumerate(dialogue_rec)}
            dialogue_doc = {
                'filetype': '.txt',
                'date': dialogue_rec[0]['Date Received'].split(' ')[0],
                'filepath': dialogue_rec[0]['textLink'],
                'body': dialogue_rec[0]['text'],
                'body_pages': body_pages,
                #'page_nos': max([int(pg) for pg in list(body_pages.keys())]),
                'clean_body': dialogue_rec[0]['text'].replace('\n','')
            }
            record.collected_docs = [dialogue_doc]
            #TODO: add to document Extractor()
            #email_parser = EmailParser(file_path=eml, max_depth=2)
            #results = email_parser.parse()
            #result = outfile.export_to_file()
            filepath = self.export_pipeline_record_to_file(record)
            self.config['LOGGER'].info(f"exported processed file to: {filepath}")
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(self.pipeline_record_ids)} of {dfdats.shape[0]} files matching {self.target_extension}")
        return True
