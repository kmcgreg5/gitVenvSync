from os import getcwd, path, execv
from sys import argv, executable, exit
from enum import Enum
import venvExtras


class projectLogger:
    class prefix(Enum):
        WARNING = "WARNING"
        MAINTANENCE = "MAINTANENCE"
        ERROR = "ERROR"
        INFO = "INFO"
    
    @staticmethod
    def log(used_prefix: prefix, lines: list, status = None):
        for line in lines:
            print(f"[{used_prefix.value}] {line}")

    


def main():
    # Ensure command line argument complience
    if len(argv) != 2:
        projectLogger.log(projectLogger.prefix.ERROR, ["Usage: python gitVenvSync.py repo-name"])
        return

    # Create or get and update the maintanence venv and throw an exception if a venv is not being used
    venvExtras.createVirtualEnvironment(getcwd())
    venvExtras.updateVirtualEnvironment(getcwd())
    venvExtras.VenvException.notUsingVenv()

    import gitExtras

    # Update the maintanence repo and restart if repo was updated
    repo = gitExtras.getExistingRepository(getcwd(), argv[0].replace(".py", ""))
    fetch_info = gitExtras.updateRepository(repo)

    gitignore = path.join(getcwd(), ".gitignore")
    return_list = gitExtras.addToFile(gitignore, ["*.token", "penv/", "code/"])
    if len(return_list) > 0:
        projectLogger.log(projectLogger.prefix.MAINTANENCE, ["Added the following items to the .gitignore:", f"\t{return_list}"])

    if gitExtras.wasRepoUpdated(fetch_info):
        projectLogger.log(projectLogger.prefix.MAINTANENCE, ["Repo updated, restarting...\n"])
        exit()
        execv(executable, ["python"] + argv)

    exit()

    projectLogger.log(projectLogger.prefix.INFO, ["Before"])

    # Instantiate repository
    repo_dir = path.join(getcwd(), "code")
    repo = gitExtras.getExistingRepository(repo_dir, argv[1])
    gitExtras.updateRepository(repo)

    gitignore = path.join(repo_dir, ".gitignore")
    return_list = gitExtras.addToFile(gitignore, ["penv/"])
    if len(return_list) > 0:
        projectLogger.log(projectLogger.prefix.MAINTANENCE, ["Added the following items to the git ignore:", f"\t{return_list}"])
        repo.index.add([".gitignore"])

    # Instantiate and update python venv
    venvExtras.createVirtualEnvironment(repo_dir)
    venvExtras.updateVirtualEnvironment(repo_dir)
    

if __name__ == "__main__":
    main()
