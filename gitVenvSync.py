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
    
    if len(argv) > 5 or (len(argv) == 4 and argv[1] not in ['--force', '--clean', '--noreset', '--disable-env']) or (len(argv) == 5 and (argv[1] not in ['--force', '--clean', '--disable-env'] or argv[2] not in ['--noreset'])):
        projectLogger.log(projectLogger.prefix.ERROR, ["Usage: python gitVenvSync.py [--force|--clean|--disable-env] [--noreset] username repo-name"])
        return
    
    enclosing_repo = argv[0].replace(".py", "")
    code_repo = argv[-1] if len(argv) >= 3 else None
    username = argv[-2] if len(argv) >= 3 else None

    force = "--force" in argv
    clean = "--clean" in argv
    disable_env = "--disable-env" in argv
    reset = "--noreset" not in argv

    # Create or get and update the maintanence venv and throw an exception if a venv is not being used
    venvExtras.createVirtualEnvironment(getcwd(), False, False)
    venvExtras.updateVirtualEnvironment(getcwd(), False)
    venvExtras.VenvException.notUsingVenv()

    import gitExtras

    # Update the maintanence repo and restart if repo was updated
    repo = gitExtras.getExistingRepository(getcwd(), username, enclosing_repo)
    fetch_info = gitExtras.updateRepository(repo, True)

    gitignore = path.join(getcwd(), ".gitignore")
    return_list = gitExtras.addToFile(gitignore, ["penv/", "code/"])
    if len(return_list) > 0:
        projectLogger.log(projectLogger.prefix.MAINTANENCE, ["Added the following items to the .gitignore:", f"\t{return_list}"])

    if gitExtras.wasRepoUpdated(fetch_info):
        projectLogger.log(projectLogger.prefix.MAINTANENCE, ["Repo updated, restarting...\n"])
        execv(executable, ["python"] + argv)

    # Instantiate repository
    repo_dir = path.join(getcwd(), "code")
    repo = gitExtras.getExistingRepository(repo_dir, username, code_repo)
    gitExtras.updateRepository(repo, reset)

    if disable_env is False:
        gitignore = path.join(repo_dir, ".gitignore")
        return_list = gitExtras.addToFile(gitignore, ["penv/"])
        if len(return_list) > 0:
            projectLogger.log(projectLogger.prefix.MAINTANENCE, ["Added the following items to the git ignore:", f"\t{return_list}"])
            repo.index.add([".gitignore"])

    # Instantiate and update python venv
    if disable_env is False:
        venvExtras.createVirtualEnvironment(repo_dir, force, clean)
        venvExtras.updateVirtualEnvironment(repo_dir, force)
    else:
        projectLogger.log(projectLogger.prefix.INFO, ["Code virtual environment creation is disabled, skipping..."])
    

if __name__ == "__main__":
    main()
