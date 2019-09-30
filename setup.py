
import glob
import os

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

conf = []
templates = []

description = '''An essential toolset that eases WordPress
                 site and server administration'''

for name in glob.glob('config/plugins.d/*.conf'):
    conf.insert(1, name)

for name in glob.glob('wo/cli/templates/*.mustache'):
    templates.insert(1, name)

if not os.path.exists('/var/log/wo/'):
    os.makedirs('/var/log/wo/')

if not os.path.exists('/var/lib/wo/tmp/'):
    os.makedirs('/var/lib/wo/tmp/')

setup(name='wo',
      version='3.9.9.2',
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      keywords='',
      author='WordOps',
      author_email='thomas@virtubox.net',
      url='https://github.com/WordOps/WordOps',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests',
                                      'templates']),
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=[
          # Required to build documentation
          # "Sphinx >= 1.0",
          # Required for testing
          # "nose",
          # "coverage",
          # Required to function
          'cement == 2.8.2',
          'pystache',
          'python-apt',
          'pynginxconfig',
          'PyMySQL',
          'psutil',
          'sh',
          'SQLAlchemy',
          'requests',
          'distro',
          'apt-mirror-updater',
      ],
      data_files=[('/etc/wo', ['config/wo.conf']),
                  ('/etc/wo/plugins.d', conf),
                  ('/usr/lib/wo/templates', templates),
                  ('/etc/bash_completion.d/',
                   ['config/bash_completion.d/wo_auto.rc']),
                  ('/usr/share/man/man8/', ['docs/wo.8'])],
      setup_requires=[],
      entry_points="""
          [console_scripts]
          wo = wo.cli.main:main
      """,
      namespace_packages=[],
      )
