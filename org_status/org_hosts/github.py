import json

import requests
from IGitt.GitHub.GitHub import GitHubToken
from IGitt.GitHub.GitHubOrganization import GitHubOrganization

from org_status.org_hosts import OrgHost, RepoStatus
from org_status.status_providers.travis import TravisBuildStatus
from org_status.status_providers.appveyor import AppVeyorStatus
from org_status.status_providers import Status


class GitHubOrg(OrgHost):
    HostName = 'github'
    StatusProvider = [TravisBuildStatus, AppVeyorStatus]

    def __init__(self, token, group, sync=True, **kargs):
        super().__init__(**kargs)

        self._group = group
        self._status_provider = []
        for i in enumerate(self.StatusProvider):
            self._status_provider.append(self.StatusProvider[i[0]](self._group))

        self._sync = sync
        if sync:
            self._token = GitHubToken(token)
            self._org = GitHubOrganization(self._token, self._group)

    @classmethod
    def get_host_status(cls):
        status = requests.get('https://status.github.com/api/status.json')
        status = json.loads(status.text)
        return status['status'] == 'good'

    def process_repository(self, web_url, branch='master'):
        self.print_status(web_url)

        # reliable enough?
        repo_name = web_url.split('/')[-1]
        repo_status = []
        for i in enumerate(self._status_provider):
            repo_status.append(self._status_provider[i[0]]
                               .get_status(repo_name,
                                           self.HostName,
                                           branch=branch))

        # if one result is passing, return that one
        if Status.PASSING in repo_status:
            repo_status = Status.PASSING
        # if statuses are identical, just return one of them
        elif repo_status[0] == repo_status[1]:
            repo_status = repo_status[0]
        # return the failing result out of the 2 results
        elif Status.FAILING in repo_status:
            repo_status = Status.FAILING
        # return the error result out of the 2 results
        elif Status.ERROR in repo_status:
            repo_status = Status.ERROR

        return RepoStatus(web_url, repo_status)

    @property
    def repositories(self):
        return [repo.web_url for repo in self._org.repositories]

    @property
    def sync(self):
        return self._sync
