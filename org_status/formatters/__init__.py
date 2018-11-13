class RepoListFormatter:
    NAME = None

    def encode_repo_list(self, repos):
        raise NotImplementedError()

    def decode_repo_list(self, file_name):
        raise NotImplementedError()


def get_all_supported_formatters():
    from org_status.formatters.gitman import GitManFormatter
    from org_status.formatters.gitshelf import GitShelfFormatter

    return (
        GitManFormatter,
        GitShelfFormatter,
    )
