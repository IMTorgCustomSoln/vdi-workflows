#!/usr/bin/env python3
"""
Report class
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


import datetime


class Report:
    """..."""

    def __init__(self, config, files):
        self.config = config
        self.files = files

    def run(self):
        pass



class TaskStatusReport(Report):
    """...

    * count for each Files
    * remainder between Tasks
    * save list of counts
    """

    def run(self):
        dirpath = self.config['WORKING_DIR'] / 'Reports' 
        dirpath.mkdir(parents=True, exist_ok=True)
        now = datetime.datetime.now().isoformat().replace('T','_').replace(':','-')
        filepath = dirpath / f'report-{now}.txt'
        with open(filepath, 'w') as report:
            next_task = None
            for idx, key in enumerate(self.files.keys()):
                files_1 = list(self.files[key].get_files())
                line = f'Files {key} contains {len(files_1)} files in directory {self.files[key].directory} of extension {self.files[key].extension_patterns}\n'
                self.config['LOGGER'].info(line)
                report.write(line)
                if idx+1 < len(self.files.keys()):
                    next_key = list(self.files.keys())[idx+1]
                    files_2 = list(self.files[next_key].get_files())
                    remaining_files = len(files_2) - len(files_1)
                    line = f'\tnext files {next_key} has {remaining_files} more files than {key}\n'
                    self.config['LOGGER'].info(line)
                    report.write(line)
                    if next_task==None and remaining_files>0:
                        next_task = line
            if next_task:
                report.write('\n\nNext task with remaining files:')
                report.write('\n'+line)
        return True