#!/usr/bin/env python3
"""
Test Task templates and TaskComponent children.

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.TaskImport import ImportFromLocalFileTask,ImportBatchDocsFromLocalFileTask 
from src.TaskTransform import CreatePresentationDocument, ApplyTextModelsTask
from src.Files import Files
from src.Task import PipelineRecord

from pathlib import Path
import tempfile
import pickle
import time

from config._constants import (
    logging_dir,
    logger
)




def test_multiple_files_CreatePresentationDocument():
  #setup
  config = {
    'LOGGER': logger,
    'TRAINING_DATA_DIR': Path('./src/data/template/'),
    'START_TIME': time.time()
    }
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory=input_dir,
    extension_patterns=['.yml']
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
   import_task = ImportBatchDocsFromLocalFileTask(
     config, 
     input_files, 
     intermediate_files
     )
   xform_task = CreatePresentationDocument(
     config, 
     intermediate_files, 
     output_files
     )
   check = import_task.run()
   check = xform_task.run()

   export_files = [item for item in output_dir.glob('**/*') if item.is_file()]
   assert len(export_files) == 2
   assert export_files[0].stem == 'test_file1'     #4records in 1 export file
   with open(export_files[0], "rb") as pipeline_record_file:
    pipeline_record = pickle.load(pipeline_record_file)
  assert type(pipeline_record) == PipelineRecord


def test_single_file_ApplyTextModelsTask():
  #setup
  config = {
    'LOGGER': logger,
    'TRAINING_DATA_DIR': Path('./src/data/template/'),
    'START_TIME': time.time()
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
   xform_dir = t_dir / 'xform'
   xform_files = Files(
      name='intermediate',
      directory=xform_dir,
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
   xform_task = CreatePresentationDocument(
     config, 
     intermediate_files, 
     xform_files
     )
   model_task = ApplyTextModelsTask(
     config, 
     xform_files, 
     output_files
     )
   check = import_task.run()
   check = xform_task.run()
   check = model_task.run()

   export_files = [item for item in output_dir.glob('**/*') if item.is_file()]
   assert len(export_files) == 4
   assert export_files[0].stem == 'test_file1'     #4records in 1 export file
   with open(export_files[0], "rb") as pipeline_record_file:
    pipeline_record = pickle.load(pipeline_record_file)
  assert type(pipeline_record) == PipelineRecord


def test_multiple_files_ApplyTextModelsTask():
  #setup
  config = {
    'LOGGER': logger,
    'TRAINING_DATA_DIR': Path('./src/data/template/'),
    'START_TIME': time.time()
    }
  input_dir = Path(__file__).parent / 'data'
  input_files = Files(
    name='input',
    directory=input_dir,
    extension_patterns=['.yml']
    )
  with tempfile.TemporaryDirectory() as t_dir:
   t_dir = Path(t_dir)
   intermediate_dir = t_dir / 'intermediate'
   intermediate_files = Files(
      name='intermediate',
      directory=intermediate_dir,
      extension_patterns=['.pickle']
      )
   xform_dir = t_dir / 'xform'
   xform_files = Files(
      name='intermediate',
      directory=xform_dir,
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
   import_task = ImportBatchDocsFromLocalFileTask(
     config, 
     input_files, 
     intermediate_files
     )
   xform_task = CreatePresentationDocument(
     config, 
     intermediate_files, 
     xform_files
     )
   model_task = ApplyTextModelsTask(
     config, 
     xform_files, 
     output_files
     )
   check = import_task.run()
   check = xform_task.run()
   check = model_task.run()

   export_files = [item for item in output_dir.glob('**/*') if item.is_file()]
   assert len(export_files) == 2
   assert export_files[0].stem == 'test_file1'     #4records in 1 export file
   with open(export_files[0], "rb") as pipeline_record_file:
    pipeline_record = pickle.load(pipeline_record_file)
  assert type(pipeline_record) == PipelineRecord