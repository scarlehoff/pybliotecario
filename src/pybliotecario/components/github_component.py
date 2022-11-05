"""
    Wrapper around the GitHub API

    To get an API key go to 
    https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
    and follow the instructions
"""
import datetime
import github as pygithub

from pybliotecario.components.component_core import Component
import logging

log = logging.getLogger(__name__)


class Github(Component):
    """
    Checks what has happened in the given repository
    """

    key_name = "GITHUB"

    def __init__(self, telegram_object, configuration=None, **kwargs):
        super().__init__(telegram_object, configuration=configuration, **kwargs)
        if self.key_name in configuration:
            self.github_config = self.read_config_section(self.key_name)
        else:
            raise Exception("MAL")
        self._token = self.github_config.get("token", "")
        self._hours = int(self.github_config.get("since_hours", 2))
        self._github = None

    @property
    def github(self):
        if self._github is None:
            self._github = pygithub.Github(self._token)
        return self._github

    @classmethod
    def configure_me(cls):
        print("")
        print(" # Github module ")
        print("This is the configuration helper for the github module")
        print("Please introduce your access token: ")
        access_token = input(" > ")
        print("Show only the issues opened in the last X hours:")
        hours = None
        while hours is None:
            try:
                hours = int(input(" > "))
            except ValueError:
                print("Only integer numbers accepted")
        dict_out = {
            self.key_name: {
                "token": access_token,
                "since_hours": hours,
            }
        }
        return dict_out

    def _check_issues(self, repo_name):
        """Get the issues in the last two hours"""
        repo = self.github.get_repo(repo_name)
        since_datetime = datetime.datetime.now() - datetime.timedelta(hours=self._hours)
        all_issues = repo.get_issues(since=since_datetime)
        titles = []
        for issue in all_issues:
            if issue.created_at < since_datetime:
                continue
            pr = ""
            if issue.pull_request is not None:
                pr = "PR"
            url = f"https://github.com/{repo_name}/issues/{issue.number}"
            titles.append(f"    > {pr}#{issue.number}: [{issue.title}]({url})")
        if titles:
            self.send_msg(
                f"New github issues/PR in {repo_name}: \n" + "\n".join(titles),
                markdown=True,
            )

    def cmdline_command(self, args):
        repository = args.check_github_issues
        self._check_issues(repository)


if __name__ == "__main__":
    from pathlib import Path
    import tempfile
    import configparser
    from pybliotecario.pybliotecario import logger_setup, main
    from pybliotecario.backend import TestUtil

    tmpdir = Path(tempfile.mkdtemp())
    tmptxt = tmpdir / "text.txt"

    config = configparser.ConfigParser()
    config["DEFAULT"] = {
        "main_folder": tmpdir,
        "token": "AAAaaa123",
        "chat_id": 453,
    }
    config["GITHUB"] = {"token": "<TOKEN GITHUB>", "since_hours": 5}

    logger_setup(tmpdir / "log.txt", debug=True)

    log.info("Testing the github component")
    test_util = TestUtil(communication_file=tmptxt)
    args = ["--check_github_issues", "NNPDF/nnpdf"]
    main(cmdline_arg=args, tele_api=test_util, config=config)
    messages = tmptxt.read_text()
    print("Results: ")
    print(messages)
