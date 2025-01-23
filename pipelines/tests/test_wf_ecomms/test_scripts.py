#!/usr/bin/env python3
"""
Test ecomms scripts
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from tests.test_wf_ecomms.scripts import (combine_dats_to_pickle)

from pathlib import Path



def test_combine_dats_to_pickle():
    result = combine_dats_to_pickle()
    assert result == True