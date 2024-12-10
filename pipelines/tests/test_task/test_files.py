#!/usr/bin/env python3
"""
Test File and Files classes.

"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.Files import File, Files

import tempfile
from pathlib import Path


def test_file():
    filepath = Path(__file__).parent / 'data'
    ftypes = ['txt','json']#,'pickle']
    for ftype in ftypes:
        with tempfile.TemporaryDirectory() as t_dir:
            #import existing file
            outpath = Path(t_dir)
            filename = f'test_file1.{ftype}'
            test_file = File(filepath / filename, ftype)
            file_content1 = test_file.load_file(return_content=True)
            file_content2 = test_file.get_content()
            assert file_content1 == file_content2 == test_file.content
            #export content to new file
            test_file.filepath = outpath / filename
            result = test_file.export_to_file()
            assert test_file.filepath.is_file() == result

def test_files(): 
    results = []
    filepath = Path(__file__).parent / 'data'
    ftypes = ['.txt','.json']
    for ftype in ftypes:
        name = 'test_name'
        directory = filepath
        extension_patterns = [ftype]
        test_files = Files(name, directory, extension_patterns)
        file_generator = test_files.get_files(filetype='full_path')
        lst_files_small_to_large = list(file_generator)
    assert len(lst_files_small_to_large) == 4