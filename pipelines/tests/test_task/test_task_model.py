#!/usr/bin/env python3
"""
Test Task templates and TaskComponent children.

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.TaskTransform import ApplyTextModelsTask
from src.Files import Files

from pathlib import Path
import tempfile
import shutil


#support
class LoggerPlaceholder:
  def __init__(self):
    self.info = self.print_statement
    self.error = self.print_statement

  def print_statement(self, text):
    print(text)


def test_ApplyTextModelsTask():
   #TODO: this is not complete!!!
   assert True == True