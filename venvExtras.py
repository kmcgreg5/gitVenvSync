from os import path, system
from venv import EnvBuilder
from sys import base_prefix, prefix
from gitVenvSync import ProjectLogger
from shutil import rmtree
from pathlib import Path
from tempfile import TemporaryDirectory

class VenvException(Exception):
    def __init__(self, message = "A virtual environment should be used to run this program."):
        super().__init__(message)

    @staticmethod
    def notUsingVenv():
        if (base_prefix == prefix):
            raise VenvException()


def createVirtualEnvironment(repo_dir: path, force: bool, clean: bool):
    penv = Path(repo_dir) / "penv"

    if (force is True or clean is True) and penv.is_dir():
        ProjectLogger.log(ProjectLogger.prefix.INFO, [f"Removing {repo_dir} python environment."])
        for file in penv.rglob("*"):
            if file.is_file():
                file.unlink()
        
        rmtree(penv)
        
    if penv.is_dir() is False:
        EnvBuilder(with_pip=True).create(penv)


def updateVirtualEnvironment(repo_dir: path, username: str, force: bool):
    pipreqs = path.join(repo_dir, "penv/bin/pipreqs")
    pip = path.join(repo_dir, "penv/bin/pip")

    ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, ["Updating pip."])
    system(f"{pip} install --upgrade --quiet pip")

    if path.isfile(pipreqs) is False:
        ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, ["Installing pipreqs."])
        system(f"{pip} install --quiet pipreqs")
        print()

    old_requirements = read_requirements(f"{repo_dir}/requirements.txt")

    ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, [f"Updating {repo_dir}/requirements.txt..."])
    system(f"{pipreqs} --ignore code,penv --force {repo_dir}")
    print()

    # Read new requirements
    new_requirements = read_requirements(f"{repo_dir}/requirements.txt")

    local_requirements, added_requirements = parse_requirements(old_requirements, new_requirements)   

    if force is False:
        with open(f"{repo_dir}/requirements.txt", 'a') as requirements:
            for requirement in added_requirements:
                requirements.write(requirement)

    ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, [f"Updating {repo_dir} virtual environment."])
    system(f"{pip} install -q -r {repo_dir}/requirements.txt")
    print()

    if len(local_requirements) != 0:
        ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, [f"Installing {repo_dir} local dependencies."])
        # Import here to avoid dependency clashes when creating a new virtual environment
        import gitExtras
        for requirement in local_requirements:
            with TemporaryDirectory() as temp_repo:
                gitExtras.getExistingRepository(temp_repo, username, requirement["name"])

                temp_old_reqs = read_requirements(f"{temp_repo}/requirements.txt")

                ProjectLogger.log(ProjectLogger.prefix.MAINTANENCE, [f"Updating {temp_repo}/requirements.txt..."])
                system(f"{pipreqs} --ignore code,penv --force {temp_repo}")
                print()

                temp_new_reqs = read_requirements(f"{temp_repo}/requirements.txt")
                temp_local_reqs, temp_added_reqs = parse_requirements(temp_old_reqs, temp_new_reqs)
                with open(f"{temp_repo}/generated-requirements.txt", "w") as requirements:
                    for temp_req in temp_new_reqs:
                        requirements.write(temp_req)
                    for temp_req in temp_added_reqs:
                        requirements.write(temp_req)
                    for temp_req in temp_local_reqs:
                        requirements.write(f"{temp_req['name']}=={temp_req['version']}\n")


                system(f"{pip} install -q {temp_repo}")
                with open(f"{repo_dir}/requirements.txt", 'a') as requirements:
                    requirements.write(f"{requirement['line']}\n")

def read_requirements(requirements_file: str) -> list[str]:
    if path.exists(requirements_file):
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
            version: str = line.split("==")[2]
            local_requirements.append({"name":name, "version":version, "line":line})
        elif package not in new_requirements and package[0] != "#": # Identify additional requirements
            added_requirements.append(f"{line}\n")
    
    return local_requirements, added_requirements
                    