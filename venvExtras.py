from os import path, system
from venv import EnvBuilder
from sys import base_prefix, prefix
from gitVenvSync import projectLogger


class VenvException(Exception):
    def __init__(self, message = "A virtual environment should be used to run this program."):
        super().__init__(message)

    @staticmethod
    def notUsingVenv():
        if (base_prefix == prefix):
            raise VenvException()


def createVirtualEnvironment(repo_dir: path):
    penv = path.join(repo_dir, "penv")
    if path.isdir(penv) is False:
        EnvBuilder(with_pip=True).create(penv)


def updateVirtualEnvironment(repo_dir: path):
    pipreqs = path.join(repo_dir, "penv/bin/pipreqs")
    pip = path.join(repo_dir, "penv/bin/pip")

    if path.isfile(pipreqs) is False:
        projectLogger.log(projectLogger.prefix.MAINTANENCE, ["Installing pipreqs."])
        system(f"{pip} install pipreqs")
        print()

    projectLogger.log(projectLogger.prefix.MAINTANENCE, [f"Updating {repo_dir}/requirements.txt..."])
    system(f"{pipreqs} --ignore code,penv --force {repo_dir}")
    print()

    projectLogger.log(projectLogger.prefix.MAINTANENCE, [f"Updating {repo_dir} virtual environment."])
    system(f"{pip} install -r {repo_dir}/requirements.txt")
    print()
