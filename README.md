# pysudoers

This library provides a [Python][1] interface to the Linux sudoers file.  python-sudoers is open sourced under the [BSD 3-Clause license](LICENSE.txt).

[![CircleCI](https://circleci.com/gh/broadinstitute/python-sudoers/tree/master.svg?style=svg)](https://circleci.com/gh/broadinstitute/python-sudoers/tree/master)
[![codecov](https://codecov.io/gh/broadinstitute/python-sudoers/branch/master/graph/badge.svg)](https://codecov.io/gh/broadinstitute/python-sudoers)

## Basics

pysudoers still runs on Python 2.7, and Python >= 3.4

## Features

This library parses a sudoers file into its component parts.  It's not 100% compliant with the EBNF format of the file (yet), but it's getting there.  Currently, the script parses out 6 distinct line types from the file:

* Defaults (This is only a string currently.  Pieces of a Defaults setting are not parsed/separated.)
* Cmnd_Alias
* Host_Alias
* Runas_Alias
* User_Alias
* User specifications (which we call **rules**)

As user specifications are the most complicated, they are most likely the area that needs the most improvement.  Currently, the following pieces of a user specification are separated out as part of the parsing:

* User list
* Host list
* Command list (containing):
 ** Tags
 ** Run As notations
 ** Commands

## Installing

You can use pip to install pysudoers:

```sh
pip install pysudoers
```

## Examples

Parsing of the `sudoers` file is done as part of initializing the `Sudoers` object.  So, you can start using the properties under `Sudoers` immediately.  The following example will print out all the different "types" from the file:

```python
from pysudoers import Sudoers

sobj = Sudoers(path="tmp/sudoers")

for default in sobj.defaults:
    print(default)

for key in sobj.host_aliases:
    print(key)
    print(sobj.host_aliases[key])

for key in sobj.cmnd_aliases:
    print(key)
    print(sobj.cmnd_aliases[key])

for key in sobj.runas_aliases:
    print(key)
    print(sobj.runas_aliases[key])

for key in sobj.user_aliases:
    print(key)
    print(sobj.user_aliases[key])

for rule in sobj.rules:
    print(rule)
```

Now, suppose you want to print out all the user specifications (rules), but you only want to see the users and hosts for each rule.

```python
from pysudoers import Sudoers

sobj = Sudoers(path="tmp/sudoers")

for rule in sobj.rules:
    print("%s | %s" % (",".join(rule["users"]), ",".join(rule["hosts"])))
```

## Contributing

Pull requests to add functionality and fix bugs are always welcome.  Please check the CONTRIBUTING.md for specifics on contributions.

### Testing

We try to have a high level of test coverage on the code.  Therefore, when adding anything to the repo, tests should be written to test a new feature or to test a bug fix so that there won't be a regression.  This library is setup to be pretty simple to build a working development environment using [Docker][4].  Therefore, it is suggested that you have [Docker][4] installed where you clone this repository to make development easier.

To start a development environment, you should be able to just run the `dev.sh` script.  This script will use the `Dockerfile` in this repository to build a [Docker][4] container with all the dependencies for development installed using [Pipenv][3].

```sh
./dev.sh
```

The first time you run the script, it should build the [Docker][4] image and then drop you into the container's shell.  The directory where you cloned this repository should be volume mounted in to `/usr/src`, which should also be the current working directory.  From there, you can make changes as you see fit.  Tests can be run from the `/usr/src` directory by simply typing `green` as [green][5] has been setup to with the correct parameters.

[1]: https://www.python.org/ "Python"
[3]: https://pipenv.readthedocs.io/en/latest/ "Pipenv"
[4]: https://www.docker.com/ "Docker"
[5]: https://github.com/CleanCut/green "green"
