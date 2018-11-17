import pytest
from unittest import mock
from io import StringIO

from argparse import ArgumentParser

from org_status.org_status import (get_argument_parser,
                                   generate_fetch_jobs,
                                   get_host_token,
                                   get_supported_status_providers,
                                   get_status_provider_statuses,
                                   present_status,
                                   )
from org_status.org_hosts import get_all_supported_hosts


def test_get_argument_parser():
    assert isinstance(get_argument_parser(), ArgumentParser)


def test_generate_fetch_jobs():
    for host in get_all_supported_hosts():
        assert next(
            generate_fetch_jobs(
                [f'{host.HostName}:coala'])) == (host, 'coala')

        with pytest.raises(ValueError):
            next(generate_fetch_jobs(['github:']))

        with pytest.raises(StopIteration):
            next(generate_fetch_jobs([]))

    # test passing in only organization name
    actual_fetch_jobs = set(generate_fetch_jobs(['templetonrobotics7190']))
    expected_fetch_jobs = {(host, 'templetonrobotics7190') for host in
                           get_all_supported_hosts()}
    assert expected_fetch_jobs == actual_fetch_jobs


def test_get_host_token():
    with mock.patch.dict('org_status.org_status.environ',
                         {'GITHUB_TOKEN': 'kaichen123',
                          'GITLAB_TOKEN': 'kaichen321'}):
        assert get_host_token('github') == 'kaichen123'
        assert get_host_token('gitlab') == 'kaichen321'
        with pytest.raises(KeyError):
            get_host_token('something_else')


def test_get_status_provider_statuses():
    actual_status_provider_statuses = set(get_status_provider_statuses())
    expected_status_provider_statuses = set()

    for status_provider in get_supported_status_providers():
        try:
            status = status_provider.get_status_provider_status()
        except NotImplementedError:
            status = None
        expected_status_provider_statuses.add((status_provider, status))

    assert actual_status_provider_statuses == expected_status_provider_statuses


class MockRepoStatus():
    def __init__(self, value):
        self.value = value


class MockStatus():
    def __init__(self, repo_url, repo_status, last_commit_date):
        self.repo_url = repo_url
        self.repo_status = MockRepoStatus(repo_status)
        self.last_commit_date = last_commit_date


def test_present_status():
    statuses = [MockStatus('https://github.com/foo/r0',
                           'passing', '2018-11-05T08:20:37Z'),
                MockStatus('https://github.com/foo/r1',
                           'passing', '2018-11-02T17:31:46Z'),
                MockStatus('https://github.com/foo/r2',
                           'passing', '2018-11-06T02:27:42Z')]

    with mock.patch('sys.stdout', new=StringIO()) as output:
        present_status(statuses, True, False)
        actual = output.getvalue().strip()
        with open('tests/fixtures/present_status_output_no_sort.txt', 'r') as f:
            expected = f.read()
        assert actual == expected

    with mock.patch('sys.stdout', new=StringIO()) as output:
        present_status(statuses, True, True)
        actual = output.getvalue().strip()
        with open('tests/fixtures/present_status_output_sorted.txt', 'r') as f:
            expected = f.read()
        assert actual == expected
