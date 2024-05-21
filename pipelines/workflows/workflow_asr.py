#!/usr/bin/env python3
"""
WorkflowASR
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Workflow import Workflow
from src.Files import Files
from src.Task import (
    UnzipTask,
    AsrWithTextClassificationTask,
    ExportVdiWorkspaceTask
)
from src.Report import TaskStatusReport
from src.models import prepare_models
from src.io import load

from config._constants import (
    logging_dir,
    logger
)

from pathlib import Path
import json
import time
import sys


class WorkflowASR(Workflow):
    """..."""

    def __init__(self):
        CONFIG = {}
        try:
            CONFIG['INPUT_DIR'] = Path('./tests/data/samples/')
            CONFIG['WORKING_DIR'] = Path('./tests/tmp/')
            CONFIG['START_TIME'] = None
            CONFIG['LOGGER'] = logger
            CONFIG['BATCH_COUNT'] = 25
            CONFIG['WORKSPACE_SCHEMA'] = None
            #CONFIG['REGEX_INPUT_FILES_NAMES'] = '_Calls_'
            self.config = CONFIG
            #working dirs
            CONFIG['WORKING_DIR'].mkdir(parents=True, exist_ok=True)
            DIR_UNZIPPED = CONFIG['WORKING_DIR'] / 'UNZIPPED'
            DIR_PROCESSED = CONFIG['WORKING_DIR'] / 'PROCESSED'
            DIR_OUTPUT = CONFIG['WORKING_DIR'] / 'OUTPUT'
            #files
            input_files = Files(
                name='input',
                directory=CONFIG['INPUT_DIR'],
                extension_patterns=['.zip']
                )
            unzip_files = Files(
                name='unzip',
                directory=DIR_UNZIPPED,
                extension_patterns=['.wav','.mp3']
                )
            processed_files = Files(
                name='processed',
                directory=DIR_PROCESSED,
                extension_patterns=['.json']
                )
            output_files = Files(
                name='output',
                directory=DIR_OUTPUT,
                extension_patterns=['.gz']
                )
            self.files = {
                'input_files': input_files,
                'unzip_files': unzip_files,
                'processed_files': processed_files,
                'output_files': output_files
            }
            #tasks
            unzip_task = UnzipTask(
                config=CONFIG,
                input=input_files,
                output=unzip_files
                )
            models_task = AsrWithTextClassificationTask(
                config=CONFIG,
                input=unzip_files,
                output=processed_files,
                name_diff='.json'
            )
            output_task = ExportVdiWorkspaceTask(
                config=CONFIG,
                input=processed_files,
                output=output_files
            )
            tasks = [
                unzip_task, 
                models_task,
                output_task
                ]
            self.tasks = tasks
        except Exception as e:
            print(e)
            sys.exit()
        

    def prepare_models(self):
        """Prepare by loading train,test data and refine models"""
        self.config['LOGGER'].info("Begin prepare_models")
        check_prepare = prepare_models.finetune()
        if not check_prepare: 
            self.config['LOGGER'].info(f"models failed to prepare")
            exit()
        self.config['LOGGER'].info("End prepare_models")
        return True

    def prepare_workspace(self):
        """Prepare workspace with output schema and file paths"""
        #prepare schema
        filepath = Path('./tests/data/meta') / 'VDI_ApplicationStateData_v0.2.1.gz'
        if filepath.is_file():
            workspace_schema = load.get_schema_from_workspace(filepath)
        self.config['WORKSPACE_SCHEMA'] = workspace_schema
        schema = self.config['WORKING_DIR'] / 'workspace_schema_v0.2.1.json'
        with open(schema, 'w') as f:
            json.dump(workspace_schema, f)
        #TODO:validate file paths
        return True
    
    def run(self):
        """Run the workflow of tasks"""
        self.config['LOGGER'].info('begin process')
        self.config['START_TIME'] = time.time()
        for task in self.tasks:
            task.run()
        self.config['LOGGER'].info(f"End process, execution took: {round(time.time() - self.config['START_TIME'], 3)}sec")

    def report(self):
        """
        TODO:
        * typical size of files
        * outlier files that are very large
        * place code in a separate file
        """
        TaskStatusReport(
            files=self.files,
            config=self.config
        ).run()
        return True

        


workflow_asr = WorkflowASR()