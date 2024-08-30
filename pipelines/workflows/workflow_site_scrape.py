#!/usr/bin/env python3
"""
WorkflowSiteScrape


UseCase-1: run across multiple banks, create workspace for each and document for each page/doc
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.Workflow import Workflow
from src.Files import Files

from src.Task import (
    ImportAndValidateUrlsTask,
    CrawlUrlsTask,
    ConvertUrlDocToPdf,
    ApplyModelsTask,
    ExportVdiWorkspaceTask
)
"""
from src.Report import (
    TaskStatusReport,
    MapBatchFilesReport,
    ProcessTimeAnalysisReport
)
"""
from src.models import prepare_models
from src.io import load
#from tests.estimate_processing_time import ProcessTimeQrModel

from config._constants import (
    logging_dir,
    logger
)

from pathlib import Path
import json
import time
import sys


class WorkflowSiteScrape(Workflow):
    """..."""

    def __init__(self):
        CONFIG = {}
        try:
            #user input
            CONFIG['INPUT_DIR'] = Path('./tests/test_site_scrape/data/samples/')
            CONFIG['WORKING_DIR'] = Path('./tests/test_site_scrape/tmp/')
            CONFIG['OUTPUT_DIRS'] = [Path('./tests/test_site_scrape/tmp/OUTPUT')]

            #system input
            CONFIG['START_TIME'] = None
            CONFIG['LOGGER'] = logger
            CONFIG['BATCH_COUNT'] = 50
            CONFIG['WORKSPACE_SCHEMA'] = None
            #CONFIG['REGEX_INPUT_FILES_NAMES'] = '_Calls_'
            self.config = CONFIG
            #working dirs
            CONFIG['WORKING_DIR'].mkdir(parents=True, exist_ok=True)
            DIR_VALIDATED = CONFIG['WORKING_DIR'] / '1_VALIDATED'
            DIR_CRAWLED = CONFIG['WORKING_DIR'] / '2_CRAWLED'
            DIR_CONVERTED = CONFIG['WORKING_DIR'] / '3_CONVERTED'
            DIR_MODELS_APPLIED = CONFIG['WORKING_DIR'] / '4_MODELS_APPLIED'
            DIR_OUTPUT = CONFIG['WORKING_DIR'] / '5_OUTPUT'

            DIR_ARCHIVE = CONFIG['WORKING_DIR'] / 'ARCHIVE'
            CONFIG['DIR_ARCHIVE'] = DIR_ARCHIVE
            #files
            input_files = Files(
                name='input',
                directory=CONFIG['INPUT_DIR'],
                extension_patterns=['.yaml']
                )
            validated_files = Files(
                name='validated',
                directory=DIR_VALIDATED,
                extension_patterns=['.json']
                )
            crawled_files = Files(
                name='crawled',
                directory=DIR_CRAWLED,
                extension_patterns=['.json','.pickle']
                )
            converted_files = Files(
                name='converted',
                directory=DIR_CONVERTED,
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
                extension_patterns=['.gz']
                )
            self.files = {
                'input_files': input_files,
                'validated_files': validated_files,
                'crawled_files': crawled_files,
                'converted_files': converted_files,
                'models_applied_files': models_applied_files,
                'output_files': output_files
            }
            #tasks
            validate_task = ImportAndValidateUrlsTask(
                config=CONFIG,
                input=input_files,
                output=validated_files
            )
            crawl_task = CrawlUrlsTask(
                config=CONFIG,
                input=validated_files,
                output=crawled_files
            )
            convert_task = ConvertUrlDocToPdf(
                config=CONFIG,
                input=crawled_files,
                output=converted_files
            )
            apply_models_task = ApplyModelsTask(
                config=CONFIG,
                input=converted_files,
                output=models_applied_files
            )
            output_task = ExportVdiWorkspaceTask(
                config=CONFIG,
                input=models_applied_files,
                output=output_files
            )
            tasks = [
                validate_task,
                crawl_task,
                convert_task,
                apply_models_task,
                output_task
                ]
            self.tasks = tasks
        except Exception as e:
            print(e)
            sys.exit()
        

    def prepare_models(self):
        """Prepare by loading train,test data and refine models
        self.config['LOGGER'].info("Begin prepare_models")
        check_prepare = prepare_models.finetune()
        if not check_prepare: 
            self.config['LOGGER'].info(f"models failed to prepare")
            exit()
        self.config['LOGGER'].info("End prepare_models")"""
        return True

    def prepare_workspace(self):
        """Prepare workspace with output schema and file paths"""
        #prepare schema
        filepath = Path('./tests/test_site_scrape/data/meta') / 'VDI_ApplicationStateData_v0.2.1.gz'
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

        


workflow_site_scrape = WorkflowSiteScrape()