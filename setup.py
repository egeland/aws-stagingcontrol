#!/usr/bin/env python

from setuptools import setup

setup(name='StagingControl',
      version='0.7.2',
      description='Tool to stop and start non-production EC2 instances on a schedule',
      url='https://github.com/egeland/aws-stagingcontrol',
      author='Frode Egeland',
      author_email='egeland@gmail.com',
      license='GPLv3',
      long_description=open('README.md').read(),
      packages=['stagingcontrol'],
      scripts=['run.py'],
      install_requires=[
          'boto >= 2.9.2',
          'argparse >= 1.2.1',
      ],
      zip_safe=False)
