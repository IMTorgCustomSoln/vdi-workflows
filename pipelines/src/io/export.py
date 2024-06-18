#!/usr/bin/env python3
"""
Export functions

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.modules.styled_text.styled_text import StyledText
from src.io import utils

import os
from pathlib import Path
import json


def format_dialogue_timestamps(dialogue):
    """Transform output and convert to PDF"""
    def format_round(num):
        return round(float(num), 1) if num!=None else None
    
    results = []
    lines = dialogue['chunks']
    timestamps = [(format_round(line['timestamp'][0]), format_round(line['timestamp'][1])) for line in lines]
    stamps = [[-1,-1] for idx in range(len(timestamps))]
    trigger = False
    try:
        for idx in range(len(timestamps)):
            if idx==0:
                stamps[0] = timestamps[0]
            elif (timestamps[idx][0] == timestamps[idx-1][1]) and trigger==False:
                stamps[idx]= timestamps[idx]
            elif trigger==True:
                accum = stamps[idx-1][1] + timestamps[idx][1]
                stamps[idx] = [ (stamps[idx-1])[1], format_round(accum) ]
            else:
                accum = stamps[idx-1][1] + timestamps[idx][1]
                stamps[idx] = [ timestamps[idx-1][1], format_round(accum) ]
                trigger = True
    except Exception as e:
        print(e)
        #TODO:Whisper did not predict an ending timestamp, which can happen if audio is cut off in the middle of a word.  Also make sure WhisperTimeStampLogitsProcessor was used during generation.
        return None

    for idx in range(len(timestamps)):
        item = f'{stamps[idx]}  -  {lines[idx]["text"]} \n'
        results.append(item)
    return results


def output_to_pdf(dialogue, results, filename=None, output_type='file'):
    """Transform output and convert to PDF."""
    #print( ('').join(results) )
    if type(results)==list and len(results) > 0:
        str_intermediate_results = ('').join(results)
        str_results = ('').join( [i if ord(i) < 128 else ' ' for i in str_intermediate_results] )
    else:
        str_results = '[0.0, 1.0] -  <This message failed to transcribe correctly>. \n'
    pdf = text_to_pdf(str_results)
    if output_type=='file':
        pdf.output(filename, 'F')
        return True
    elif output_type=='str':
        result = {
            'dialogue': dialogue,
            'object':pdf, 
            'byte_string': pdf.output(dest='S').encode('latin-1')
            }
        return result
    elif output_type=='object':
        return pdf
    else:
        raise TypeError(f'argument "output_type" must be: "file" or "str"; parameter provided: {output_type}')


import textwrap
from fpdf import FPDF

def text_to_pdf(text):
    """Convert text to PDF object.
    
    ref: https://stackoverflow.com/questions/10112244/convert-plain-text-to-pdf-in-python
    """
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    if '\n' in text:
        splitted = text.split('\n')
    else:
        splitted = text

    for line in splitted:
        try:
            lines = textwrap.wrap(line, width_text)
        except Exception as e:
            print(e)
            lines = [line[:int(width_text)]]

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    return pdf





import pandas as pd
from pypdf import PdfReader

from collections.abc import Iterable
import io
import gzip
import copy
from datetime import datetime


def export_to_output(schema, dialogues, filepath, output_type='vdi_workspace'):
    """...
    
    TODO: separate excel from vdi_workspace
    """
    workspace_schema = copy.deepcopy(schema)
    documents_schema = workspace_schema['documentsIndex']['documents']

    if output_type == 'excel':
        documents = []
        for dialogue in dialogues:
            dialogue['formatted'] = format_dialogue_timestamps(dialogue)
            pdf = {'dialogue': dialogue}
            document_record = {}        #copy.deepcopy(documents_schema)
            document_record['filename_original'] = pdf['dialogue']['file_name']
            document_record['account'] = pdf['dialogue']['file_name'].split('_')[0]
            document_record['date'] = pdf['dialogue']['file_name'].split('_')[1]
            #scores = [model['pred'] for model in pdf['dialogue']['classifier'] if 'pred' in model.keys()]
            #document_record['score'] = max(scores) if len(scores)>0 else 0.0
            check_iter = isinstance(pdf['dialogue']['formatted'], Iterable)
            if check_iter:
                text = '  '.join(pdf['dialogue']['formatted'])   #\015
                label = []
                highest_pred_target = {'pred': 0.0, 'target': None, 'search': None}
                for model in pdf['dialogue']['classifier']:
                    if 'pred' in model.keys():
                        index = text.find(model['target'])
                        item = [index, len(model['target']), True]
                        label.append(item)
                        if highest_pred_target['pred'] < model['pred']:
                            highest_pred_target['pred'] = model['pred']
                            highest_pred_target['target'] = model['target']
                            highest_pred_target['search'] = model['search']
            else:
                text = pdf['dialogue']['formatted']
                label = []
            document_record['search'] = highest_pred_target['search']
            document_record['target'] = highest_pred_target['target']
            document_record['pred'] = highest_pred_target['pred']
            document_record['data'] = text                              #TODO:note - excel has limit of ~32,767 characters
            document_record['label'] = label
            document_record['filepath'] = pdf['dialogue']['file_path']
            documents.append(document_record)
        raw = pd.DataFrame(documents)
        raw.rename(columns={
            'filename_original': 'File_Name', 
            'account': 'Account', 
            'date': 'Call_Date', 
            'pred': 'Score', 
            'target': 'Text_Hit', 
            'search': 'Model_Type',
            'data': 'data', 
            'label': 'label',
            'filepath': 'File_Path'
            }, inplace=True)
        df = raw.sort_values(by=['Account','Score'], ascending=False)
        #TODO:fix
        #if check_iter and len(text)>0:
        #    try:
        #        case_results = StyledText.df_to_xlsx(df=df, output_path=filepath, verbose=True)
        #    except Exception as e:
        #        print(e)
        #else:
        df.to_excel(filepath, index=False)
        return True

    elif output_type == 'vdi_workspace':
        #to string
        pdfs = []
        for dialogue in dialogues:
            dialogue['formatted'] = format_dialogue_timestamps(dialogue)
            pdf = output_to_pdf(
                dialogue=dialogue,
                results=dialogue['formatted'],
                output_type='str'
            )
            if pdf!=None:
                pdfs.append(pdf)
        #load documents
        documents = []
        for idx, pdf in enumerate(pdfs):
            document_record = copy.deepcopy(documents_schema)
            pdf_pages = {}
            with io.BytesIO(pdf['byte_string']) as open_pdf_file:
                reader = PdfReader(open_pdf_file)
                for page in range( len(reader.pages) ):
                    text = reader.pages[page].extract_text()
                    pdf_pages[page+1] = text
            #raw
            document_record['id'] = str(idx)
            document_record['body_chars'] = {idx+1: len(page) for idx, page in enumerate(pdf_pages.values())}                 #{1: 3958, 2: 3747, 3: 4156, 4: 4111,
            document_record['body_pages'] = pdf_pages                                                                           #{1: 'Weakly-Supervised Questions for Zero-Shot Relation…a- arXiv:2301.09640v1 [cs.CL] 21 Jan 2023<br><br>', 2: 'tive approach without using any gold question temp…et al., 2018) with unanswerable questions<br><br>', 3: 'by generating a special unknown token in the out- …ng training. These spurious questions can<br><b
            document_record['date_created'] = None
            #document_record['length_lines'] = None    #0
            #document_record['length_lines_array'] = None    #[26, 26, 7, 
            document_record['page_nos'] = pdf['object'].pages.__len__()
            document_record['length_lines'] = pdf['dialogue']['formatted'].__len__() if pdf['dialogue']['formatted']!=None else 0
            data_array = {idx: val for idx,val in enumerate(list( pdf['byte_string'] ))}        #new list of integers that are the ascii values of the byte string
            document_record['dataArray'] = data_array
            document_record['toc'] = []
            document_record['pp_toc'] = ''
            document_record['clean_body'] = ' '.join( list(pdf_pages.values()) )
            #file info
            record_path = Path(pdf['dialogue']['file_path'])
            document_record['file_extension'] = record_path.suffix
            document_record['file_size_mb'] = record_path.stat().st_size
            document_record['filename_original'] = record_path.name
            document_record['title'] = record_path.name
            document_record['filepath'] = str(record_path)
            document_record['filetype'] = 'audio'
            dt_group1 = record_path.stem.split('_')
            dt_group2 = record_path.stem.split('.')
            if len(dt_group1)>1:
                dt = dt_group1[1]
            elif len(dt_group2)>1:
                dt = dt_group2[3]
            else:
                raise Exception(f'neither dt_group format is acceptable to extract from name: {record_path.stem}')
            document_record['date'] = (datetime(int(dt[0:4]), int(dt[4:6]), int(dt[6:8]) )).isoformat()
            document_record['reference_number'] = record_path.stem.split('_')[0]
            if 'classifier' in pdf['dialogue'].keys():
                highest_pred_target = max(pdf['dialogue']['classifier'], key=lambda model: model['pred'] if 'pred' in model.keys() else 0 )
                hit_count = len([model for model in pdf['dialogue']['classifier'] if model!={}])
                models = pdf['dialogue']['classifier']
            else:
                highest_pred_target = {}
                hit_count = None
                models = None
            document_record['sort_key'] = highest_pred_target['pred'] if 'pred' in highest_pred_target.keys() else 0.0
            document_record['hit_count'] = hit_count
            document_record['time_asr'] = pdf['dialogue']['time_asr']
            document_record['time_textmdl'] = pdf['dialogue']['time_textmdl']

            document_record['snippets'] = []
            document_record['summary'] = "TODO:summary"
            document_record['_showDetails'] = False
            document_record['_activeDetailsTab'] = 0
            document_record['models'] = models
            documents.append(document_record)
        #validate
        workspace_schema['documentsIndex']['documents'] = documents
        #export
        #filepath_export_wksp_gzip = Path('./tests/results/VDI_ApplicationStateData_vTEST.gz')
        filepath_export_wksp_gzip = filepath
        with gzip.open(filepath_export_wksp_gzip, 'wb') as f_out:
            f_out.write( bytes(json.dumps(workspace_schema, default=utils.date_handler), encoding='utf8') )    #TODO: datetime handlder, ref: https://stackoverflow.com/questions/455580/json-datetime-between-python-and-javascript
        return True