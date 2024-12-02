"""Define the Sudoers unit tests."""
# Don't warn about things that happen as that is part of unit testing
# pylint: disable=protected-access

from pathlib import Path
from textwrap import dedent
from unittest import mock

import pytest
from testtools import TestCase

from pysudoers import (
    BadAliasExceptionError,
    BadRuleExceptionError,
    DuplicateAliasExceptionError,
    Sudoers,
)


class TestSudoers(TestCase):
    """Act as a base class for all Sudoers tests."""

    def setUp(self) -> None:
        """Set up class-wide variables and mocks."""
        super().setUp()

        # Find the path to the test sudoers file
        pwd = Path(__file__).resolve().parent
        self.test_data_dir = pwd / "data"
        self.test_correct_file = self.test_data_dir / "correct.txt"

        self.test_correct_rules = [
            {
                "users": ["SOMEUSERS"],
                "hosts": ["SOMEHOSTS"],
                "commands": [
                    {"run_as": ["SOMERUNAS"], "tags": None, "command": "SOMECMND"},
                ],
            },
            {
                "users": ["SOMEUSERS"],
                "hosts": ["ALL"],
                "commands": [
                    {
                        "run_as": ["SOMERUNAS"],
                        "tags": None,
                        "command": "/path/to/something/else",
                    },
                ],
            },
            {
                "users": ["SOMEUSERS"],
                "hosts": ["SOMEHOSTS"],
                "commands": [
                    {
                        "run_as": ["ALL"],
                        "tags": ["NOPASSWD"],
                        "command": "/path/to/something/else",
                    },
                    {
                        "run_as": ["ALL"],
                        "tags": ["NOPASSWD"],
                        "command": "/path/to/more",
                    },
                ],
            },
            {
                "users": ["randouser"],
                "hosts": ["SOMEHOSTS"],
                "commands": [
                    {"run_as": ["SOMERUNAS"], "tags": None, "command": "SOMECMND"},
                    {
                        "run_as": ["root"],
                        "tags": None,
                        "command": "/path/to/more/things",
                    },
                ],
            },
        ]

        self.fake_path = Path("/path/to/sudoers")

    def tearDown(self) -> None:  # pylint:disable=invalid-name
        """Tear down everything after each test."""
        super().tearDown()

        mock.patch.stopall()

    def get_mock_open(self, data: str = "") -> mock.MagicMock:
        """Return a read-only instance of mock_open that returns data with iteration setup correctly."""
        # Thanks SO! https://stackoverflow.com/questions/24779893/customizing-unittest-mock-mock-open-for-iteration
        mopen = mock.mock_open(read_data=dedent(data))
        mopen.return_value.__iter__ = lambda self: self
        mopen.return_value.__next__ = lambda self: next(iter(self.readline, ""))

        return mopen


class TestInit(TestSudoers):
    """Test the class initializer."""

    def test_defaults(self) -> None:
        """Parameters are set correctly inside the class using defaults."""
        # Mock out "open" so we don't actually open a file
        mopen = self.get_mock_open()
        with mock.patch.object(Path, "open", mopen) as mock_file:
            sudoobj = Sudoers(path=self.fake_path)
            mock_file.assert_called_with(encoding="ascii")

            # Check all the internal values
            assert sudoobj.path == self.fake_path

    def test_data_setup(self) -> None:
        """Internal _data key structure is setup correctly."""
        # Mock out "open" so we don't actually open a file
        mopen = self.get_mock_open()
        with mock.patch.object(Path, "open", mopen) as mock_file:
            sudoobj = Sudoers(path=self.fake_path)
            mock_file.assert_called_with(encoding="ascii")

            # Check all the internal values
            for alias in sudoobj.ALIAS_TYPES:
                assert alias in sudoobj._data

            assert "Defaults" in sudoobj._data
            assert "Rules" in sudoobj._data

    def test_easy_parse(self) -> None:
        """Correct parameters yield a correctly parsed sudoers file."""
        # Find the path to the test sudoers file
        sudoobj = Sudoers(path=self.test_correct_file)

        # Check all the internal values for aliases
        assert "SOMECMND" in sudoobj._data["Cmnd_Alias"]
        assert sudoobj._data["Cmnd_Alias"]["SOMECMND"] == ["/path/to/the/command"]
        assert "SOMEHOSTS" in sudoobj._data["Host_Alias"]
        assert sudoobj._data["Host_Alias"]["SOMEHOSTS"] == ["some-host1", "some-host2"]
        assert "SOMERUNAS" in sudoobj._data["Runas_Alias"]
        assert sudoobj._data["Runas_Alias"]["SOMERUNAS"] == ["runuser"]
        assert "SOMEUSERS" in sudoobj._data["User_Alias"]
        assert sudoobj._data["User_Alias"]["SOMEUSERS"] == [
            "user1",
            "user2",
            "user3",
            "user4",
            "user5",
            "user6",
            "user7",
        ]

        # Check internal values for defaults
        assert sudoobj._data["Defaults"] == [
            "Defaults !insults",
            "Defaults:SOMEUSERS !umask",
        ]
        # Check internal values for rules
        assert sudoobj._data["Rules"] == self.test_correct_rules


