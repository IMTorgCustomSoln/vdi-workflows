#!/usr/bin/env python3
"""
Test Task templates and TaskComponent children.

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.TaskExport import ExportToLocalTableTask
from src.Files import Files

from pathlib import Path
import os
import tempfile
import shutil

from config._constants import (
    logging_dir,
    logger
)


def test_ExportToLocalTableTask():
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory=input_dir,
    extension_patterns=['.pickle']          #TODO:populate pickle files in data/ for testing - they're empty now!
    )
  #individual files
  config = {
    'LOGGER': logger
    }
  with tempfile.TemporaryDirectory() as t_dir:
   output_files = Files(
      name='output',
      directory=t_dir,
      extension_patterns=['.csv']
      )
   name_diff = ''
   tmp_task = ExportToLocalTableTask(
     config, 
     input_files, 
     output_files     #TODO:True / False
     )
   check = tmp_task.run()
   export_file = [item for item in Path(t_dir).glob('**/*') if item.is_file()]
   assert len(export_file) == 1
   assert export_file[0].stem == 'export-4'     #4records in 1 export file
  #batches of files
  '''TODO
  config = {
    'LOGGER': logger,
    'BATCH_COUNT': 1
    }
  with tempfile.TemporaryDirectory() as t_dir:
   output_files = Files(
    name='output',
    directory=t_dir,
    extension_patterns=['.csv']
    )
   name_diff = ''
   tmp_task = ExportToLocalTableTask(
    config, 
    input_files, 
    output_files
    )
   check = tmp_task.run()
   export_file = [item for item in Path(t_dir).glob('**/*') if item.is_file()]
   assert len(export_file) == 4                 #1 record in each of 4 export files
   '''