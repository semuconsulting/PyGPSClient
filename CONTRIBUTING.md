# How to contribute

Here are some guidelines on how to contribute to the PyGPSClient project.

We appreciate any contribution, from fixing a grammar mistake in a comment to implementing new functionality. Please read this section if you are contributing your work.

Being one of our contributors, you agree and confirm that:

* The work is all your own.
* Your work will be distributed under a BSD 3-Clause License once your pull request is merged.
* You submitted work fulfils or mostly fulfils our styles and standards.

Please help us keep our issue list small by adding fixes: #{$ISSUE_NO} to the commit message of pull requests that resolve open issues. GitHub will use this tag to auto close the issue when the PR is merged.

## Coding conventions

  * This is open source software. We endeavour to make the code as transparent as possible.
  * We use [Eclipse PyDev](https://www.pydev.org/) for development and testing, but you are at liberty to use your preferred IDE.
  * We use [pylint](https://pypi.org/project/pylint/) (>=2.6.0) for code analysis.
  * We use [black](https://pypi.org/project/black/) (>= 20.8) for code formatting and ask that you do the same.

## Testing

We use python's native unittest framework for local unit testing, complemented by the Travis CI automated build and testing workflow. Code coverage is somewhat limited at present so we welcome improvements.

Please write unittest examples for new code you create and add them to the /tests folder following the naming convention test_*.py.

We test on the following platforms using u-blox [NEO-6](https://www.u-blox.com/en/product/neo-6-series), [NEO-7](https://www.u-blox.com/en/product/neo-7-series) and [NEO-8](https://www.u-blox.com/en/product/neo-m8-series) devices:
* Windows 10
* MacOS (Catalina)
* Linux (Ubuntu Bionic)
* Raspberry Pi OS (32-bit)

## Submitting changes

Please send a [GitHub Pull Request to PyGPSClient](https://github.com/semuconsulting/PyGPSClient/pulls) with a clear list of what you've done (read more about [pull requests](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-requests)). Please follow our coding conventions (below) and make sure all of your commits are atomic (one feature per commit).

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    > 
    > A paragraph describing what changed and its impact."



Thanks,

semuadmin