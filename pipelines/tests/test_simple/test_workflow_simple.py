#!/usr/bin/env python3
"""
Test simple (default) workflow
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from workflows.workflow_simple import workflow_simple

'''
def test_prepare_models():
    check1 = workflow_simple.prepare_models()
    assert check1 == True
'''

def test_prepare_workspace():
    check1 = workflow_simple.prepare_workspace()
    assert check1 == True


def test_run():
    check1 = workflow_simple.prepare_workspace()
    check2 = workflow_simple.run()
    assert check2 == True