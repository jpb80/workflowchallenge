#!/usr/bin/env python

import unittest
from mock import mock_open, patch
import sys
import os
sys.path.insert(0, os.path.abspath("../src/workflowapp"))

import workflow

HERE = os.path.abspath(os.path.dirname(__file__))


class WorkflowTests(unittest.TestCase):


    @patch("os.path.isfile")
    @patch("json.load")
    @patch("__builtin__.open", new_callable=mock_open())
    def test_process_inventory(self, m, m_json, isfile):
        workflow.process_inventory("file.json")
        m.assert_called_with("file.json", "r")


    @patch("os.path.isfile")
    @patch("json.load")
    @patch("__builtin__.open", new_callable=mock_open())
    def test_load_settings(self, m, m_json, isfile):
        workflow.load_settings("file.json")
        m.assert_called_with("file.json", "r")


    @patch("requests.Session.get")
    def test_get_inventory(self, m):
        workflow.get_inventory("url", "jsonfile")
        m.assert_called_with("url")


suite = unittest.TestLoader().loadTestsFromTestCase(WorkflowTests)
unittest.TextTestRunner(verbosity=2).run(suite)
