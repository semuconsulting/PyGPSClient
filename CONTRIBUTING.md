# PyGPSClient How to contribute

PyGPSClient is a volunteer project and we appreciate any contribution, from fixing a grammar mistake in a comment to extending test coverage or implementing new functionality. Please read this section if you are contributing your work.

If you're intending to make significant changes, please raise them in the [Discussions Channel](https://github.com/semuconsulting/pygpsclient/discussions/categories/ideas) beforehand.

Being one of our contributors, you agree and confirm that:

* The work is all your own.
* Your work will be distributed under a BSD 3-Clause License once your pull request is merged.
* You submitted work fulfils or mostly fulfils our styles and standards.

Please help us keep our issue list small by adding fixes: #{$ISSUE_NO} to the commit message of pull requests that resolve open issues. GitHub will use this tag to auto close the issue when the PR is merged.

## Coding conventions

* This is open source software. Code should be as simple and transparent as possible. Favour clarity over brevity.
* The code should be compatible with Python >= 3.9 and tkinter >= 8.6.
* Avoid external library dependencies unless there's a compelling reason not to.
* We use and recommend [Visual Studio Code](https://code.visualstudio.com/) with the [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) for development and testing.
* Code should be documented in accordance with [Sphinx](https://www.sphinx-doc.org/en/master/) docstring conventions.
* Code should formatted using [black](https://pypi.org/project/black/) (>= 25.0.0).
* We use and recommend [pylint](https://pypi.org/project/pylint/) (>= 3.3.0) for code analysis.
* We use and recommend [bandit](https://pypi.org/project/bandit/) (>= 1.8.0) for security vulnerability analysis.
* Commits must be [signed](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits).

## Testing

While we endeavour to test on as wide a variety of u-blox devices and host platforms as possible, as a volunteer project we only have a limited number of devices available. We particularly welcome testing contributions relating to specialised devices (e.g. high precision HP, real-time kinematics RTK, Automotive Dead-Reckoning ADR, etc.).

We use Python's native unittest framework for local unit testing, complemented by the GitHub Actions automated build and testing workflow.

Please write unittest examples for new code you create and add them to the `/tests` folder following the naming convention `test_*.py`.

We test on the following host platforms using a variety of GNSS devices:

* Windows 11 (Intel and Snapdragon)
* MacOS (Sonoma & Sequoia, Intel and Apple Silicon)
* Linux (Ubuntu 24.04 LTS Numbat & 25.02 Puffin)
* Raspberry Pi OS (Bookworm 32-bit & 64-bit)

## Submitting changes

Please send a [GitHub Pull Request to PyGPSClient](https://github.com/semuconsulting/PyGPSClient/pulls) with a clear list of what you've done (read more about [pull requests](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-requests)). Please follow our coding conventions (below) and make sure all of your commits are atomic (one feature per commit).

Please use the supplied [Pull Request Template](https://github.com/semuconsulting/pygpsclient/blob/master/.github/pull_request_template.md).

Please sign all commits - see [Signing GitHub Commits](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits) for instructions.

Always write a clear log message for your commits. One-line messages are fine for small changes, but bigger changes should look like this:

    $ git commit -m "A brief summary of the commit
    > 
    > A paragraph describing what changed and its impact."



Thanks,

semuadmin