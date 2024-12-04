import pandas as pd

from typing import List
import click
from colorama import Fore, init as init_colorama
import chardet
import re
import csv
import pathlib
import json
import sys
import io

from pathlib import PureWindowsPath, PurePosixPath, Path
from itertools import chain

init_colorama()


ASCII_MATCH = re.compile("[a-zA-Z0-9]")


def validate_files(
        dat_filepath,
        link_dirpath,
        type,
        linkfields={'TextLink': 'TextLink', 'NativeLink': 'NativeLink'}
        ):
    """Validate ediscovery file package.


    * Do files referend to by .dat links exist?
    * Do the line counts match? ie: Documents = .dat; Pages = .opt
    * Does the number of rows in the DAT match the number of files loaded? ie: .dat == VOL /IMAGES, /NATIVES, /TEXT
    * Do all documents have text? (If not, image and OCR)
    * Do the Custodian counts appear correct?
    """
    #support
    def get_linux_path_from_windows(win_path):
        posix = str(PurePosixPath(PureWindowsPath(win_path)))
        return posix

    checks = []
    #load
    dat_rows = get_table_rows_from_dat_file(dat_filepath, '\x14')


    #check: Are txt files found in .dat records?
    if type=='text':
        txt_file_content = get_nested_dirs_files_lines(link_dirpath)
        extxt_files = set( [pathlib.Path(get_linux_path_from_windows(doc[linkfields['TextLink']])).stem for doc in dat_rows] )
        txt_paths = set( [pathlib.Path(txt).stem for txt in list(txt_file_content.keys())] )
        diff = extxt_files.difference(txt_paths)
        check_file_diff =  len(diff) == 0
        checks.append(check_file_diff)

    #check: Are native file paths found in .dat records?
    if type=='native':
        native_files = get_file_names(link_dirpath)
        dat_paths = [ str(pathlib.Path(get_linux_path_from_windows(doc[linkfields['NativeLink']]))) for doc in dat_rows ]
        native_paths = [str(file) for file in native_files]
        files_exist = []
        for dat_path in dat_paths:
            for txt_path in native_paths:
                if dat_path in txt_path:
                    files_exist.append(dat_path)
                else:
                    continue
        check_path_diff =  len(files_exist) == len(dat_paths)
        checks.append(check_path_diff)
    return checks


def copy_dat_file_with_fixed_format(bom_file, new_file, separator_str='', remove_chars=[], new_separator='\x14'):
    """Copy the dat file (in utf-8 with BOM format) to a new file using utf-8 only encoding.

    __Note:__ typical ediscovery separator characters include: thorn (þ) and pilcrow (\x14 or ¶)

    __Usage:__
    ```
    >>> original_file = dirHome / ''
    >>> new_file = dirHome / 'new_file.dat'
    >>> copy_dat_file_with_fixed_format(original_file, new_file, 'þ\x14þ', ['þ'])
    >>> df = pd.read_csv(new_file, sep='\x14')
    ```
    """
    s = open(bom_file, mode='r', encoding='utf-8-sig').read()
    s = s.replace(separator_str, new_separator)
    if len(remove_chars) > 0:
        for char in remove_chars:
            s = s.replace(char, '')
    open(new_file, mode='w', encoding='utf-8').write(s)
    return True


def get_file_names(dir_path):
    """..."""
    p_dir_path = pathlib.Path(dir_path)
    if p_dir_path.is_dir():
        files = [item for item in p_dir_path.glob('**/*') if item.is_file()]
    else:
        raise TypeError
    return files


def get_file_lines(file_path):
    """..."""
    if pathlib.Path(file_path).is_file():
        lines = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
    else:
        raise TypeError
    return lines


def get_nested_dirs_files_lines(dir_path):
    """..."""
    files_lines = {}
    try:
        if pathlib.Path(dir_path).is_dir():
            dirs = [dir for dir in dir_path.iterdir() if dir.is_dir()]
            for dir in dirs:
                files = [file for file in dir.iterdir() if file.is_file()]
                for file_path in files:
                    with open(file_path, 'r') as f:
                        file_lines = f.readlines()
                        files_lines[str(file_path)] = file_lines
    except:
        raise TypeError
    return files_lines


def get_encoding(filepath) -> str:
    with open(filepath, "rb") as readfile:
        raw = readfile.read()
    det = chardet.detect(raw)
    return det["encoding"]


