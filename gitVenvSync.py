from os import getcwd, path, execv
from sys import argv, executable
import venvExtras

def main():
    # Ensure command line argument complience
    if len(argv) != 2:
        print("Usage: python gitVenvSync.py repo-name")
        return

    # Create or get and update the maintanence venv and throw an exception if a venv is not being used
    venvExtras.createVirtualEnvironment(getcwd())
    venvExtras.updateVirtualEnvironment(getcwd())
    venvExtras.VenvException.notUsingVenv()

    import gitExtras

    # Update the maintanence repo and restart if repo was updated
    repo = gitExtras.getExistingRepository(getcwd(), argv[0].replace(".py", ""))
    fetch_info = gitExtras.updateRepository(repo)
    if gitExtras.wasRepoUpdated(fetch_info):
        print("\nRepo updated, restarting...\n")
        execv(executable, ["python"] + argv)

    # Instantiate repository
    repo_dir = path.join(getcwd(), "code")
    repo = gitExtras.getExistingRepository(repo_dir, argv[1])
    gitExtras.updateRepository(repo)

    # Instantiate and update python venv
    venvExtras.createVirtualEnvironment(repo_dir)
    venvExtras.updateVirtualEnvironment(repo_dir)
    

if __name__ == "__main__":
    main()