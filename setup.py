import os
import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install as _install

def read_requirements():
    with open('requirements.txt') as req_file:
        return req_file.read().splitlines()

class PostInstallCommand(_install):
    """Post-installation for installation mode."""
    def run(self):
        _install.run(self)
        # Manually install requirements to ensure correct order
        requirements = read_requirements()
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + requirements)
        # Run the post-install script
        script_path = os.path.join(os.path.dirname(__file__), 'scripts/install_other_dependencies.sh')
        subprocess.check_call(['bash', script_path])

setup(
    name='text-to-speech-toolbox',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=read_requirements(),
    cmdclass={
        'install': PostInstallCommand,
    },
)
