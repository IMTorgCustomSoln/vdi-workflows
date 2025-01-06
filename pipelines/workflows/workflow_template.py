#!/usr/bin/env python3
"""
WorkflowTemplate


UseCase-1: use this as a template for building-out new workflows
* load .txt files
* classify and create intermediary .json records
* output as table .csv
* basic reporting
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Workflow import Workflow
from src.Files import Files

from src.TaskTransform import ApplyTextModelsTask
from src.TaskImport import ImportFromLocalFileTask
from src.TaskExport import ExportToLocalTableTask
"""TODO
from src.Report import (
    TaskStatusReport,
    MapBatchFilesReport,
    ProcessTimeAnalysisReport
)
"""
from src.models import prepare_models
from src.io import load
#TODO: from tests.estimate_processing_time import ProcessTimeQrModel

from config._constants import (
    logging_dir,
    logger
)

from pathlib import Path
import json
import time
import sys


class WorkflowTemplate(Workflow):
    """..."""

    def __init__(self):
        CONFIG = {}
        try:
            #user input
            CONFIG['INPUT_DIR'] = Path('./tests/test_wf_template/data/')
            CONFIG['TRAINING_DATA_DIR'] = Path('./src/data/template/') 
            CONFIG['WORKING_DIR'] = Path('./tests/test_wf_template/tmp/')
            CONFIG['OUTPUT_DIRS'] = [Path('./tests/test_wf_template/tmp/OUTPUT')]

            #system input
            CONFIG['START_TIME'] = None
            CONFIG['LOGGER'] = logger
            CONFIG['BATCH_RECORD_COUNT'] = 50
            CONFIG['WORKSPACE_SCHEMA'] = None
            #CONFIG['REGEX_INPUT_FILES_NAMES'] = '_Calls_'
            self.config = CONFIG

            #working dirs
            CONFIG['WORKING_DIR'].mkdir(parents=True, exist_ok=True)
            DIR_VALIDATED = CONFIG['WORKING_DIR'] / '1_VALIDATED'
            #DIR_CONVERTED = CONFIG['WORKING_DIR'] / '2_CONVERTED'
            DIR_MODELS_APPLIED = CONFIG['WORKING_DIR'] / '2_MODELS_APPLIED'
            DIR_OUTPUT = CONFIG['WORKING_DIR'] / '3_OUTPUT'
            DIR_ARCHIVE = CONFIG['WORKING_DIR'] / 'ARCHIVE'
            CONFIG['DIR_ARCHIVE'] = DIR_ARCHIVE

            #files
            input_files = Files(
                name='input',
                directory=CONFIG['INPUT_DIR'],
                extension_patterns=['.txt', '.md']
                )
            validated_files = Files(
                name='validated',
                directory=DIR_VALIDATED,
                extension_patterns=['.json']
                )
            models_applied_files = Files(
                name='models_applied',
                directory=DIR_MODELS_APPLIED,
                extension_patterns=['.json']
                )
            output_files = Files(
                name='output',
                directory=DIR_OUTPUT,
                extension_patterns=['.csv']
                )
            self.files = {
                'input_files': input_files,
                'validated_files': validated_files,
                'models_applied_files': models_applied_files,
                'output_files': output_files
            }
            #tasks
            validate_task = ImportFromLocalFileTask(
                config=CONFIG,
                input=input_files,
                output=validated_files
            )
            apply_models_task = ApplyTextModelsTask(
                config=CONFIG,
                input=validated_files,
                output=models_applied_files
            )
            
            output_task = ExportToLocalTableTask(
                config=CONFIG,
                input=models_applied_files,
                output=output_files
            )
            tasks = [
                validate_task,
                apply_models_task,
                output_task
                ]
            self.tasks = tasks
        except Exception as e:
            print(e)
            sys.exit()
        

    def prepare_models(self):
        """Prepare by loading train,test data and refine models"""
        self.config['LOGGER'].info("Begin prepare_models")
        check_prepare_keywords = prepare_models.validate_key_terms(self.config)
        check_prepare_model = prepare_models.finetune_classification_model(self.config)
        if not (check_prepare_keywords | check_prepare_model): 
            self.config['LOGGER'].info(f"keywords or models failed to prepare")
            return False
        self.config['LOGGER'].info("End prepare_models")
        return True

    def prepare_workspace(self):
        """Prepare workspace with output schema and file paths"""
        #prepare schema
        filepath = Path('./tests/data/VDI_ApplicationStateData_v0.2.1.gz')
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
        self.config['LOGGER'].info(f"end process, execution took: {round(time.time() - self.config['START_TIME'], 3)}sec")
        return True

    '''
    def report_task_status(self):
        """
        TODO:
        * typical size of files
        * outlier files that are very large
        * place code in a separate file
        
        TaskStatusReport(
            files=self.files,
            config=self.config
        ).run()"""
        return True
    
    def report_map_batch_to_files(self):
        """Create .csv of files in each batch output
        
        MapBatchFilesReport(
            files=self.files,
            config=self.config
        ).run()"""
        return True
    
    def report_process_time_analysis(self):
        """Analyze processing times of completed files
        
        MapBatchFilesReport(
            files=self.files,
            config=self.config
        ).run()
        ProcessTimeAnalysisReport(
            files=self.files,
            config=self.config
        ).run()"""
        return True
    '''
        


workflow_template = WorkflowTemplate()