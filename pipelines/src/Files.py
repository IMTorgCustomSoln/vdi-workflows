#!/usr/bin/env python3
"""
Files class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


import os
from pathlib import Path
import json
import gzip


class File:
    """..."""
    types = ['json','schema','workspace']#TODO:,'archive']

    def __init__(self, filepath, type):
        filepath = Path(filepath).resolve()
        if filepath.is_file():
            self.filepath = filepath
        else:
            raise TypeError
        if type in File.types:
            self.type = type
        else:
            raise TypeError
        self.content = None

    def load_file(self, return_content=False):
        """..."""
        #support functions
        def import_json(filepath):
            with open(filepath, 'r') as f:
                json_content = json.load(f)
            return json_content
            
        def import_workspace(filepath):
            with gzip.open(filepath, 'rb') as f:
                workspace_json = json.load(f)
            return workspace_json
        
        options = {
            'json-.json': import_json,
            'schema-.json': import_json,
            'workspace-.gz': import_workspace
        }

        #workflow
        ext = self.filepath.suffix
        key = f'{self.type}-{ext}'
        self.content = options[key](self.filepath)
        if return_content:
            return self.get_content()
        else:
            return True

    def get_content(self):
        return self.content

    
    



class Files:
    """..."""

    def __init__(self, name, directory, extension_patterns):
        path = Path(directory)
        if Path(path).is_dir()==False:
            check = Path(path).mkdir()
            if check==False:
                raise ValueError(f'invalid directory path {directory}')
        self.name = name
        self.directory = path
        self.extension_patterns = extension_patterns

    def get_files(self, type='full_path'):
        def get_full_path(file):
            return file
        def get_name_only(file):
            return file.name
        options = {
            'full_path': get_full_path,
            'name_only': get_name_only
        }
        for file in self.directory.rglob('*'):
            check1 = '__MACOSX' not in str(file)
            suffixes = [ext for ext in self.extension_patterns 
                      if ext==file.suffix
                      ]
            check2 = len(suffixes)==1
            if all([check1, check2]):
                if file.is_file():
                    result = options[type](file)
                    yield result
                else:
                    raise Exception(f'file {file} is not found')
            else:
                continue