# pysudoers

This library provides a [Python][1] interface to the Linux sudoers file.  python-sudoers is open sourced under the [BSD 3-Clause license](LICENSE.txt).

[![CircleCI](https://circleci.com/gh/broadinstitute/python-sudoers/tree/master.svg?style=svg)](https://circleci.com/gh/broadinstitute/python-sudoers/tree/master)
[![codecov](https://codecov.io/gh/broadinstitute/python-sudoers/branch/master/graph/badge.svg)](https://codecov.io/gh/broadinstitute/python-sudoers)

## Basics

`pysudoers` runs on [Python][1] >= 3.6

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
  * Tags
  * Run As notations
  * Commands

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

We try to have a high level of test coverage on the code.  Therefore, when adding anything to the repo, tests should be written to test a new feature or to test a bug fix so that there won't be a regression.  This library is setup to be pretty simple to build a working development environment using [Docker][3].  Therefore, it is suggested that you have [Docker][3] installed where you clone this repository to make development easier.

To start a development environment, you should be able to just run the `dev.sh` script.  This script will use the `Dockerfile` in this repository to build a [Docker][3] container with all the dependencies for development installed using [Poetry][2].

```sh
./dev.sh
```

The first time you run the script, it should build the [Docker][3] image and then drop you into the container's shell.  The directory where you cloned this repository should be volume mounted in to `/usr/src`, which should also be the current working directory.  From there, you can make changes as you see fit.  Tests can be run from the `/usr/src` directory by simply typing `green` as [green][4] has been setup to with the correct parameters.

## Changelog

To generate the `CHANGELOG.md`, you will need [Docker][3] and a GitHub personal access token.  We currently use [github-changelog-generator](https://github.com/github-changelog-generator/github-changelog-generator) for this purpose.  The following should generate the file using information from GitHub:

```sh
docker run -it --rm \
    -e CHANGELOG_GITHUB_TOKEN='yourtokenhere' \
    -v "$(pwd)":/working \
    -w /working \
    ferrarimarco/github-changelog-generator --verbose
```

To generate the log for an upcoming release that has not yet been tagged, you can run a command to include the upcoming release version.  For example, `2.0.0`:

```sh
docker run -it --rm \
    -e CHANGELOG_GITHUB_TOKEN='yourtokenhere' \
    -v "$(pwd)":/working \
    -w /working \
    ferrarimarco/github-changelog-generator --verbose --future-release 2.0.0 --unreleased
```

## Releases

Releases to the codebase are typically done using the [bump2version][5] tool.  This tool takes care of updating the version in all necessary files, updating its own configuration, and making a GitHub commit and tag.  We typically do version bumps as part of a PR, so you don't want to have [bump2version][5] tag the version at the same time it does the commit as commit hashes may change.  Therefore, to bump the version a patch level, one would run the command:

```sh
bump2version --verbose --no-tag patch
```

Once the PR is merged, you can then checkout the new master branch and tag it using the new version number that is now in `.bumpversion.cfg`:

```sh
git checkout master
git pull --rebase
git tag 1.0.0 -m 'Bump version: 0.1.0 → 1.0.0'
git push --tags
```

[1]: https://www.python.org/ "Python"
[2]: https://python-poetry.org/ "Poetry"
[3]: https://www.docker.com/ "Docker"
[4]: https://github.com/CleanCut/green "green"
[5]: https://pypi.org/project/bump2version/ "bump2version"