def get_lines(filepath, encoding) -> List[str]:
    try:
        with open(filepath, encoding=encoding, errors="backslashreplace") as txt_file:
            lines: List[str] = list(txt_file.readlines())
        return lines
    except UnicodeDecodeError as e:
        click.echo(f"Error decoding {filepath}: {e}")
    raise Exception("Could not parse file")


def remove_empty_lines(lines):
    new_lines = []
    for line in lines:
        if len(line) > 1:
            new_lines.append(line)
    return new_lines


def get_table_rows_from_dat_file(dat_file, sep='\x14'):
    """Get table rows from .dat file (leverage pandas).

    __Usage__
    ```
    >>> dat_rows = get_table_rows_from_dat_file(dat_filepath)
    ```
    """
    df = None
    dat_file = pathlib.Path(dat_file)
    if dat_file.is_file():
        df = pd.read_csv(dat_file, sep=sep, encoding='utf-8')
    return df.to_dict('records')


def get_table_rows_from_lines(lines, field_list_or_first_row_header=[]):
    """Get table rows from .dat from ingested lines (BASIC CODE).

    __Usage__
    ```
    >>> dat_lines = get_file_lines(dat_filepath)
    >>> dat_rows = get_table_rows(dat_lines)
    ```
    """
    #support
    def split_cells_on_chars(ln):
        chars = ["þþ", "þ\x14þ", "þ\n", "þ", "|", "\n"]
        tmp_line = [ln]
        idx = 0
        while len(tmp_line) == 1 and idx < len(chars):
            nested_list = [item.split(chars[idx]) for item in tmp_line]
            tmp_line = list(chain(*nested_list))
            idx = idx + 1
            if idx == len(chars):
                raise TypeError
        
        if len(tmp_line) > 1:
            for char in chars:
                tmp_line = [item.strip(char) for item in tmp_line]
        
        return tmp_line

    #main
    new_lines = []
    for line in lines:
        new_line = split_cells_on_chars(line)
        new_line = [i.strip("þ") for i in new_line]
        new_line = [i.strip("þ\n") for i in new_line]
        new_line = [i.strip("|") for i in new_line]
        cell_per_line = len(new_line)
        assert cell_per_line > 1
        new_lines.append(new_line)
    new_lines = remove_empty_lines(new_lines)
    assert all([len(l) == cell_per_line for l in new_lines])

    if field_list_or_first_row_header==[]:
        fields = new_lines.pop(0)
    else:
        fields = field_list_or_first_row_header
    rows = []
    for line in new_lines:
        row = {}
        for i, field_name in enumerate(fields):
            row[field_name] = line[i]
        rows.append(row)

    assert len(rows) == len(new_lines)
    return rows


def make_csv(rows, filepath: pathlib.Path):
    with open(str(filepath), "wt") as writefile:
        writer = csv.DictWriter(writefile, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def make_json(cells, filepath: pathlib.Path):
    with open(str(filepath), "wt") as writefile:
        write_text = json.dumps(cells, sort_keys=True, indent=4)
        writefile.write(write_text)


@click.command()
@click.argument("source")
@click.argument("dest")
@click.option(
    "-j",
    "--json",
    is_flag=True,
    help="Whether to convert to JSON, rather than CSV (the default)",
)
def loadfile(source, dest, json):
    """
    Converts a .DAT formatted loadfile to CSV or JSON.

    SOURCE: the the file you wish to convert

    DEST: the directory where the converted file will be created.

    The converted file will have the same name as the original file, with either .csv or
    .json added at the end.
    """

    src_path: pathlib.Path = pathlib.Path(source)
    if json:
        dest_path = pathlib.Path(dest) / f"{src_path.name}.json"
    else:
        dest_path = pathlib.Path(dest) / f"{src_path.name}.csv"
    if src_path.is_file():
        enc = get_encoding(src_path)
        lines = get_lines(src_path, enc)
        rows = get_table_rows(lines)
        if json:
            make_json(rows, dest_path)
        else:
            make_csv(rows, dest_path)
        click.echo(Fore.GREEN + f"Success: output saved to {dest_path}")
    else:
        click.echo(Fore.RED + f"Oops, {source} is a directory")


if __name__ == "__main__":
    loadfile()
