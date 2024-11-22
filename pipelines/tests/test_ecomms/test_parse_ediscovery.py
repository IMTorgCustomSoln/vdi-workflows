from pathlib import Path

from src.modules.parse_ediscovery.loadfile import validate_files, get_table_rows, get_file_lines, get_nested_dirs_files_lines


#setup
cwdir = 'tests/test_ecomms/data_ediscovery/'

dat_file = 'load_file_01.dat'
dat_filepath = Path(cwdir) / dat_file
with open(dat_filepath, 'r') as f:
    dat_lines = f.readlines()

txt_dir = 'VOL01/TEXT/'
txt_dirpath = Path(cwdir) / txt_dir
img_dir = 'VOL01/IMAGES/'
img_dirpath = Path(cwdir) / img_dir


def test_get_rows():
    rows = get_table_rows(dat_lines)
    assert len(rows)==4

def test_get_file_lines():
    dat_lines = get_file_lines(dat_filepath)
    assert len(dat_lines) == 5

def test_get_nested_dirs_files_lines():
    txt_dicts = get_nested_dirs_files_lines(txt_dirpath)
    assert len(txt_dicts.keys()) == 10
    
def test_validate_files():
    checks = validate_files(dat_filepath, txt_dirpath)
    assert checks == [True]