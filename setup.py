from setuptools import setup, find_packages
import sys, os

version = '0.1.4'

setup(name='maclocate',
      version=version,
      description="Python interface to the SkyHook wireless API",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Ian McCracken',
      author_email='ian.mccracken@gmail.com',
      url='http://maclocate.googlecode.com',
      license='MIT License',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'simplexmlapi',
          'Twisted'
      ],
      entry_points={
          'console_scripts': [
              'maclocate = maclocate:cli'
          ]
      },
      )
