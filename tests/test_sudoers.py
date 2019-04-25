# -*- coding: utf-8 -*-
"""Define the Sudoers unit tests."""
# Don't warn about things that happen as that is part of unit testing
# pylint: disable=protected-access

import os
import sys

# Python 2/3 compatibility
try:
    from unittest import mock
except ImportError:
    import mock
from testtools import TestCase

from pysudoers import BadAliasException, BadRuleException, DuplicateAliasException
from pysudoers import Sudoers


class TestSudoers(TestCase):
    """Act as a base class for all Sudoers tests."""

    def setUp(self):
        """Set up class-wide variables and mocks."""
        super(TestSudoers, self).setUp()

        # Differentiate patch IDs for "open" depending on the Python version
        pyver = sys.version_info[0]
        self.open_patch_id = "builtins.open"
        if pyver < 3:
            self.open_patch_id = "__builtin__.open"

        # Find the path to the test sudoers file
        pwd = os.path.dirname(__file__)
        self.test_data_dir = os.path.join(pwd, "data")
        self.test_correct_file = os.path.join(self.test_data_dir, "correct.txt")

        self.test_correct_rules = [
            {"users": ["SOMEUSERS"], "hosts": ["SOMEHOSTS"], "commands": [
                {"run_as": ["SOMERUNAS"], "tags": None, "command": "SOMECMND"},
            ]},
            {"users": ["SOMEUSERS"], "hosts": ["ALL"], "commands": [
                {"run_as": ["SOMERUNAS"], "tags": None, "command": "/path/to/something/else"},
            ]},
            {"users": ["SOMEUSERS"], "hosts": ["SOMEHOSTS"], "commands": [
                {"run_as": ["ALL"], "tags": ["NOPASSWD"], "command": "/path/to/something/else"},
                {"run_as": ["ALL"], "tags": ["NOPASSWD"], "command": "/path/to/more"},
            ]},
            {"users": ["randouser"], "hosts": ["SOMEHOSTS"], "commands": [
                {"run_as": ["SOMERUNAS"], "tags": None, "command": "SOMECMND"},
                {"run_as": ["root"], "tags": None, "command": "/path/to/more/things"},
            ]}
        ]

        self.fake_path = "/path/to/sudoers"

    def tearDown(self):
        """Tear down everything after each test."""

        super(TestSudoers, self).tearDown()

        mock.patch.stopall()


class TestInit(TestSudoers):
    """Test the class initializer."""

    def test_defaults(self):
        """Parameters are set correctly inside the class using defaults."""
        # Mock out "open" so we don't actually open a file
        with mock.patch(self.open_patch_id, mock.mock_open()) as mock_file:
            sudoobj = Sudoers(path=self.fake_path)
            mock_file.assert_called_with(self.fake_path, "r")

            # Check all the internal values
            self.assertEqual(sudoobj._path, self.fake_path)

    def test_hard_coded(self):
        """Hard coded alias names are locked and shouldn't change."""
        # Mock out "open" so we don't actually open a file
        alias_names = ["Cmnd_Alias", "Host_Alias", "Runas_Alias", "User_Alias"]

        with mock.patch(self.open_patch_id, mock.mock_open()) as mock_file:
            sudoobj = Sudoers(path=self.fake_path)
            mock_file.assert_called_with(self.fake_path, "r")

            # Check all the internal values
            self.assertEqual(sudoobj._alias_types, alias_names)

    def test_data_setup(self):
        """Internal _data key structure is setup correctly."""
        # Mock out "open" so we don't actually open a file
        with mock.patch(self.open_patch_id, mock.mock_open()) as mock_file:
            sudoobj = Sudoers(path=self.fake_path)
            mock_file.assert_called_with(self.fake_path, "r")

            # Check all the internal values
            for alias in sudoobj._alias_types:
                self.assertIn(alias, sudoobj._data)

            self.assertIn("Defaults", sudoobj._data)
            self.assertIn("Rules", sudoobj._data)

    def test_easy_parse(self):
        """Correct parameters yield a correctly parsed sudoers file."""
        # Find the path to the test sudoers file
        sudoobj = Sudoers(path=self.test_correct_file)

        # Check all the internal values for aliases
        self.assertIn("SOMECMND", sudoobj._data["Cmnd_Alias"])
        self.assertEqual(sudoobj._data["Cmnd_Alias"]["SOMECMND"], ["/path/to/the/command"])
        self.assertIn("SOMEHOSTS", sudoobj._data["Host_Alias"])
        self.assertEqual(sudoobj._data["Host_Alias"]["SOMEHOSTS"], ["some-host1", "some-host2"])
        self.assertIn("SOMERUNAS", sudoobj._data["Runas_Alias"])
        self.assertEqual(sudoobj._data["Runas_Alias"]["SOMERUNAS"], ["runuser"])
        self.assertIn("SOMEUSERS", sudoobj._data["User_Alias"])
        self.assertEqual(sudoobj._data["User_Alias"]["SOMEUSERS"], ["user1", "user2", "user3"])

        # Check internal values for defaults
        self.assertEqual(sudoobj._data["Defaults"], ["Defaults !insults", "Defaults:SOMEUSERS !umask"])
        # Check internal values for rules
        self.assertEqual(sudoobj._data["Rules"], self.test_correct_rules)


