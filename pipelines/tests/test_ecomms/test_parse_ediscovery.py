#!/usr/bin/env python3
"""
Test ecomms workflow
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.modules.parse_ediscovery.loadfile import (
    validate_files, 
    copy_dat_file_with_fixed_format,
    get_table_rows_from_lines, 
    get_table_rows_from_dat_file, 
    get_file_lines, 
    get_nested_dirs_files_lines
)

import pandas as pd

from pathlib import Path
import os
import tempfile



#setup
cwdir = Path('tests/test_ecomms/data_ediscovery/basic_layout')

dat_file = 'load_file_01.dat'
dat_filepath = cwdir / dat_file

txt_dir = 'VOL01/TEXT/'
txt_dirpath = cwdir / txt_dir
img_dir = 'VOL01/IMAGES/'
img_dirpath = cwdir / img_dir
native_dir = 'VOL01/NATIVES/'
native_dirpath = cwdir / native_dir



def test_get_file_lines():
    dat_lines = get_file_lines(dat_filepath)
    assert len(dat_lines) == 5

def test_get_table_rows_from_lines():
    dat_lines = get_file_lines(dat_filepath)
    rows = get_table_rows_from_lines(dat_lines)
    assert len(rows)==4

def test_copy_dat_file_with_fixed_format():
    with tempfile.TemporaryDirectory() as t_dir:
        new_file = os.path.join (t_dir, 'new_file.dat')
        SEP = '\x14'
        check = copy_dat_file_with_fixed_format(
            bom_file = dat_filepath, 
            new_file = new_file, 
            separator_str='|', 
            remove_chars=[], 
            new_separator=SEP
            )
        df = pd.read_csv(new_file, sep=SEP)
        assert df.shape == (4, 23)
    assert check == True

def test_get_table_rows_from_dat_file():
    rows = get_table_rows_from_dat_file(dat_filepath)
    assert len(rows) == 4

def test_get_nested_dirs_files_lines():
    txt_dicts = get_nested_dirs_files_lines(txt_dirpath)
    assert len(txt_dicts.keys()) == 10
    
def test_validate_txt_files():
    with tempfile.TemporaryDirectory() as t_dir:
        new_file = os.path.join (t_dir, 'new_file.dat')
        SEP = '\x14'
        check = copy_dat_file_with_fixed_format(
            bom_file = dat_filepath, 
            new_file = new_file, 
            separator_str='|', 
            remove_chars=[], 
            new_separator=SEP
            )
        checks = validate_files(
            new_file, 
            txt_dirpath, 
            type='text', 
            linkfields={'TextLink':'Extracted Text'}
            )
    assert checks == [True]

def test_validate_native_files():
    with tempfile.TemporaryDirectory() as t_dir:
        new_file = os.path.join (t_dir, 'new_file.dat')
        SEP = '\x14'
        check = copy_dat_file_with_fixed_format(
            bom_file = dat_filepath, 
            new_file = new_file, 
            separator_str='|', 
            remove_chars=[], 
            new_separator=SEP
            )
        checks = validate_files(
            new_file, 
            native_dirpath, 
            type='native', 
            linkfields={'NativeLink':'FILE_PATH'}
            )
    assert checks == [True]