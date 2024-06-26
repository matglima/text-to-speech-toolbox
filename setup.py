import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install as _install

def read_requirements():
    with open('requirements.txt') as req_file:
        return req_file.readlines()

class post_install(_install):
    def run(self):
        _install.run(self)
        script_path = os.path.join(os.path.dirname(__file__), 'scripts/install_other_dependencies.sh')
        subprocess.check_call(['bash', script_path])

setup(
    name='text-to-speech-toolbox',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=read_requirements(),
    cmdclass={
        'install': post_install,
    },
)
