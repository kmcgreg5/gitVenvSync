import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from gitVenvSync.projectLogger import ProjectLogger
from gitVenvSync import venvExtras
from typing import Optional

    
def main(args: list=sys.argv[1:]):
    # Ensure command line argument complience
    parser = ArgumentParser(prog="git-venv-sync")
    parser.add_argument("username", help="The GitHub username.")
    parser.add_argument("reponame", help="The GitHub repository name.")
    parser.add_argument("--branch", default="main", help="The repo branch to sync.")
    parser.add_argument("--no-reset", action="store_true", help="Disables the hard reset applied to the repo before updating.")
    parser.add_argument("--script-template", default=None, help="A path to a script file to use as a template.")

    venv_options = parser.add_mutually_exclusive_group()
    venv_options.add_argument("--force", action="store_true", help="Recreates the repos virtual environment from only the generated and local requirements.")
    venv_options.add_argument("--clean", action="store_true", help="Recreates the repos virtual environment.")
    venv_options.add_argument("--disable-env", action="store_true", help="Disables the repos virtual environment.")

    args = parser.parse_args(args)
    
    code_repo: str = args.reponame
    username: str = args.username
    branch: str = args.branch

    force: bool = args.force
    clean: bool = args.clean
    disable_env: bool = args.disable_env
    reset: bool = args.no_reset is False
    script_template: Optional[str] = args.script_template

    # Create or get and update the maintanence venv and throw an exception if a venv is not being used
    maintanence_dir = Path(__file__).resolve().parent
    venvExtras.createVirtualEnvironment(maintanence_dir, False, False)
    venvExtras.updateVirtualEnvironment(maintanence_dir, "kmcgreg5", False)
    venvExtras.VenvException.notUsingVenv()

    from gitVenvSync import gitExtras

    # Update the maintanence repo and restart if repo was updated
    repo = gitExtras.getExistingRepository(maintanence_dir, "kmcgreg5", "gitVenvSync")
    fetch_info = gitExtras.updateRepository(repo, True)

    gitignore = os.path.join(maintanence_dir, ".gitignore")
    return_list = gitExtras.addToFile(gitignore, ["penv/", "code/"])
    if len(return_list) > 0:
        ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, ["Added the following items to the .gitignore:", f"\t{return_list}"])

    if gitExtras.wasRepoUpdated(fetch_info):
        ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, ["Repo updated, restarting...\n"])
        os.execv(sys.executable, ["python"] + sys.argv)

    # Instantiate repository
    repo_dir = os.path.join(os.getcwd(), "code") if os.getcwd() == maintanence_dir else os.getcwd()
    repo = gitExtras.getExistingRepository(repo_dir, username, code_repo, branch)
    gitExtras.updateRepository(repo, reset, __default_script_text(script_template))

    if disable_env is False:
        gitignore = os.path.join(repo_dir, ".gitignore")
        return_list = gitExtras.addToFile(gitignore, ["penv/"])
        if len(return_list) > 0:
            ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, ["Added the following items to the git ignore:", f"\t{return_list}"])
            repo.index.add([".gitignore"])

    # Instantiate and update python venv
    if disable_env is False:
        venvExtras.createVirtualEnvironment(repo_dir, force, clean)
        venvExtras.updateVirtualEnvironment(repo_dir, username, force)
    else:
        ProjectLogger.log(ProjectLogger.prefix.INFO, ["Code virtual environment creation is disabled, skipping..."])
    
def __default_script_text(disable_env: bool, file: str=None) -> str:
    if file is not None:
        with open(file, "r") as script_template:
            return script_template.read()
    
    
    return '''script_dir=$(dirname "$0")

if [ $script_dir = '.' ]
then
    script_dir=$(pwd)
fi

source "$script_dir/penv/bin/activate"
python "$script_dir/{scriptname}" "$@"
deactivate
'''

if __name__ == "__main__":
    main()
