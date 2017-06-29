#!/usr/bin/env python

# Package app
import app
import unittest

# Module from package app
from app import *


class TestBuildProjects(unittest.TestCase):

    def test_upper(self):
        helper.load_project(project, command_list)
        self.assertEqual("foo".upper(), "FOO")

suite = unittest.TestLoader().loadTestsFromTestCase(TestWombatMethods)
unittest.TextTestRunner(verbosity=2).run(suite)
