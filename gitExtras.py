import os
import git
import globals

def getExistingRepository(repo_dir: os.path, repo_name: str) -> git.Repo:
    git_dir = os.path.join(repo_dir, ".git")
    if os.path.isdir(git_dir):
        repo = git.Repo(repo_dir)
        print("Exisitng repository found.")
    else:
        repo = git.Repo.init(repo_dir)
        remote = repo.create_remote("origin", getGitHttpsUrl(repo_name))
        remote.fetch()
        repo.create_head('main', remote.refs.main)  # create local branch "master" from remote "master"
        repo.heads.main.set_tracking_branch(remote.refs.main)  # set local "master" to track remote "master
        repo.heads.main.checkout() 
        print("Repository created and connected.")

    return repo

def updateRepository(repo: git.Repo) -> list:
    origin = repo.remote(name="origin")
    return origin.pull()[0]

def wasRepoUpdated(fetch_info: git.remote.FetchInfo) -> bool:
    if fetch_info.flags == 4:
        return False
     
    return True

def getGitHttpsUrl(repo_name: str) -> str:
    auth = "user:token"
    with open(globals.TOKENFILE, "r") as token_file:
        auth = token_file.read().strip()

    return f"https://{auth}@github.com/{auth.split(':')[0]}/{repo_name}"