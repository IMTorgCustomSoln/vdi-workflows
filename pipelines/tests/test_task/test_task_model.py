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
   t_dir = Path(t_dir)
   intermediate_dir = t_dir / 'intermediate'
   intermediate_files = Files(
      name='intermediate',
      directory=intermediate_dir,
      extension_patterns=['.pickle']
      )
   output_dir = t_dir / 'output'
   output_files = Files(
      name='output',
      directory=output_dir,
      extension_patterns=['.pickle']
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

   export_files = [item for item in Path(t_dir).glob('**/*') if item.is_file()]
   assert len(export_files) == 8
   assert export_files[7].stem == 'test_file3'     #4records in 1 export file
  #batches of files
  #assert True == True