class TestProperties(TestSudoers):
    """Test the class properties."""

    def setUp(self) -> None:
        """Set up class-wide variables and mocks."""
        super().setUp()

        self.sudoobj = Sudoers(path=self.test_correct_file)

    def test_cmnd_aliases(self) -> None:
        """cmnd_aliases property returns the correct data."""
        # Make sure the values match
        assert "SOMECMND" in self.sudoobj.cmnd_aliases
        assert self.sudoobj.cmnd_aliases["SOMECMND"] == ["/path/to/the/command"]

    def test_host_aliases(self) -> None:
        """host_aliases property returns the correct data."""
        # Make sure the values match
        assert "SOMEHOSTS" in self.sudoobj.host_aliases
        assert self.sudoobj.host_aliases["SOMEHOSTS"] == ["some-host1", "some-host2"]

    def test_rules(self) -> None:
        """Rules property returns the correct data."""
        # Make sure the values match
        assert self.sudoobj.rules == self.test_correct_rules

    def test_runas_aliases(self) -> None:
        """runas_aliases property returns the correct data."""
        # Make sure the values match
        assert "SOMERUNAS" in self.sudoobj.runas_aliases
        assert self.sudoobj.runas_aliases["SOMERUNAS"] == ["runuser"]

    def test_path(self) -> None:
        """Path property returns the correct data."""
        # Make sure the values match
        assert self.sudoobj.path == self.test_correct_file

    def test_user_aliases(self) -> None:
        """user_aliases property returns the correct data."""
        # Make sure the values match
        assert "SOMEUSERS" in self.sudoobj.user_aliases
        assert self.sudoobj.user_aliases["SOMEUSERS"] == [
            "user1",
            "user2",
            "user3",
            "user4",
            "user5",
            "user6",
            "user7",
        ]


class TestParser(TestSudoers):
    """Test the file parser for errors."""

    def test_bad_alias1(self) -> None:
        """An alias without a name will raise an exception."""
        # Find the path to the test sudoers file
        data = "Host_Alias\n"
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            pytest.raises(BadAliasExceptionError, Sudoers, path=self.fake_path)

    def test_bad_alias2(self) -> None:
        """An alias without a name will raise an exception."""
        # Find the path to the test sudoers file
        data = "Runas_Alias SOMERUNAS=\n"
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            pytest.raises(BadAliasExceptionError, Sudoers, path=self.fake_path)

    def test_dup_alias(self) -> None:
        """An alias without a name will raise an exception."""
        # Find the path to the test sudoers file
        data = """
        Host_Alias SOMEHOSTS=some-host1, some-host2
        Host_Alias SOMEHOSTS=host3, host4
        """
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            pytest.raises(DuplicateAliasExceptionError, Sudoers, path=self.fake_path)

    def test_bad_rule(self) -> None:
        """A rule without an equal sign will raise an exception."""
        # Find the path to the test sudoers file
        data = "SOMEUSERS SOMEHOSTS (SOMERUNAS) SOMECMND\n"
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            pytest.raises(BadRuleExceptionError, Sudoers, path=self.fake_path)

    def test_escaped_split(self) -> None:
        """A command alias with embedded commas and escaped charaters will be correctly split."""
        # Find the path to the test sudoers file
        data = r"Cmnd_Alias AUDIT_CMDS = /bin/awk -F\: {OFS=FS; print "
        data += r"$1\,substr($2\,1\,4)\,$3\,$4\,$5\,$6\,$7\,$8\,$9} /var/log/audit.log"
        result = {
            "AUDIT_CMDS": [
                "/bin/awk -F\\:{OFS=FS; print "
                "$1\\,substr($2\\,1\\,4)\\,$3\\,$4\\,$5\\,$6\\,$7\\,$8\\,$9} /var/log/audit.log"
            ]
        }
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            sudoobj = Sudoers(path=self.fake_path)
            assert sudoobj.cmnd_aliases == result

    def test_hash_include(self) -> None:
        """An include with a hash will not cause an exception."""
        # Find the path to the test sudoers file
        data = "#include /test/dir/file\n"
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            _ = Sudoers(path=self.fake_path)

    def test_at_include(self) -> None:
        """An include with an @ will not cause an exception."""
        # Find the path to the test sudoers file
        data = "@include /test/dir/file\n"
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            _ = Sudoers(path=self.fake_path)

    def test_hash_includedir(self) -> None:
        """An includedir with a hash will not cause an exception."""
        # Find the path to the test sudoers file
        data = "#includedir /test/dir/file\n"
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            _ = Sudoers(path=self.fake_path)

    def test_at_includedir(self) -> None:
        """An includedir with an @ will not cause an exception."""
        # Find the path to the test sudoers file
        data = "@includedir /test/dir/file\n"
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            _ = Sudoers(path=self.fake_path)


