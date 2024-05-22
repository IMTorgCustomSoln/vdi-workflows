#!/usr/bin/env python3
"""
Main entrypoint
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

import os
import sys
import argparse
from pathlib import Path
import time
import json
from datetime import datetime


#register here
from config import config_env
from workflows import (
    workflow_asr
)
workflow_options = {
    'workflow_asr': workflow_asr.workflow_asr
    }



def main(args):
    """..."""
    config_env.config()
    if args.workflow in workflow_options.keys():
        workflow = workflow_options[args.workflow]
        getattr(workflow, args.task)()





if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow", 
                        help="Choose workflow from available files: `./workflows/workflow_*` ")
    parser.add_argument("task", 
                        help="Choose task workflow should perform")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)