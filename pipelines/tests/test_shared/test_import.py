#!/usr/bin/env python3
"""
Test import
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.Files import File

import tempfile
from pathlib import Path
import json
import yaml

def test_json():
    input = {
        "array": [1, 2, 3],
        "boolean": True,
        "color": "gold",
        "null": None,
        "number": 123,
        "object": {"a": "b", "c": "d"},
        "string": "Hello World",
    }
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as fp:
        json.dump(input, fp)
        fp.flush()
        input_file = File(filepath=fp.name, filetype="json")
        output_dict = input_file.load_file(return_content=True)
    assert output_dict == input

def test_yaml():
  input = {
        "array": [1, 2, 3],
        "boolean": True,
        "color": "gold",
        "null": None,
        "number": 123,
        "object": {"a": "b", "c": "d"},
        "string": "Hello World",
    }
  with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml") as fp:
    yaml.dump(input, fp)
    fp.flush()
    input_file = File(filepath=fp.name, filetype="yaml")
    output_dict = input_file.load_file(return_content=True)
    assert output_dict == input