class TestResolution(TestSudoers):
    """Test the alias resolution methods."""

    def test_no_nesting(self) -> None:
        """Test resolving an alias with no nested aliases."""
        data = "Cmnd_Alias SECONDCMDS=/path/to/second/cmd"
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            sudoobj = Sudoers(path=self.fake_path)
            res = sudoobj._resolve_aliases("Cmnd_Alias", "SECONDCMDS")
            assert res == ["/path/to/second/cmd"]

    def test_single_nesting(self) -> None:
        """Test resolving an alias with single level of nested aliases."""
        data = """
            Cmnd_Alias CMDALIAS=FIRSTCMDS, SECONDCMDS
            Cmnd_Alias FIRSTCMDS=/path/to/first/cmd,/path/to/first/cmd2
            Cmnd_Alias SECONDCMDS=/path/to/second/cmd
        """
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            sudoobj = Sudoers(path=self.fake_path)
            res1 = sudoobj._resolve_aliases("Cmnd_Alias", "CMDALIAS")
            res2 = sudoobj._resolve_aliases("Cmnd_Alias", "FIRSTCMDS")
            res3 = sudoobj._resolve_aliases("Cmnd_Alias", "SECONDCMDS")
            assert res1 == [
                "/path/to/first/cmd",
                "/path/to/first/cmd2",
                "/path/to/second/cmd",
            ]
            assert res2 == ["/path/to/first/cmd", "/path/to/first/cmd2"]
            assert res3 == ["/path/to/second/cmd"]

    def test_multiple_nesting(self) -> None:
        """Test resolving an alias with multiple levels of nested aliases."""
        data = """
            Cmnd_Alias CMDALIAS=FIRSTCMDS
            Cmnd_Alias FIRSTCMDS=/path/to/first/cmd,/path/to/first/cmd2,SECONDCMDS
            Cmnd_Alias SECONDCMDS=/path/to/second/cmd
        """
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            sudoobj = Sudoers(path=self.fake_path)
            res1 = sudoobj._resolve_aliases("Cmnd_Alias", "CMDALIAS")
            res2 = sudoobj._resolve_aliases("Cmnd_Alias", "FIRSTCMDS")
            res3 = sudoobj._resolve_aliases("Cmnd_Alias", "SECONDCMDS")
            assert res1 == [
                "/path/to/first/cmd",
                "/path/to/first/cmd2",
                "/path/to/second/cmd",
            ]
            assert res2 == [
                "/path/to/first/cmd",
                "/path/to/first/cmd2",
                "/path/to/second/cmd",
            ]
            assert res3 == ["/path/to/second/cmd"]

    def test_mapping(self) -> None:
        """Test resolving different alias types using accessor methods."""
        data = """
        Cmnd_Alias SOMECMDS=/path/to/second/cmd
        Host_Alias SOMEHOSTS=host1, host2,host3
        Runas_Alias SOMERUNAS=user1,user2
        User_Alias SOMEUSERS=user3, user4
        """
        mopen = self.get_mock_open(data)
        with mock.patch.object(Path, "open", mopen):
            sudoobj = Sudoers(path=self.fake_path)
            cmnd_res = sudoobj.resolve_command("SOMECMDS")
            host_res = sudoobj.resolve_host("SOMEHOSTS")
            runas_res = sudoobj.resolve_runas("SOMERUNAS")
            user_res = sudoobj.resolve_user("SOMEUSERS")
            assert cmnd_res == ["/path/to/second/cmd"]
            assert host_res == ["host1", "host2", "host3"]
            assert runas_res == ["user1", "user2"]
            assert user_res == ["user3", "user4"]
