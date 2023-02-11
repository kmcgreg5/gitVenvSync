import os
import sys
import shutil
from venv import EnvBuilder
from .projectLogger import ProjectLogger
from pathlib import Path
from tempfile import TemporaryDirectory

class VenvException(Exception):
    def __init__(self, message = "A virtual environment should be used to run this program."):
        super().__init__(message)

    @staticmethod
    def notUsingVenv():
        def is_venv() -> bool:
            return (hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
        if is_venv() is False:
            raise VenvException()


def createVirtualEnvironment(repo_dir: os.path, force: bool, clean: bool):
    penv = Path(repo_dir) / "penv"

    if (force is True or clean is True) and penv.is_dir():
        ProjectLogger.log(ProjectLogger.prefix.INFO, [f"Removing {repo_dir} python environment."])
        for file in penv.rglob("*"):
            if file.is_file():
                file.unlink()
        
        shutil.rmtree(penv)
        
    if penv.is_dir() is False:
        EnvBuilder(with_pip=True).create(penv)


def updateVirtualEnvironment(repo_dir: os.path, username: str, force: bool):
    pipreqs = os.path.join(repo_dir, "penv/bin/pipreqs")
    pip = os.path.join(repo_dir, "penv/bin/pip")

    ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, ["Updating pip."])
    os.system(f"{pip} install --upgrade --quiet pip")

    if os.path.isfile(pipreqs) is False:
        ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, ["Installing pipreqs."])
        os.system(f"{pip} install --quiet pipreqs")
        print()

    old_requirements = read_requirements(f"{repo_dir}/requirements.txt")

    ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, [f"Updating {repo_dir}/requirements.txt..."])
    os.system(f"{pipreqs} --ignore code,penv --force {repo_dir}")
    print()

    # Read new requirements
    new_requirements = read_requirements(f"{repo_dir}/requirements.txt")

    local_requirements, added_requirements = parse_requirements(old_requirements, new_requirements)   

    if force is False:
        with open(f"{repo_dir}/requirements.txt", 'a') as requirements:
            for requirement in added_requirements:
                requirements.write(requirement)

    ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, [f"Updating {repo_dir} virtual environment."])
    os.system(f"{pip} install -q -r {repo_dir}/requirements.txt")
    print()

    if len(local_requirements) != 0:
        ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, [f"Installing {repo_dir} local dependencies."])
        # Import here to avoid dependency clashes when creating a new virtual environment
        from .gitExtras import getExistingRepository
        for requirement in local_requirements:
            with TemporaryDirectory() as temp_dir:
                temp_repo: str = f"{temp_dir}/{requirement['name']}"
                temp_dir_path = str(temp_dir) # copy to avoid overwriting the variable
                # __init__.py indicates a top level package
                if os.path.exists(f"{temp_repo}/__init__.py"):
                    temp_dir_path = temp_repo
                getExistingRepository(temp_repo, username, requirement["name"], requirement["branch"])

                temp_old_reqs = read_requirements(f"{temp_repo}/requirements.txt")

                ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, [f"Updating {temp_repo}/requirements.txt..."])
                os.system(f"{pipreqs} --ignore code,penv --force {temp_repo}")
                print()

                temp_new_reqs = read_requirements(f"{temp_repo}/requirements.txt")
                temp_local_reqs, temp_added_reqs = parse_requirements(temp_old_reqs, temp_new_reqs)
                with open(f"{temp_dir_path}/generated-requirements.txt", "w") as requirements:
                    for temp_req in temp_new_reqs:
                        requirements.write(temp_req)
                    for temp_req in temp_added_reqs:
                        requirements.write(temp_req)
                    for temp_req in temp_local_reqs:
                        requirements.write(f"{temp_req['name']}=={temp_req['branch']}\n")

                if temp_repo != temp_dir_path:
                    os.rename(f"{temp_repo}/pyproject.toml", f"{temp_dir_path}/pyproject.toml")
                    os.rename(f"{temp_repo}/README.md", f"{temp_dir_path}/README.md")

                os.system(f"{pip} install -q {temp_dir_path}")
                with open(f"{repo_dir}/requirements.txt", 'a') as requirements:
                    requirements.write(f"{requirement['line']}\n")


def read_requirements(requirements_file: str) -> list[str]:
    if os.path.exists(requirements_file):
        with open(requirements_file, 'r') as requirements:
            return requirements.readlines()
    
    return []


def parse_requirements(old_requirements: list[str], new_requirements:list[str]) -> tuple[list[dict], list[str]]:
    def get_package(line: str) -> str:
        return line.split('=')[0].replace('!', '').replace('>', '').replace('<', '').replace('~', '').strip()

    new_packages = []
    for line in new_requirements:
        line = line.strip()
        if (line) == 0: continue
        if line[0] == "#": continue
        new_packages.append(get_package(line))

    # Parse requirements
    local_requirements: list = []
    added_requirements: list = []
    for line in old_requirements:
        line = line.strip()
        if len(line) == 0: continue
        package = get_package(line)
        # Identify local packages
        if package == "#local":
            name: str = line.split("==")[1]
            branch: str = line.split("==")[2]
            local_requirements.append({"name":name, "branch":branch, "line":line})
        elif package not in new_packages and package[0] != "#": # Identify additional requirements
            added_requirements.append(f"{line}\n")
    
    return local_requirements, added_requirements
                    