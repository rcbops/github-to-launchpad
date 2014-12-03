GitHub to LaunchPad Issue Migration Tool
========================================

This is a tool to migrate issues from a GitHub repository to a launchpad 
project.

Contributing
------------

For development::

    $ mkvirtualenv $(virtualenv_name)
    $ pip install --allow-unverified lazr.authentication -r dev-requirements.txt

If you're working on Python 2.6 you'll also need to install ``argparse``.

Usage
-----

::

    $ python github-to-lp.py user/repo launchpad-project
    $ python github-to-lp.py --state=all user/repo launchpad-project
