#!/usr/bin/env python3
"""
Test workflow
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from workflows.workflow_asr import workflow_asr


def test_workflow_asr_prepare_models():
    #workflow_asr.prepare_models()
    assert True == True

def test_workflow_asr_prepare_workspace():
    check = workflow_asr.prepare_workspace()
    assert check == True

def test_workflow_asr_run():
    check = workflow_asr.run()
    assert check == True

def test_workflow_asr_report_task_status():
    check = workflow_asr.report_task_status()
    assert check == True

def test_workflow_asr_report_map_batch_to_files():
    check = workflow_asr.report_map_batch_to_files()
    assert check == True