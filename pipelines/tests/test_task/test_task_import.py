#!/usr/bin/env python3
"""
Test Task templates and TaskComponent children.

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.Task import ImportFromLocalFileTask
from src.Files import Files

from pathlib import Path
import os
import tempfile
import shutil

from config._constants import (
    logging_dir,
    logger
)


def test_ImportFromLocalFileTask():
  config = {
    'LOGGER': logger
    }
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory=input_dir,
    extension_patterns=['.txt']
    )
  with tempfile.TemporaryDirectory() as t_dir:
   output_files = Files(
      name='output',
      directory=t_dir,
      extension_patterns=['.txt']
      )
   name_diff = ''
   tmp_task = ImportFromLocalFileTask(
     config, 
     input_files, 
     output_files
     )
   check = tmp_task.run()
   files1 = list(input_files.get_files())
   files2 = [item for item in Path(t_dir).glob('**/*') if item.is_file()]
   assert len(files1) == len(files2)