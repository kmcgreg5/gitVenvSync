import os
import sys
import venvExtras

def main():
    # Ensure command line argument complience
    if len(sys.argv) != 2:
        print("Usage: python gitVenvSync.py repo-name")
        return

    # Create or get and update the maintanence venv and throw an exception if a venv is not being used
    venvExtras.createVirtualEnvironment(os.getcwd())
    venvExtras.updateVirtualEnvironment(os.getcwd())
    venvExtras.VenvException.notUsingVenv()

    import gitExtras

    # Update the maintanence repo and restart if repo was updated
    repo = gitExtras.getExistingRepository(os.getcwd(), sys.argv[0].replace(".py", ""))
    fetch_info = gitExtras.updateRepository(repo)
    if gitExtras.wasRepoUpdated(fetch_info):
        print("\nRepo updated, restarting...\n")
        os.execv(sys.executable, ["python"] + sys.argv)

    # Instantiate repository
    repo_dir = os.path.join(os.getcwd(), "code")
    repo = gitExtras.getExistingRepository(repo_dir, sys.argv[1])
    gitExtras.updateRepository(repo)

    # Instantiate and update python venv
    venvExtras.createVirtualEnvironment(repo_dir)
    venvExtras.updateVirtualEnvironment(repo_dir)
    

if __name__ == "__main__":
    main()