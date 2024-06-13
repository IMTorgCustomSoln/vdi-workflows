#!/usr/bin/env python3
"""
Task class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Files import File
from src.io import export

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
    
    def get_next_run_files(self):
        """Get the files that should be provided to run()
        Typically:
        * get input files
        * get output files
        * get remainder files by comparing input to output
        """
        input_names = set(self.input_files.get_files(type='name_only'))
        processed_names = set([file.replace(self.name_diff,'') for file in self.output_files.get_files(type='name_only')])
        remainder_names = list( input_names.difference(processed_names) )
        remainder_paths = [file for file in self.input_files.get_files() if file.name in remainder_names]
        return remainder_paths

    def run(self):
        """Run processing steps on input files"""
        pass


class ImportTask(Task):
    """..."""



class ExportTask(Task):
    """..."""





from src.io import utils

class UnzipTask(Task):
    """Decompress archive files in a folder"""

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_folder = output.directory
        self.target_extension=['.wav','.mp3']

    def run(self):
        sound_files_list = []
        for file in self.get_next_run_files():
            extracted_sound_files = utils.decompress_filepath_archives(
                filepath=file,
                extract_dir=self.target_folder,
                target_extension=self.target_extension
                )
            sound_files_list.extend(extracted_sound_files)
        sound_files_list = [file for file in set(sound_files_list) if file!=None]
        self.config['LOGGER'].info(f"end ingest file location from {self.input_files.directory.resolve().__str__()} with {len(sound_files_list)} files matching {self.target_extension}")
        return True


from src.models import asr

class AsrWithTextClassificationTask(Task):
    """Apply Automatic Speech Recognition and Text Classification to
    audio files"""

    def __init__(self, config, input, output, name_diff):
        super().__init__(config, input, output, name_diff)
        self.target_files = output
        self.infer_text_classify_only = False       #TODO:separate into another Task???

    def run(self):
        unprocessed_files = self.get_next_run_files()
        if len(unprocessed_files)>0:
            #process by batch
            for idx, batch in enumerate( utils.get_next_batch_from_list(unprocessed_files, self.config['BATCH_COUNT']) ):
                batch_files = asr.run_workflow(
                    config=self.config,
                    sound_files=batch, 
                    intermediate_save_dir=self.target_files.directory,
                    infer_text_classify_only=False
                    )
                self.config['LOGGER'].info(f"end model workflow, batch-index: {idx} with {len(batch_files)} files")
        return True


class ExportVdiWorkspaceTask(Task):
    """Export files to a VDI Workspace file."""

    def __init__(self, config, input, output):
        super().__init__(config, input, output)
        self.target_folder = output.directory

    def run(self):
        #load schema
        workspace_filepath = self.config['WORKING_DIR'] / 'workspace_schema_v0.2.1.json'
        if workspace_filepath.is_file():
            self.config['WORKSPACE_SCHEMA'] = File(workspace_filepath, 'schema').load_file(return_content=True)
            self.config['LOGGER'].info(f"workspace schema loaded")
        else:
            self.config['LOGGER'].info(f"run prepare() to load workspace schema")
            sys.exit()

        #export by batch
        processed_files = self.get_next_run_files()
        cnt = 0
        for idx, batch in enumerate( utils.get_next_batch_from_list(processed_files, self.config['BATCH_COUNT']) ):
            self.config['LOGGER'].info("begin export")
            batch_span = f'{cnt+idx}-{len(batch)}'
            dt = datetime.datetime.now().isoformat().split('T')[0].replace('-','')
            export_filepath = self.target_folder / f'VDI_ApplicationStateData_v0.2.1_{dt}_{batch_span}.gz'    #v0.2.1_YYYYMMDD_0-100.gz
            dialogues = [File(file, 'json').load_file(return_content=True)
                         for file in batch
                         ]
            check = export.export_to_output(
                schema=self.config['WORKSPACE_SCHEMA'], 
                dialogues=dialogues, 
                filepath=export_filepath, 
                output_type='vdi_workspace'
                )
            cnt = len(batch)
            self.config['LOGGER'].info(f"Data processed for batch-{idx+1}: {check}")
        return True
    

class ValidateUrlsTask(Task):
    """..."""

class CrawlUrlsTask(Task):
    """..."""

class DownloadlUrlsTask(Task):
    """..."""

class ConvertPdfsTask(Task):
    """..."""

class ApplyModelsTask(Task):
    """..."""