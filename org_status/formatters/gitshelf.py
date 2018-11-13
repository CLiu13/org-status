import yaml
from giturlparse import parse

from org_status.formatters import RepoListFormatter


class GitShelfFormatter(RepoListFormatter):
    NAME = 'gitshelf'

    def encode_repo_list(self, urls):
        for url in urls:
            name = parse(url).repo
            yield {'book': name,
                   'git': url,
                   'branch': 'master'}

    def decode_repo_list(self, file_name):
        with open(file_name, 'r') as file:
            yml_data = yaml.load(file)
            for repo in yml_data['books']:
                yield [repo['book'], repo['git']]
