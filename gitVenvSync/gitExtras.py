from __future__ import annotations
import os
import stat
from .projectLogger import ProjectLogger
from typing import Optional
    

def getExistingRepository(repo_dir: os.path, username: str, repo_name: str, branch: str="main") -> Repo:
    from git import Repo, Head

    git_dir = os.path.join(repo_dir, ".git")
    if os.path.isdir(git_dir):
        repo = Repo(repo_dir)
        ProjectLogger.log(ProjectLogger.prefix.INFO, [f"Existing repository {repo.git.execute(['git', 'remote', 'show','origin']).splitlines()[1].strip().split(' ')[-1]} found."])

        current_branch = repo.active_branch.name
        if current_branch != branch:
            ProjectLogger.log(ProjectLogger.prefix.INFO, [f"Switching from branch {current_branch} to branch {branch}."])
            repo.git.reset('--hard')
            branch_reference = getattr(repo.remotes.origin.refs, branch)
            head: Head = repo.create_head(branch, branch_reference)
            head.set_tracking_branch(branch_reference)
            head.checkout(force=True) 
        
    else:
        if (username is None or repo_name is None):
            raise ValueError("A username and repo name must be provided to instantiate repositories")
            
        repo = Repo.init(repo_dir)
        remote = repo.create_remote("origin", getGitSSHUrl(username, repo_name))
        remote.fetch()

        branch_reference = getattr(remote.refs, branch)
        head: Head = repo.create_head(branch, branch_reference)
        head.set_tracking_branch(branch_reference)
        head.checkout(force=True) 
        ProjectLogger.log(ProjectLogger.prefix.INFO, [f"Repository {repo_name} created and connected on branch {branch}."])

    return repo


def updateRepository(repo: Repo, reset: bool, script: str=None, script_extension: str="") -> remote.FetchInfo:
    #from git import Repo, remote, Head
    from git.exc import GitCommandError

    origin = repo.remote(name="origin")
    try:
        if reset: repo.git.reset('--hard')
        fetch_info = origin.pull()
        
    except GitCommandError as error:
        message = f"An issue has occurred with the pull request for {next(repo.remote(name='origin').urls).split(':')[-1].strip('.git')}. Please resolve this before continuing."
        raise Exception(message) from error

    if len(fetch_info) > 0:
        return fetch_info[0]
    else:
        return None

def createExecutionScript(repo: Repo, script: str, script_extension: str=""):
    repo_name: str = repo.remotes.origin.url.split('.git')[0].split('/')[-1]
    path: str = f"{repo.working_dir}/{repo_name}.sh"
    if not os.path.exists(path):
        script_name: Optional[str] = None
        if os.path.exists(f"{repo.working_dir}/main{script_extension}"):
            script_name = f"main"
        elif os.path.exists(f"{repo.working_dir}/{repo_name}{script_extension}"):
            script_name = f"{repo_name}"
        
        if script_name is not None:
            with open(path, "w") as script_file:
                script = script.replace("{scriptname}", f"{script_name}")
                script_file.write(script)
            # Make executable by the user
            os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
            ProjectLogger.log(ProjectLogger.prefix.INFO, [f"Shell script {path} created."])
        else:
            ProjectLogger.log(ProjectLogger.prefix.INFO, [f"Shell script generation skipped, no entrypoint found."])


def wasRepoUpdated(fetch_info: remote.FetchInfo) -> bool:
    if fetch_info is None:
        return False
        
    ProjectLogger.log(ProjectLogger.prefix.INFO, [f"Flag: {fetch_info.flags}"])
    if fetch_info.flags == 4:
        return False
     
    return True


def addToFile(filename: str, input: list) -> list:
    if os.path.exists(filename) is False:
        with open(filename, "x") as file:
            pass

    with open(filename, "r") as file:
        file_content = file.read().strip()
    
    cleaned_input = []
    for item in input:
        if item not in file_content:
            cleaned_input.append(item)

    if len(cleaned_input) > 0:
        with open(filename, "a") as file:
            file.writelines(cleaned_input)
        
    return cleaned_input


def getGitSSHUrl(username: str, repo_name: str) -> str:
    return f"git@github.com:{username}/{repo_name}.git"
