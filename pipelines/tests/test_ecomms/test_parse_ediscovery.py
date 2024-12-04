#!/usr/bin/env python3
"""
Test ediscovery workflow
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
from contextlib import contextmanager



#setup
@contextmanager
def setup_basic_layout():
    """Typical simple layout for testing."""
    cwdir = Path('tests/test_ecomms/data_ediscovery/basic_layout')
    home_dirpath = cwdir / 'VOL01'
    dat_file = 'load_file_01.dat'
    dat_filepath = cwdir / dat_file
    try:
        yield [cwdir, home_dirpath, dat_file, dat_filepath]
    finally:
        pass
    
@contextmanager
def setup_extended_layout():
    """Extended layout for large amount of data."""
    cwdir = Path('tests/test_ecomms/data_ediscovery/extended_layout')
    home_dirpath = cwdir / '12345_VOL01' / 'VOL01'
    dat_file = 'load_file_01.dat'
    dat_filepath = home_dirpath / 'DATA' /  dat_file
    try:
        yield [cwdir, home_dirpath, dat_file, dat_filepath]
    finally:
        pass


def test_get_file_lines():
    with setup_basic_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
        dat_lines = get_file_lines(dat_filepath)
        assert len(dat_lines) == 5
    with setup_extended_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
        dat_lines = get_file_lines(dat_filepath)
        assert len(dat_lines) == 5

def test_get_table_rows_from_lines():
    with setup_basic_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
        dat_lines = get_file_lines(dat_filepath)
        rows = get_table_rows_from_lines(dat_lines)
        assert len(rows) == 4
    with setup_extended_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
        dat_lines = get_file_lines(dat_filepath)
        rows = get_table_rows_from_lines(dat_lines)
        assert len(rows) == 4

def test_copy_dat_file_with_fixed_format():
    with setup_basic_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
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
    with setup_basic_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
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
    with setup_basic_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
        rows = get_table_rows_from_dat_file(dat_filepath)
        assert len(rows) == 4
    with setup_extended_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
        rows = get_table_rows_from_dat_file(dat_filepath)
        assert len(rows) == 4

def test_get_nested_dirs_files_lines():
    with setup_basic_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
        txt_dir = home_dirpath / 'TEXT'
        txt_dicts = get_nested_dirs_files_lines(txt_dir)
        assert len(txt_dicts.keys()) == 10
    with setup_extended_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
        txt_dir = home_dirpath / 'TEXT'
        txt_dicts = get_nested_dirs_files_lines(txt_dir)
        assert len(txt_dicts.keys()) == 4
    
def test_validate_txt_files():
    with setup_basic_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
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
                home_dirpath,
                linkfields={'TextLink':'Extracted Text', 'NativeLink':'FILE_PATH'}
                )
        assert checks == [True, True]
    with setup_extended_layout() as env:
        cwdir, home_dirpath, dat_file, dat_filepath = env
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
                home_dirpath,
                linkfields={'TextLink':'Extracted Text', 'NativeLink':'FILE_PATH'}
                )
        assert checks == [True, True]