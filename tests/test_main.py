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


    @patch("os.path.isdir")
    @patch("os.path.isfile")
    @patch("json.load")
    @patch("__builtin__.open", new_callable=mock_open())
    def test_setup(self, m, m_json, isfile, isdir):
        workflow.setup("file.json", "output")
        m.assert_called_with("file.json", "r")
        isdir.assert_called_with("output")


    @patch("requests.Session.get")
    def test_get_inventory(self, m):
        workflow.get_inventory("url", "jsonfile")
        m.assert_called_with("url")


    @patch("__builtin__.open", new_callable=mock_open())
    def test_run_statistics_on_column(self, m):
        inv_row = dict(
            {
                "Port": "Shanghai, China",
                "Rank": "1",
                "Volume 2011": "31.74",
                "Volume 2012": "32.53",
                "Volume 2013": "33.62",
                "Volume 2014": "35.29",
                "Volume 2015": "36.54"
            })

        inventory = list()
        inventory.append(inv_row)
        workflow.run_statistics_on_column(inventory, "Volume 2015", "file.json")
        m.assert_called_with("file.json", "w")


    def test_median_odd(self):
        sorted_values = [5.0,4.5,3.0,2.5,1.0]
        result = workflow._median(sorted_values)
        self.assertEqual(result, 3.0)


    def test_median_even(self):
        sorted_values = [5.0,4.5,3.0,2.5,1.5,1.0]
        result = workflow._median(sorted_values)
        self.assertEqual(result, 2.75)


    def test_max(self):
        sorted_values = [5.0,4.5,3.0,2.5,1.0]
        result = workflow._max(sorted_values)
        self.assertEqual(result, 5.0)


    def test_min(self):
        sorted_values = [5.0,4.5,3.0,2.5,1.0]
        result = workflow._min(sorted_values)
        self.assertEqual(result, 1.0)


suite = unittest.TestLoader().loadTestsFromTestCase(WorkflowTests)
unittest.TextTestRunner(verbosity=2).run(suite)
