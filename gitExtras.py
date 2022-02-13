from os import path
from git import Repo, remote
import globals
from gitVenvSync import projectLogger

def getExistingRepository(repo_dir: path, repo_name: str) -> Repo:
    git_dir = path.join(repo_dir, ".git")
    if path.isdir(git_dir):
        repo = Repo(repo_dir)
        projectLogger.log(projectLogger.prefix.INFO, [f"Exisitng repository {repo_name} found."])
    else:
        repo = Repo.init(repo_dir)
        remote = repo.create_remote("origin", getGitHttpsUrl(repo_name))
        remote.fetch()
        repo.create_head('main', remote.refs.main)  # create local branch "master" from remote "master"
        repo.heads.main.set_tracking_branch(remote.refs.main)  # set local "master" to track remote "master
        repo.heads.main.checkout() 
        projectLogger.log(projectLogger.prefix.INFO, [f"Repository {repo_name} created and connected."])

    return repo

def updateRepository(repo: Repo) -> remote.FetchInfo:
    origin = repo.remote(name="origin")
    return origin.pull()[0]

def wasRepoUpdated(fetch_info: remote.FetchInfo) -> bool:
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

def getGitHttpsUrl(repo_name: str) -> str:
    auth = "user:token"
    with open(globals.TOKENFILE, "r") as token_file:
        auth = token_file.read().strip()

    return f"https://{auth}@github.com/{auth.split(':')[0]}/{repo_name}"