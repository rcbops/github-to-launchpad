#!/usr/bin/env python
# 3rd party
import argparse
import getpass

import github3
from launchpadlib import errors as lperrors
from launchpadlib import launchpad

try:
    input_func = raw_input
except NameError: # Python 3.x
    input_func = input


TEMPLATE = """Opened by {username} on {date} at {github_url}

------------------------------------------------------------

{issue_body}

Tags: {issue_tags}
"""


def make_description_from(issue):
    values = {
        'date': str(issue.created_at),
        'username': str(issue.user),
        'github_url': issue.html_url,
        'issue_body': issue.body_text,
        'issue_tags': ', '.join(str(l) for l in issue.labels),
        }
    return TEMPLATE.format(values)


class MigrationAssistant(object):
    def __init__(self):
        self.launchpad = None
        self.github = None
        self.repository = None
        self.distribution = None

    def _issues(self, state, direction='asc'):
        return self.repository.iter_issues(state=state,
                                           direction=direction)

    def _migrate(self, state):
        for issue in self._issues(state):
            title = issue.title
            description = make_description_from(issue)
            yield issue, self._create_lp_bug(title, description)

    def _create_lp_bug(self, title, description):
        # Use self.launchpad, self.distribution
        bugs = self.launchpad.bugs
        try:
            bug = bugs.createBug(title=title,
                                 description=description,
                                 target=self.distribution,
                                 private=False)
        except lperrors.HTTPError:
            bug = None
        return bug

    def login_to_github(self, username, password):
        self.github = github3.login(username, password)
        self.github.set_user_agent('github-issues-to-launchpad v0.0.0')

    def login_to_launchpad(self, auth_name='github-to-lp', env='production'):
        self.launchpad = launchpad.Launchpad.login_with(auth_name, env)

    def migrate_issues(self, from_repository, to_distribution, state='open'):
        self.distribution = self.launchpad.distributions[to_distribution]
        owner, repo = from_repository.split('/')
        self.repository = self.github.repository(owner, repo)
        for gh_issue, lp_bug in self._migrate(state):
            if lp_bug is not None:
                print("Migrating GH#{0} to {1}".format(gh_issue.number,
                                                       lp_bug.web_link))
            else:
                print("Could not create bug on LaunchPad for {0}".format(
                    gh_issue.html_url
                    ))


def get_username_and_password():
    def prompt_for_input(prompt_str, secure=True):
        prompt = getpass.getpass if secure else input_func
        input_str = ''

        while not input_str:
            input_str = prompt(prompt_str)

        return input_str

    return (prompt_for_input('Enter your GitHub username: '),
            prompt_for_input('Enter your GitHub password: '))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'from_repository',
        description='Repository on GitHub to transfer issues from. Example: '
                    'rcbops/ansible-lxc-rpc'
        )
    parser.add_argument(
        'to_distribution',
        description='The distribution name on LaunchPad. Example: '
                    'openstack-ansible'
        )
    parser.add_argument(
        '--state',
        description='State in which issues should be in to be moved. '
                    'Accepted values: open, closed, all',
        default='open'
        )
    return parser.parse_args()


def main():
    args = parse_args()
    m = MigrationAssistant()
    (user, password) = get_username_and_password()
    m.login_to_github(user, password)
    m.login_to_launchpad()
    m.migrate_issues(args.from_repository, args.to_distribution, args.state)
