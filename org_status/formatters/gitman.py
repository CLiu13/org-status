import yaml
from giturlparse import parse

from org_status.formatters import RepoListFormatter


class GitManFormatter(RepoListFormatter):
    NAME = 'gitman'

    def encode_repo_list(self, urls):
        for url in urls:
            name = parse(url).repo
            yield {'name': name,
                   'repo': url,
                   'rev': 'master'}

    def decode_repo_list(self, file_name):
        with open(file_name, 'r') as file:
            yml_data = yaml.load(file)
            for repo in yml_data['sources']:
                yield [repo['name'], repo['repo']]
