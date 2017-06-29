#!/usr/bin/env python

# Package app
import app
import unittest

# Module from package app
from app import helper


class TestWombatMethods(unittest.TestCase):

    def test_helper_get_status_success(self):

        event = "testing event"
        success_status = 0
        return_status = helper.get_status(event, success_status)
        self.assertEqual(return_status, 0)


    def test_helper_get_status_failure(self):

        event = "testing event"
        failure_status = 2
        return_status = helper.get_status(event, failure_status)
        self.assertEqual(return_status, 2)



suite = unittest.TestLoader().loadTestsFromTestCase(TestWombatMethods)
unittest.TextTestRunner(verbosity=2).run(suite)
