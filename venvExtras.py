import os
import venv
import sys

class VenvException(Exception):
    def __init__(self, message = "A virtual environment should be used to run this program."):
        super().__init__(message)

    @staticmethod
    def notUsingVenv():
        if (sys.base_prefix == sys.prefix):
            raise VenvException()

def createVirtualEnvironment(repo_dir: os.path):
    penv = os.path.join(repo_dir, "penv")
    if os.path.isdir(penv) is False:
        venv.EnvBuilder(with_pip=True).create(penv)

def updateVirtualEnvironment(repo_dir: os.path):
    pipreqs = os.path.join(repo_dir, "penv/bin/pipreqs")
    pip = os.path.join(repo_dir, "penv/bin/pip")

    if os.path.isfile(pipreqs) is False:
        os.system(f"{pip} install pipreqs")
        print()

    os.system(f"{pipreqs} --ignore code,penv --force {repo_dir}")
    print()

    os.system(f"{pip} install -r requirements.txt")
    print()
