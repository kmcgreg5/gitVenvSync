from os import path, system
from venv import EnvBuilder
from sys import base_prefix, prefix
from gitVenvSync import projectLogger
from shutil import rmtree
from pathlib import Path


class VenvException(Exception):
    def __init__(self, message = "A virtual environment should be used to run this program."):
        super().__init__(message)

    @staticmethod
    def notUsingVenv():
        if (base_prefix == prefix):
            raise VenvException()


def createVirtualEnvironment(repo_dir: path, force: bool):
    penv = Path(repo_dir) / "penv"

    if force is True and penv.is_dir():
        projectLogger.log(projectLogger.prefix.INFO, [f"Removing {repo_dir} python environment."])
        for file in penv.rglob("*"):
            if file.is_file():
                file.unlink()
        
        rmtree(penv)
        
    if penv.is_dir() is False:
        EnvBuilder(with_pip=True).create(penv)


def updateVirtualEnvironment(repo_dir: path, force: bool):
    pipreqs = path.join(repo_dir, "penv/bin/pipreqs")
    pip = path.join(repo_dir, "penv/bin/pip")

    if path.isfile(pipreqs) is False:
        projectLogger.log(projectLogger.prefix.MAINTANENCE, ["Installing pipreqs."])
        system(f"{pip} install pipreqs")
        print()

    with open(f"{repo_dir}/requirements.txt", 'r') as requirements:
        current_requirements = requirements.readlines()

    
    projectLogger.log(projectLogger.prefix.MAINTANENCE, [f"Updating {repo_dir}/requirements.txt..."])
    system(f"{pipreqs} --ignore code,penv --force {repo_dir}")
    print()
    if force is False:
        with open(f"{repo_dir}/requirements.txt", 'r') as requirements:
            new_requirements = requirements.read()

        with open(f"{repo_dir}/requirements.txt", 'a') as requirements:
            for line in current_requirements:
                line = line.strip()
                package = line.split('=')[0].replace('!', '').replace('>', '').replace('<', '').replace('~', '').strip()
                
                if package not in new_requirements:
                    requirements.write(f"{line}\n")



    projectLogger.log(projectLogger.prefix.MAINTANENCE, [f"Updating {repo_dir} virtual environment."])
    system(f"{pip} install -r {repo_dir}/requirements.txt")
    print()
