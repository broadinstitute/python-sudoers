# -*- coding: utf-8 -*-
"""Manage a sudoers file."""

import logging
import re

LOGGER = logging.getLogger(__name__)


class Sudoers(object):
    """Provide methods for dealing with all aspects of a sudoers file."""

    def __init__(self, path):
        """Initialize the class.

        :param string path: The path to the sudoers file
        """
        self._alias_types = ["Cmnd_Alias", "Host_Alias", "Runas_Alias", "User_Alias"]

        self._path = path

        # Initialize the internal _data data member
        self._data = {}
        self._data["Rules"] = []
        for alias in self._alias_types:
            self._data[alias] = {}

        self.parse_file()

    @property
    def cmnd_aliases(self):
        """Return the command aliases."""
        return self._data["Cmnd_Alias"]

    @property
    def host_aliases(self):
        """Return the host aliases."""
        return self._data["Host_Alias"]

    @property
    def path(self):
        """Return the path to the sudoers file."""
        return self._path

    @property
    def rules(self):
        """Return the rules."""
        return self._data["Rules"]

    @property
    def runas_aliases(self):
        """Return the run as aliases."""
        return self._data["Runas_Alias"]

    @property
    def user_aliases(self):
        """Return the user aliases."""
        return self._data["User_Alias"]

    def parse_line(self, line):
        """Parse one line of the sudoers file."""
        pieces = line.split()

        if pieces[0] in self._alias_types:
            index = pieces[0]

            # Raise an exception if there aren't at least 2 elements after the split
            if len(pieces) < 2:
                raise BadAliasException("bad alias: %s" % line)

            # We need to keep all line spacing, so use the original line with the index stripped
            kvline = re.sub(r"^%s " % index, "", line)

            # Split out the alias key/value
            keyval = kvline.split("=")
            if (len(keyval) != 2) or (not keyval[1]):
                raise BadAliasException("bad alias: %s" % line)
            if keyval[0] in self._data[index]:
                raise DuplicateAliasException("duplicate alias: %s" % line)

            # Separate the comma-separated list of values
            val_list = keyval[1].split(",")
            if not val_list:
                raise BadAliasException("bad alias: %s" % line)
            # Make sure extra whitespace is stripped for each item in the list, then convert back to a list
            val_list = list(map(str.strip, val_list))

            self._data[index][keyval[0]] = val_list

            # Debugging output
            logging.debug("%s: %s => %s", index, keyval[0], val_list)
        else:
            # Everything that doesn't match the above aliases is assumed to be a rule
            self._data["Rules"].append(line)

    def parse_file(self):
        """Parse the sudoers file."""
        backslash_re = re.compile(r"\\$")

        sudo = open(self._path, "r")

        for line in sudo:
            # Strip whitespace from beginning and end
            line = line.strip()

            # Ignore all comments
            if line.startswith("#"):
                continue

            # Ignore all empty lines
            if not line:
                continue

            if backslash_re.search(line):
                concatline = line.rstrip("\\")
                while True:
                    # Get the next line from the file
                    nextline = next(sudo).strip()

                    # Make sure we don't go past EOF
                    if not nextline:
                        break

                    # Add the next line to the previous line
                    concatline += nextline.rstrip("\\")

                    # Break when the next line doesn't end with a backslash
                    if not backslash_re.search(nextline):
                        break

                line = concatline

            logging.debug(line)
            self.parse_line(line)


class BadAliasException(BaseException):
    """Provide a custom exception type to be raised when an alias is malformed."""


class DuplicateAliasException(BaseException):
    """Provide a custom exception type to be raised when an alias is malformed."""
