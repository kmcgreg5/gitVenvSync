from os import path
from git import Repo, remote
from gitVenvSync import projectLogger
from git.exc import GitCommandError


def getExistingRepository(repo_dir: path, username: str, repo_name: str) -> Repo:
    git_dir = path.join(repo_dir, ".git")
    if path.isdir(git_dir):
        repo = Repo(repo_dir)
        projectLogger.log(projectLogger.prefix.INFO, [f"Existing repository {next(repo.remote(name='origin').urls).split(':')[-1].strip('.git')} found."])
    else:
        if (username is None or repo_name is None):
            raise ValueError("A username and repo name must be provided to instantiate repositories")
            
        repo = Repo.init(repo_dir)
        remote = repo.create_remote("origin", getGitSSHUrl(username, repo_name))
        remote.fetch()
        repo.create_head('main', remote.refs.main)
        repo.heads.main.set_tracking_branch(remote.refs.main)
        repo.heads.main.checkout(force=True) 
        projectLogger.log(projectLogger.prefix.INFO, [f"Repository {repo_name} created and connected."])

    return repo


def updateRepository(repo: Repo) -> remote.FetchInfo:
    origin = repo.remote(name="origin")
    try:
        repo.git.reset('--hard')
        fetch_info = origin.pull()
        
    except GitCommandError as error:
        message = f"An issue has occurred with the pull request for {next(repo.remote(name='origin').urls).split(':')[-1].strip('.git')}. Please resolve this before continuing."
        raise Exception(message) from error
    
    if len(fetch_info) > 0:
        return fetch_info[0]
    else:
        return None


def wasRepoUpdated(fetch_info: remote.FetchInfo) -> bool:
    if fetch_info is None:
        return False
        
    projectLogger.log(projectLogger.prefix.INFO, [f"Flag: {fetch_info.flags}"])
    if fetch_info.flags == 4:
        return False
     
    return True


def addToFile(filename: path, input: list) -> list:
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