class TestProperties(TestSudoers):
    """Test the class properties."""

    def setUp(self):
        """Set up class-wide variables and mocks."""
        super(TestProperties, self).setUp()

        self.sudoobj = Sudoers(path=self.test_correct_file)

    def test_cmnd_aliases(self):
        """cmnd_aliases property returns the correct data."""
        # Make sure the values match
        self.assertIn("SOMECMND", self.sudoobj.cmnd_aliases)
        self.assertEqual(self.sudoobj.cmnd_aliases["SOMECMND"], ["/path/to/the/command"])

    def test_host_aliases(self):
        """host_aliases property returns the correct data."""
        # Make sure the values match
        self.assertIn("SOMEHOSTS", self.sudoobj.host_aliases)
        self.assertEqual(self.sudoobj.host_aliases["SOMEHOSTS"], ["some-host1", "some-host2"])

    def test_rules(self):
        """rules property returns the correct data."""
        # Make sure the values match
        self.assertEqual(self.sudoobj.rules, self.test_correct_rules)

    def test_runas_aliases(self):
        """runas_aliases property returns the correct data."""
        # Make sure the values match
        self.assertIn("SOMERUNAS", self.sudoobj.runas_aliases)
        self.assertEqual(self.sudoobj.runas_aliases["SOMERUNAS"], ["runuser"])

    def test_path(self):
        """path property returns the correct data."""
        # Make sure the values match
        self.assertEqual(self.sudoobj.path, self.test_correct_file)

    def test_user_aliases(self):
        """user_aliases property returns the correct data."""
        # Make sure the values match
        self.assertIn("SOMEUSERS", self.sudoobj.user_aliases)
        self.assertEqual(self.sudoobj.user_aliases["SOMEUSERS"], ["user1", "user2", "user3"])


class TestParser(TestSudoers):
    """Test the file parser for errors."""

    def test_bad_alias1(self):
        """An alias without a name will raise an exception."""
        # Find the path to the test sudoers file
        test_file = os.path.join(self.test_data_dir, "bad_alias1.txt")
        self.assertRaises(BadAliasException, Sudoers, path=test_file)

    def test_bad_alias2(self):
        """An alias without a name will raise an exception."""
        # Find the path to the test sudoers file
        test_file = os.path.join(self.test_data_dir, "bad_alias2.txt")
        self.assertRaises(BadAliasException, Sudoers, path=test_file)

    def test_dup_alias(self):
        """An alias without a name will raise an exception."""
        # Find the path to the test sudoers file
        test_file = os.path.join(self.test_data_dir, "dup_alias.txt")
        self.assertRaises(DuplicateAliasException, Sudoers, path=test_file)

    def test_bad_rule(self):
        """A rule without an equal sign will raise an exception."""
        # Find the path to the test sudoers file
        test_file = os.path.join(self.test_data_dir, "bad_rule.txt")
        self.assertRaises(BadRuleException, Sudoers, path=test_file)
