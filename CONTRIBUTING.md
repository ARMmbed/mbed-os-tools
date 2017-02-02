* [Contributing](#contributing)
  * [Contributor argeement](#contributor-agreement)
  * [Enhancements vs bugs](#enhancements-vs-bugs)
  * [Workflow](#workflow)
    * [Forking and cloning this repository](#forking-and-cloning-this-repository)
    * [Issues solving](#issues-solving)
    * [Code review](#code-review)
  * [Issues and bug reporting](#issues-and-bug-reporting)
* [How to contribute](#how-to-contribute)
  * [Simple workflow for bugifx](#simple-workflow-for-bugifx)
    * [Branch naming conventions](#branch-naming-conventions)
  * [Coding style and coding rules](#coding-style-and-coding-rules)
    * [Code Like a Pythonista: Idiomatic Python](#code-like-a-pythonista-idiomatic-python)
    * [Coding Style: Readability Counts](#coding-style-readability-counts)
    * [Style Guide for Python Code](#style-guide-for-python-code)
    * [Whitespace](#whitespace)
    * [Naming](#naming)
* [Testing and code coverage](#testing-and-code-coverage)
* [Code coverage](#code-coverage)
* [Keep your GitHub fork updated](#keep-your-github-fork-updated)
    * [Tracking changes](#tracking-changes)
    * [Verify with:](#verify-with)
    * [Updating](#updating)
* [Final notes](#final-notes)

# Contributing
We really appreciate your contributions! We are an open source project and we need your help. We want to keep it as easy as possible to contribute changes that get things working in your environment. There are a few guidelines that we need contributors to follow so that we can have a chance of keeping on top of things.

## Contributor agreement
For your pull request to be accepted, we will need you to agree to our [contributor agreement](http://developer.mbed.org/contributor_agreement/) to give us the necessary rights to use and distribute your contributions. (To click through the agreement create an account on mbed.com and log in.)


## Enhancements vs bugs
Enhancements are:
* New features implementation.
* Code refactoring.
* Coding rules or coding style improvements.
* Code comments improvement.
* Documentation work.
Bugs are:
* Issues raised internally or externally by application users.
* Internally (from the ARM mbed team) created issues from the Continuous Integration pipeline and build servers.
* Issues detected using automation tools such as compilers, sanitizers, static code and analysis tools.

## Workflow
### Forking and cloning this repository
First [fork](https://help.github.com/articles/fork-a-repo/) this repository in GitHub, then clone it locally with:
```
$ git clone <repo-link>
```
Now you can create separate branches in the forked repository and prepare pull requests with changes.
### Issues solving
Simple work-flow issue solving process may contain below steps:
1. Issue filed (by any user).
2. Proper label assigned by gate-keeper.
3. Bug-fixer forked and cloned.
4. Optional clarifications made using the Issues tab's Comment section.
5. Pull request with fix created.
6. Pull request reviewed by others.
7. All code review comments handled.
8. Pull request accepted by gate-keeper.
9. Pull request merged successfully.

### Code review
The code review process is designed to catch both style and domain specific issues. It is also designed to follow and respect the _definition of done_. Please make sure your code follows the style of the source code you are modifying. Each pull request must be reviewed by the gate-keeper before we can merge it to the master branch.
## Issues and bug reporting
Please report all bugs using the Issues tab on the GitHub web-page. It will help us to collaborate on issues more promptly. One of our gate-keepers (developers responsible for quality and the repository) will review the issue and assign a label such as _bug_, _enhancement_, _help wanted_ or _wontfix_.
# How to contribute
You can either file a bug, help fix a bug or propose a new feature (or enhancement) and implement it yourself. If you want to contribute please:
* Bug reports: File a bug report in the Issues tab of this repo to let us know there are problems with our code.
  * Make sure your bug report contains a simple description of the problem.
  * Include information about the host computer's configuration and OS or VM used.
  * Include information about the application's version. All applications should have at least a ``--version`` switch you can use to check the version.
  * Copy/paste useful console dumps and configuration files' content. Please use [fenced code blocks](https://help.github.com/articles/github-flavored-markdown/#fenced-code-blocks) to encapsulate code snippets.
* New features or bug fix: Create a pull request with your changes.
* General feedback: Give your feedback by posting your comments on existing pull requests and issues.

## Simple workflow for bugifx
* Select an issue to fix from open issues.
* Fork repository you wish to modify.
* Clone locally your fork, create a separate branch for issue to fix:

Note: In this example we will fix issue #38.
```
$ git clone <fork-repo-link>
$ git checkout -b issue_38
... add changes locally to fix an issue
```

* Add and commit your changes.

```
$ git add .
$ git commit -m "Add fix for issue #38" -m "More verbose explanation of the change/fix"
$ git push origin issue_38

```

* Push changes to GitHub.
* Create pull request from GitHub webpage (your fork's dashboard).

### Branch naming conventions
We prefer is you use standardised naming convention when creating pull requests.
Below few example of branch names' prefixes you could use when creating pull request from your fork:
* ```issue_``` - branch with fix for issue. E.g. ```issue_38```.
* ```doc_``` - documentation update. E.g. ```doc_add_faq```.
* ```devel_``` - development of a new feature. E.g. ```devel_udp_client_test```.
* ```test_``` - when pull request will consist of only new/updates to test cases. E.g. ```test_paralllel_execution```.

## Coding style and coding rules
This chapter attempts to explain the basic styles and patterns that are used in mbed test tools projects. he following norms should be followed for new code, and for code that needs clean-up.

### Code Like a Pythonista: Idiomatic Python
Please do your best to follow [Idiomatic Python](http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html) interactive tutorial.

### Coding Style: Readability Counts
"*Programs must be written for people to read, and only incidentally for machines to execute.*"
    —Abelson & Sussman, Structure and Interpretation of Computer Programs
Try to make your programs easy to read and obvious.

### Style Guide for Python Code
Please see [PEP 0008 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/) for details.

### Whitespace
* 4 spaces per indentation level.
* No hard tabs.
* Never mix tabs and spaces.
* One blank line between functions.
* Two blank lines between classes.
* No whitespace at the end of a line.

* Add a space after "," in dicts, lists, tuples, & argument lists, and after ":" in dicts, but not before.
* Put spaces around assignments & comparisons (except in argument lists).
* No spaces just inside parentheses or just before argument lists.
* No spaces just inside docstrings.

Example:
```python
def make_squares(key, value=0):
    """! Return a dictionary and a list...
    @param value Value parameter with default value of zero (0)
    @return Retruns tuple of 'd' stuff and 'l' stuff
    """
    d = {key: value}
    l = [key, value]
    return d, l
```

### Naming
* ```joined_lower``` for functions, methods, attributes
* ```joined_lower``` or ALL_CAPS for constants
* ```StudlyCaps``` for classes
* ```camelCase``` only to conform to pre-existing conventions
* Attributes: ```interface```, ```_internal```, ```__private```
* But try to avoid the ```__private``` form. I never use it. Trust me. If you use it, you WILL regret it later.

# Testing and code coverage
The application should be unit tested (at least a minimal set of unit tests should be implemented in the ``/test`` directory). We should be able to measure the unit test code coverage.
Run a unit test suite to make sure your changes are not breaking current implementation:
```
$ cd <package>
$ python setup.py test
```
# Code coverage
To measure application code coverage for unit tests please use the coverage tool. This set of commands will locally create a code coverage report for all unit tests:
```
$ cd <package>
$ coverage run setup.py test
$ coverage report
$ coverage html
```
Last command will generate for you useful HTML code coverage report. It can be used to check which parts of your code are not unit tested.

# Keep your GitHub fork updated
I want to fork a GitHub repo SOME_REPO/appname to USER/appname and want to keep it updated.
### Tracking changes
```
$ git clone git@github.com:USER/appname.git
$ cd appname
$ git remote add upstream git@github.com:SOME_REPO/appname.git
```
### Verify with:
```
$ git remote -v
origin  https://github.com/USER/appname.git (fetch)
origin  https://github.com/USER/appname.git (push)
upstream  https://github.com/SOME_REPO/appname.git (fetch)
upstream  https://github.com/SOME_REPO/appname.git (push)
```
### Updating
Each time I want to update, from my local master branch I will do the following:
```
$ git fetch upstream
$ git rebase upstream/master
```
The goal of the rebase is to have a cleaner history if I have local changes or commits on the repo.
# Final notes
1. Please do not change the version of the package in the ``setup.py`` file. The person or process responsible for releasing will do this and release the new version.
2. Keep your GitHub updated! Please make sure you are rebasing your local branch with changes so you are up to date and it is possible to automatically merge your pull request.
3. Please, if possible, squash your commits before pushing to the remote repository.
4. Please, as part of your pull request:
  * Update ``README.md`` if your changes add new functionality to the module.
  * Add unit tests to the ``/test`` directory to cover your changes or new functionality.
