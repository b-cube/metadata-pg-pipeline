from setuptools import setup, find_packages
import semproc
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

readme = open('README.md').read()
reqs = [line.strip() for line in open('requirements.txt')]

setup(name='metadata-pg-pipeline',
      version=lib.__version__,
      description='Intermediate tooling for pushing pipeline (or other) outputs to postgres for ad hoc analysis',
      long_description=readme,
      license='MIT',
      keywords='',
      author='Soren Scott',
      author_email='sorenscott@gmail.com',
      maintainer='Soren Scott',
      maintainer_email='sorenscott@gmail.com',
      url='http://github.io/b-cube/metadata-pg-pipeline',
      install_requires=reqs,
      cmdclass={'test': PyTest},
      packages=find_packages(exclude=["local", "tests"])
)
