#!/usr/bin/env python3
"""
Files class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from operator import itemgetter
import os
from pathlib import Path
import json
import gzip
import pickle
import yaml


class File:
    """...
    Manipulate an individual file based upon its format.

    Usage
    ```
    >>> test_file = File(filepath / filename, 'txt')
    >>> file_content = test_file.load_file(return_content=True)
    >>> test_file.filepath = outpath / filename
    >>> result = test_file.export_to_file()
    ```
    """
    types = ['txt','json','yaml','pickle','schema','workspace']#TODO:,'archive']

    def __init__(self, filepath, filetype):
        filepath = Path(filepath).resolve()
        if not filepath.is_file():
            with open(filepath, 'w') as f_out:
                f_out.write("")
        self.filepath = filepath
        if filetype in File.types:
            self.filetype = filetype
        else:
            raise TypeError
        self.content = None

    def load_file(self, return_content=False):
        """Import from file"""
        #support functions
        def import_text(filepath):
            try:
                with open(filepath, 'r') as f_in:
                    text_content = f_in.readlines()
            except Exception as e:
                print(e)
                text_content = None
            return text_content

        def import_json(filepath):
            try:
                with open(filepath, 'r') as f:
                    json_content = json.load(f)
            except Exception as e:
                print(e)
                json_content = None
            return json_content
        
        def import_yaml(filepath):
            try:
                with open(filepath, 'r') as f:
                    yaml_content = yaml.safe_load(f)
            except Exception as e:
                print(e)
                yaml_content = None
            return yaml_content
        
        def import_pickle(filepath):
            try:
                with open(filepath, 'rb') as f:
                    content = pickle.load(f)
            except Exception as e:
                print(e)
                content = None
            return content
            
        def import_workspace(filepath):
            try:
                with gzip.open(filepath, 'rb') as f:
                    workspace_json = json.load(f)
            except Exception as e:
                print(e)
                workspace_json = None
            return workspace_json
        
        options = {
            'txt-.txt': import_text,
            'text-.txt': import_text,
            'json-.json': import_json,
            'yaml-.yaml': import_yaml,
            'yaml-.yml': import_yaml,
            'pickle-.pickle': import_pickle,
            'schema-.json': import_json,
            'workspace-.gz': import_workspace
        }

        #workflow
        ext = self.filepath.suffix
        key = f'{self.filetype}-{ext}'
        self.content = options[key](self.filepath)
        if return_content:
            return self.get_content()
        else:
            return True

    def get_content(self):
        return self.content
    
    def export_to_file(self):
        """Export to file"""
        #support functions
        def export_text(filepath):
            with open(filepath, 'w') as f_out:
                if type(self.content)==list:
                    for item in self.content:
                        f_out.write(f"{item}\n")
            return True
        
        def export_json(filepath):
            with open(filepath, 'w') as f:
                json.dump(self.content, f)
            return True
        
        def export_pickle(filepath):
            with open(filepath, 'wb') as f:
                pickle.dump(self.content, f)
            return True
        
        '''TODO:complete    
        def import_workspace(filepath):
            with gzip.open(filepath, 'wb') as f:
                workspace_json = json.load(f)
            return workspace_json
        '''
        options = {
            'txt-.txt': export_text,
            'text-.txt': export_text,
            'json-.json': export_json,
            'pickle-.pickle': export_pickle,
            #'schema-.json': import_json,
            #'workspace-.gz': import_workspace
        }
        #workflow
        ext = self.filepath.suffix
        key = f'{self.filetype}-{ext}'
        check = options[key](self.filepath)
        return check


    
    



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

    def get_files(self, filetype='full_path'):
        """Return files from smallest to largest by size"""
        def get_full_path(file):
            return file
        def get_name_and_suffix(file):
            return file.name
        def get_name_without_suffix(file):
            return file.stem
        def get_name_only(file):
            return file.stem.split('.')[0]
        options = {
            'full_path': get_full_path,
            'name_and_suffix': get_name_and_suffix,
            'name_without_suffix': get_name_without_suffix,
            'name_only': get_name_only,
        }
        files = [{'file': file, 'size':file.stat().st_size} 
                 for file in self.directory.rglob('*')
                 ]
        files_ascending_size = sorted(files, key=itemgetter('size'))
        files_sorted = [file['file'] for file in files_ascending_size]
        for file in files_sorted:
            check1 = '__MACOSX' not in str(file)
            suffixes = [ext for ext in self.extension_patterns 
                      if ext==file.suffix
                      ]
            check2 = len(suffixes)==1
            if all([check1, check2]):
                if file.is_file():
                    result = options[filetype](file)
                    yield result
                else:
                    raise Exception(f'file {file} is not found')
            else:
                continue