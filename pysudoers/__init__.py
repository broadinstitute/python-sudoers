# -*- coding: utf-8 -*-
"""Manage a sudoers file."""

import logging
import re
import shlex

LOGGER = logging.getLogger(__name__)


class Sudoers(object):
    """Provide methods for dealing with all aspects of a sudoers file."""

    def __init__(self, path):
        """Initialize the class.

        :param string path: The path to the sudoers file or file-like object
        """
        self._alias_types = ["Cmnd_Alias", "Host_Alias", "Runas_Alias", "User_Alias"]

        self._path = path

        # Initialize the internal _data data member
        self._data = {}
        self._data["Defaults"] = []
        self._data["Rules"] = []
        for alias in self._alias_types:
            self._data[alias] = {}

        self.parse_file()

    @property
    def cmnd_aliases(self):
        """Return the command aliases."""
        return self._data["Cmnd_Alias"]

    @property
    def defaults(self):
        """Return any Defaults."""
        return self._data["Defaults"]

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

    @staticmethod
    def parse_alias(alias_key, line):
        """Parse an alias line into its component parts.
        :param str alias_key: The type of alias we are parsing
        :param str line: The line from sudoers

        :return: 0) the key for the alias and 1) the list of members of that alias
        :rtype: tuple
        """
        # We need to keep all line spacing, so use the original line with the index stripped
        kvline = re.sub(r"^%s\s*" % alias_key, "", line)

        # Split out the alias key/value
        keyval = kvline.split("=")
        if (len(keyval) != 2) or (not keyval[1]):
            raise BadAliasException("bad alias: %s" % line)

        # Separate the comma-separated list of values, respecting quotes
        lex = shlex.shlex(keyval[1], posix=True, punctuation_chars=True)
        lex.wordchars += '%'
        val_list = list(lex)
        terms = []
        if not val_list:
            raise BadAliasException("bad alias: %s" % line)
        lastterm = ','
        cmnd = ''
        for term in val_list:
            # terms looks like:  ['user1', ',' 'user2', 'host1', ',', 'host2]
            # start saving users.  Ignore commas.
            # if term is not a coma and lastterm is not a comma, start saving to hosts
            if lastterm != ',' and term != ',':
                cmnd += ' '
            elif term == ',':
                terms.append(cmnd)
                cmnd = ''
                lastterm = term
                continue
            cmnd += term
            lastterm = term
        if cmnd != '':
            terms.append(cmnd)
        # Return a tuple with the key / value pair
        return (keyval[0], terms)

    @staticmethod
    def parse_commands(commands):  # pylint: disable-msg=too-many-locals
        """Parse all commands from a rule line.

        Given a portion of a user specification (rule) line representing the *commands* part of the rule, parse out
        the components and return the results as a list of dictionaries.  There will be one dictionary per command in
        the line, and the keys of the dictionary will be *run_as*, *command*, and *tags*.  *run_as* and *tags* will
        also be lists.

        :param str commands: The portion of a rule line representing the commands

        :return: A dictionary describing the commands allowed
        :rtype: dict
        """
        # This is the regular expression to try to parse out each command per line if it has a run as
        runas_re = re.compile(r"\s*\(([\w,!?:]*)\)\s*([\S\s]*)")
        data = []

        # runas and tags are running collectors as they are inherited by later commands
        # runas starts as 'root' to account for any commands without an explicit run as list,
        # since they can only appear at the start, before the first explicit run as list
        runas = ['root']
        tags = None

        # split the commands along commas without splitting users/groups inside run as parenthesis
        # ex: "root ALL = (ALL, ALL) ALL" shouldn't be split along the comma in parenthesis
        cmds = list()
        in_parens = False
        curr_string = ""
        for char in commands:
            if in_parens:
                curr_string += char
                if char == ')':
                    in_parens = False
            else:
                if char == ',':
                    cmds.append(curr_string)
                    curr_string = ""
                elif char == '(':
                    in_parens = True
                    curr_string += '('
                else:
                    curr_string += char
        if curr_string != "":
            # add the last command
            cmds.append(curr_string)

        for command in cmds:
            tmp_data = {}
            tmp_command = None
            # See if we have parentheses (a "run as") in the current command
            match = runas_re.search(command)
            if match:
                # split along commas and colons to get users and groups
                unfiltered_data = re.split(",|:", match.group(1))
                # filter out empty string in the case of (: [groups])
                tmp_data["run_as"] = list(filter(None, unfiltered_data))
                # Keep track of the latest "run_as"
                runas = tmp_data["run_as"]
                # tmp["command"] = match.group(2)
                tmp_command = match.group(2)
            else:
                # Else, just treat this like a normal command
                tmp_data["run_as"] = runas
                # tmp["command"] = command
                tmp_command = command

            # Now check for tags
            tmp_data["tags"] = tags
            cmd_pieces = tmp_command.split(":")
            # The last element of the list, but return the string, not a 1-element list
            tmp_data["command"] = cmd_pieces[-1:][0]
            # tag_index is everything but the last element
            tag_index = len(cmd_pieces) - 1
            if tag_index > 0:
                tmp_data["tags"] = cmd_pieces[:tag_index]
                tags = tmp_data["tags"]

            data.append(tmp_data)

        return data

    def parse_rule(self, line):
        """Parse a rule line into its component parts.

        Given a user specification (rule) line, parse out the components and return the results in a dictionary.  The
        keys of the returned dictionary will be *users*, *hosts*, and *commands*.

        :param str line: The line from the sudoers file to be parsed

        :return: A dictionary describing the rule line
        :rtype: dict
        """
        rule_re = re.compile(r"([\S\s]*)=([\S\s]*)")
        rule = {}
        rule['original'] = line

        # Do a basic check for rule syntax
        match = rule_re.search(line)
        if not match:
            raise BadRuleException("invalid rule: %s" % line)

        # Split to the left of the = into user and host parts
        (userhost, cmndinfo) = re.split(r'''\s*?=\s*''', line, 1)

        lex = shlex.shlex(userhost, posix=True, punctuation_chars=True)
        lex.wordchars += '.%'
        terms = list(lex)
        rule["users"] = []
        rule["hosts"] = []
        key = "users"
        lastterm = ','
        for term in terms:
            # terms looks like:  ['user1', ',' 'user2', 'host1', ',', 'host2]
            # start saving users.  Ignore commas.
            # if term is not a coma and lastterm is not a comma, start saving to hosts
            if lastterm != ',' and term != ',':
                key = 'hosts'
            elif term == ',':
                lastterm = term
                continue
            rule[key].append(term)
            lastterm = term

        # Parse the commands
        rule["commands"] = self.parse_commands(cmndinfo)

        return rule

    def parse_defaults(self, line):
        """Parse the defaults into component pieces.
            Defaults[@user] setting
            Returns a list of dicts.  dict has two components.
                user: string
                setting: string
        """
        defaults_re = re.compile(r'''^Defaults # line starts with word default
                                    ([!@>:]\S+)?    # has optional scope
                                    \s+        # whitespace
                                    (.*)       # the rest of the line
                                 $''', re.X)
        pieces = defaults_re.split(line, maxsplit=1)  # one split leaves two parts
        return dict(
            {
                'scope': pieces[1],
                'setting': pieces[2]
            }
        )

    def parse_line(self, line):
        """Parse one line of the sudoers file.

        Take one line from the sudoers file and parse it.  The contents of the line are stored in the internal
        *_data* member according to the type of the line.  There is no return value from this function.
        """
        defaults_re = re.compile(r"^Defaults")

        # Trim unnecessary spaces (no spaces before/after commas, colons, and equals signs)
        line = re.sub(r"\s*([,:=])\s*", r"\g<1>", line)

        lex = shlex.shlex(line, posix=True, punctuation_chars=True)
        lex.whitespace += ','
        pieces = shlex.split(line)
        if pieces[0] in self._alias_types:
            index = pieces[0]

            # Raise an exception if there aren't at least 2 elements after the split
            if len(pieces) < 2:
                raise BadAliasException("bad alias: %s" % line)

            (key, members) = self.parse_alias(index, line)
            if key in self._data[index]:
                raise DuplicateAliasException("duplicate alias: %s" % line)

            self._data[index][key] = members
            # Debugging output
            logging.info("%s: %s => %s", index, key, members)
        elif defaults_re.search(line):
            default = self.parse_defaults(line)
            self._data["Defaults"].append(default)
        else:
            # Everything that doesn't match the above aliases is assumed to be a rule
            rule = self.parse_rule(line)
            self._data["Rules"].append(rule)

    def parse_file(self):
        """Parse the sudoers file.

        Parse the entire sudoers file.  The results are stored in the internal *_data* member.  There is no return
        value from this function.
        """
        backslash_re = re.compile(r"\\$")

        if hasattr(self._path, 'write'):
            sudo = self._path
        else:
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

        sudo.close()

    def _resolve_aliases(self, alias_type, name):
        """For the provided alias type, resolve the provided name for any aliases that may exist.

        This function is recursive in nature.  If the provided name is not an existing alias, it is returned (as a
        list). If the name is an alias of the provided type, the function is called again on each of the names derived
        from the alias in case there are nested aliases.

        :param obj alias_type: The alias type for which we are resolving
        :param str name: A string representing a name or another alias

        :return: A list of one or more name
        :rtype: list
        """
        data = []

        # See if the name provided is an alias or not.
        if name in self._data[alias_type]:
            namematch = self._data[alias_type][name]

            # For each name in the list, try to resolve that name as well, and then add it to the accumulator
            for expanded_name in namematch:
                resolved = self._resolve_aliases(alias_type, expanded_name)
                # Cycle through the resolved list and remove any duplicates
                for res in resolved:
                    if res not in data:
                        data.append(res)
        else:
            data = [name]

        return data

    def resolve_command(self, command):
        """Resolve the provided command for any aliases that may exist."""
        return self._resolve_aliases("Cmnd_Alias", command)

    def resolve_host(self, host):
        """Resolve the provided host for any aliases that may exist."""
        return self._resolve_aliases("Host_Alias", host)

    def resolve_runas(self, runas):
        """Resolve the provided run as user for any aliases that may exist."""
        return self._resolve_aliases("Runas_Alias", runas)

    def resolve_user(self, user):
        """Resolve the provided user for any aliases that may exist."""
        return self._resolve_aliases("User_Alias", user)


class BadAliasException(Exception):
    """Provide a custom exception type to be raised when an alias is malformed."""


class BadRuleException(Exception):
    """Provide a custom exception type to be raised when a rule is malformed."""


class DuplicateAliasException(Exception):
    """Provide a custom exception type to be raised when an alias is malformed."""
