"""
    Module containing functions to deal with Git and Mercurial repositories.
    Useful for monitoring changes in a repository being able to apply custom filters
"""

import os
import re
import subprocess as sp
from pybliotecario.components.component_core import Component
import logging

log = logging.getLogger(__name__)

re_hg_branch = re.compile("(?<=branch:).*(?=\n)")
re_hg_user = re.compile("(?<=user:).*(?=<)")
re_hg_msg = re.compile("(?<=summary:).*(?=\n)")

re_git_user = re.compile("(?<=From:).*(?=<)")
re_git_msg = re.compile("(?<=Subject:).*(?=\n\n)")


def mercurial_incoming():
    """ Performs mercurial incoming and prettifies it """
    cmd = ["hg", "incoming"]
    cmd_ran = sp.run(cmd, stdout=sp.PIPE)
    out = cmd_ran.stdout
    changesets = out.decode().split("changeset")[1:]
    rev_dicts = []
    for rev in changesets:
        branch = re_hg_branch.search(rev).group().strip()
        user = re_hg_user.search(rev).group().strip()
        msg = re_hg_msg.search(rev).group().strip()
        rev_dicts.append({"branch": branch, "user": user, "msg": msg})
    return rev_dicts


def mercurial_pull():
    """ Performs mercurial pull """
    cmd = ["hg", "pull"]
    sp.run(cmd)


def git_incoming():
    """ Performs a hg incoming-like function using git own methods"""
    # TODO: use one of the git apis instead of this, but maybe this is the cleanest way to do it?
    cmd = ["git", "fetch"]
    sp.run(cmd)
    cmd = ["git", "log", "..origin/master", "--no-merges", "--format=email"]
    cmd_ran = sp.run(cmd, stdout=sp.PIPE)
    out = cmd_ran.stdout
    changesets = out.decode().split("changeset")[1:]
    msgs = re_git_msg.findall(changesets)
    users = re_git_user.findall(changesets)
    rev_dicts = []
    for msg_raw, user_raw in zip(msgs, users):
        msg = msg_raw.replace("[PATCH]", "").strip()
        user = user_raw.strip()
        branch = ""
        rev_dicts.append({"branch": branch, "user": user, "msg": msg})
    return rev_dicts


def git_pull():
    """ Performs git pull """
    cmd = ["git", "pull", "-f"]
    sp.run(cmd)


def repo_check_incoming(repo_path, max_log_n=4):
    """ Wrapper around git incoming / hg incoming """
    os.chdir(repo_path)
    if os.path.isdir(".hg"):
        commits = mercurial_incoming()
        mercurial_pull()
    elif os.path.isdir(".git"):
        commits = git_incoming()
        git_pull()

    n_commits = len(commits)
    repo_name = os.path.basename(repo_path)
    msg = "{0} new commits found in the {1} repository".format(n_commits, repo_name)
    if n_commits > max_log_n:
        msg += ", showing only the latest {0}".format(max_log_n)
    answer = [msg]
    for commit in commits[:max_log_n]:
        m = "\n > By {0}".format(commit["user"])
        if commit["branch"]:
            m += " in branch {0}".format(commit["branch"])
        m += ": " + commit["msg"]
        answer.append(m)
    return "\n".join(answer)


class Repository(Component):
    """
    Checks in the repository given
        in check_repository for new (i.e., not pulled)
        commits
    """

    def cmdline_command(self, args):
        repository = args.check_repository
        msg = repo_check_incoming(repository)
        self.send_msg(msg)
