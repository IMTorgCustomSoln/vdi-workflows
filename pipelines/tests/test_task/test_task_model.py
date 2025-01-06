#!/usr/bin/env python3
"""
Test Task templates and TaskComponent children.

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.TaskImport import ImportFromLocalFileTask
from src.TaskTransform import ApplyTextModelsTask
from src.Files import Files

from pathlib import Path
import tempfile
import shutil

from config._constants import (
    logging_dir,
    logger
)


def test_ApplyTextModelsTask():
  #setup
  config = {
    'LOGGER': logger,
    'TRAINING_DATA_DIR': Path('./src/data/template/')
    }
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory=input_dir,
    extension_patterns=['.txt']
    )
  with tempfile.TemporaryDirectory() as t_dir:
   intermediate_files = Files(
      name='intermediate',
      directory=t_dir,
      extension_patterns=['.pickle']
      )
   output_files = Files(
      name='output',
      directory=t_dir,
      extension_patterns=['.json']
      )
   name_diff = ''
   #implement
   import_task = ImportFromLocalFileTask(
     config, 
     input_files, 
     intermediate_files
     )
   xform_task = ApplyTextModelsTask(
     config, 
     intermediate_files, 
     output_files     #TODO:True / False
     )
   check = import_task.run()
   check = xform_task.run()

   export_file = [item for item in Path(t_dir).glob('**/*') if item.is_file()]
   assert len(export_file) == 1
   assert export_file[0].stem == 'export-4'     #4records in 1 export file
  #batches of files
  #assert True == True