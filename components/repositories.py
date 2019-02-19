import os
import re
import subprocess as sp
import pdb

re_hg_branch = re.compile('(?<=branch:).*(?=\n)')
re_hg_user = re.compile('(?<=user:).*(?=<)')
re_hg_msg = re.compile('(?<=summary:).*(?=\n)')

re_git_user = re.compile('(?<=From:).*(?=<)')
re_git_msg = re.compile('(?<=Subject:).*(?=\n\n)')

def mercurial_incoming():
    cmd = ['hg', 'incoming']
    out = sp.run(cmd, capture_output = True)
    changesets = out.stdout.decode().split('changeset')[1:]
    rev_dicts = []
    for rev in changesets:
        branch = re_hg_branch.search(rev)[0].strip()
        user = re_hg_user.search(rev)[0].strip()
        msg = re_hg_msg.search(rev)[0].strip()
        rev_dicts.append( {'branch' : branch, 'user' : user, 'msg' : msg} )
    return rev_dicts

def mercurial_pull():
    cmd = ['hg', 'pull']
    out = sp.run(cmd)

def git_incoming():
    # TODO: use one of the git apis instead of this, but maybe this is the cleanest way to do it?
    cmd = ["git", "fetch"]
    sp.run(cmd)
    cmd = ["git", "log", "..origin/master", "--no-merges", "--format=email" ]
    out = sp.run(cmd, capture_output = True)
    changesets = out.stdout.decode() 
    msgs = re_git_msg.findall(changesets)
    users = re_git_user.findall(changesets)
    rev_dicts = []
    for msg_raw, user_raw in zip(msgs, users):
        msg = msg_raw.replace("[PATCH]", "").strip()
        user = user_raw.strip()
        branch = ""
        rev_dicts.append( {'branch' : branch, 'user' : user, 'msg' : msg} )
    return rev_dicts

def git_pull():
    cmd = ['git', 'pull', '-f']
    out = sp.run(cmd)

def repo_check_incoming(repo_path, max_print = 4):
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
    if n_commits > max_print:
        msg += ", showing only the latest {0}".format(max_print)
    answer = [msg]
    for commit in commits[:max_print]:
        m = "\n > By {0}".format(commit['user'])
        if commit['branch']:
            m += " in branch {0}".format(commit['branch'])
        m += ": " + commit['msg']
        answer.append(m)
    return "\n".join(answer)

